from web3 import Web3
import json
import sys, getopt
import sqlite3

from Crypto.PublicKey import ECC
from Crypto.Cipher import AES
from Crypto.Hash import SHA256
from Crypto.Protocol.KDF import HKDF
from Crypto.Random.random import getrandbits, randrange
from py_ecc.optimized_bn128 import curve_order as CURVE_ORDER
from crypto_utils import H1, H2
from py_ecc.optimized_bn128 import add, multiply, neg, normalize, pairing, is_on_curve
from crypto_utils import IntPoly, encrypt_int, decrypt_int, point_to_eth


def get_db():
    db = sqlite3.connect('./instance/webapp.db',detect_types=sqlite3.PARSE_DECLTYPES)
    db.row_factory = sqlite3.Row
    return db

def parse_args():
    opts, args = getopt.getopt(sys.argv[1:], 'c:h:p:s:')
    port = '8545'
    host = 'http://127.0.0.1'
    contract_address = None
    private_key = None

    for opt, value in opts:
        if opt == '-p':
            port = value
        elif opt == '-c':
            contract_address = value
        elif opt == '-h':
            host = 'http://'+host
        elif opt == '-s':
            private_key = value
    if contract_address is None:
        sys.exit('You must provide a contract address')
    if private_key is None:
        sys.exit('You must provide a private_key')

    return host, port, contract_address, private_key

class EncryptedAccount:
    def __init__(self, account):
        if len(account)!=3:
            raise ValueError('size of account must be 3')

        self.e_sk = account[0]
        self.tag = account[1]
        self.nonce = account[2]

class BlockchainClient:
    def __init__(self, contract_address, private_key, port='8545', host='http://127.0.0.1'):
        """
        Connect the user to the ethereum blockchain and espacially to
        the TOAD contract.

        Args:
            contract_address : address of CipherETHDKG contract
            port(str) : the port of the host who run a node of the blockchain
            host(str) : the host runnig a node of the bockchain
        """
        self.private_key = private_key
        self.contract_address = contract_address
        self.host = host
        self.port = port

        self.tp_key_list = []
        self.tp_anon_id = {}
        self.poly_dict = {}
        self.share_dict = {}
        self.gski={}
        self.gpki={}

        self.w3 = Web3(Web3.HTTPProvider(self.host+':'+self.port))
        self.connected = True
        if(self.w3.isConnected() == False):
            self.connected = False
            print('ERREUR: connection to the node failed')
        else:
            print('connection to the node succeeded')

        with open('../build/contracts/TOAD.json','r') as file_abi:
            json_file = file_abi.read()
            abi = json.loads(json_file)['abi']

        self.contract = self.w3.eth.contract(contract_address, abi=abi)

    def get_contract_Info(self):
        self.group_size = self.contract.caller().N()
        self.threshold = self.contract.caller().t()
        self.public_account = self.contract.caller().public_account()
        self.encrypted_public_account = []
        for i in range(self.group_size):
            self.encrypted_public_account.append(EncryptedAccount(self.contract.caller().get_encrypted_public_account(i)))

        db = get_db()
        print(self.public_account)
        pk_sql = db.execute(
            'SELECT * from eth_public_key WHERE account_address=?',
            (self.public_account,)
        ).fetchone()

        pk_x = int(pk_sql['pk_x'],0)
        pk_y = int(pk_sql['pk_y'],0)
        self.key_point = ECC.EccPoint(pk_x, pk_y)*int(self.private_key,0)

        db.close()

    def decrypt_public_account(self,index):
        sym_key = HKDF((str(self.key_point.x)+str(self.key_point.y)).encode(),32,b'',SHA256)
        encrypted_account_eth = self.contract.caller().get_encrypted_public_account(index)

        e_sk = encrypted_account_eth[0]
        tag = encrypted_account_eth[1]
        nonce = encrypted_account_eth[2]
        aes = AES.new(sym_key, AES.MODE_CCM, nonce=nonce)
        try:
             self.public_account_private_key = aes.decrypt_and_verify(e_sk, tag).decode()
             return True
        except ValueError:
            return False

    def generate_si(self):
        self.si = randrange(CURVE_ORDER)
        self.h_si_2 = multiply(H2,self.si)
        self.h_si_1 = multiply(H1,self.si)

    def generate_anonymous_id(self):
        ui = getrandbits(64)
        self.tp_key_list.append((ECC.generate(curve='P-256'),ui))

    def generate_rand_poly(self, round):
        coeffs = [randrange(CURVE_ORDER) for i in range(self.threshold)]
        coeffs = [self.si,]+coeffs
        self.poly_dict[round] = IntPoly(coeffs)

    def publish_tpk(self,round):
        transaction = self.contract.functions.publish_pk(
            [int(coord) for coord in self.tp_key_list[round][0].pointQ.xy],
            self.tp_key_list[round][1],
            round
            ).buildTransaction(
            {
                'chainId':1,
                'gas':1000000,
                'nonce': self.w3.eth.getTransactionCount(self.public_account)
            }
        )
        signed_tx = self.w3.eth.account.signTransaction(transaction, self.public_account_private_key)
        txn_hash = self.w3.eth.sendRawTransaction(signed_tx.rawTransaction)

    def retrieve_tpki_ui(self, round):
        filter_tpk = self.contract.events.PublicKey.createFilter(fromBlock=0, argument_filters={"round":round})
        events = filter_tpk.get_all_entries()
        # TODO changer le 1 en group size
        if len(events) == 1:
            self.tp_anon_id[round] = []
            for event in events:
                uj = event['args']['anonymous_id']
                coord_ecc_point = event['args']['public_key']
                tpkj = ECC.EccPoint(coord_ecc_point[0], coord_ecc_point[1])
                self.tp_anon_id[round].append({'uj':uj,'tpkj':tpkj})

            self.tp_anon_id[round] = sorted(self.tp_anon_id[round], key=lambda k:k['uj'])

    def evaluate_shares(self, round):
        poly = self.poly_dict[round]
        uj_list = [d['uj'] for d in self.tp_anon_id[round]]
        return [self.poly_dict[round].evaluate(uj) for uj in uj_list]

    def encrypt_shares(self, round, shares):
        tski = self.tp_key_list[round][0].d
        tpkj_list = self.tp_anon_id[round]
        n = len(tpkj_list)
        result=[]
        for i in range(n):
            tpkj = tpkj_list[i]['tpkj']
            key_point = tpkj*tski
            result.append(encrypt_int(shares[i], key_point))

        transaction = self.contract.functions.publish_share(
            result,
            round,
            self.tp_key_list[round][1]
            ).buildTransaction(
            {
                'chainId':1,
                'gas':1000000,
                'nonce': self.w3.eth.getTransactionCount(self.public_account)
            }
        )
        signed_tx = self.w3.eth.account.signTransaction(transaction, self.public_account_private_key)
        txn_hash = self.w3.eth.sendRawTransaction(signed_tx.rawTransaction)

    def retrieve_shares(self, round):
        filter_tpk = self.contract.events.Share.createFilter(fromBlock=0, argument_filters={"round":round})
        events = filter_tpk.get_all_entries()
        # TODO changer le 1 en group size
        if len(events) == 1:
            self.share_dict[round]=[]
            for event in events:
                list_share = event['args']['shares'] + [event['args']['anonymous_id'],]
                self.share_dict[round].append(list_share)
            self.share_dict[round].sort(key=lambda k:k[-1])

    def find_rank(self, round):
        #my_ui = self.tp_key_list[round][1]
        my_ui = 14819965287647311834
        tp_id = self.tp_anon_id[round]
        for i in range(len(tp_id)):
            if tp_id[i]['uj'] == my_ui:
                return i

    def decrypt_my_shares(self, round):
        # TODO enlever la zone commentée utilisée pour le test
        #tski = self.tp_key_list[round][0].d
        tski = 101556918311806889347608112229875415018165084929375640946667848539180553894032
        column_id = self.find_rank(round)
        list_shares = self.share_dict[round]
        my_shares = [row[column_id] for row in list_shares]
        fj_ui=[]

        for share in my_shares:
            key_point = self.tp_anon_id[round][column_id]['tpkj']*tski
            fj_ui.append(decrypt_int(share, key_point))

        return fj_ui

    def compute_group_keys(self, round, fj_ui):
        self.gski[round] = sum(fj_ui)
        self.gpki[round] = multiply(H1,self.gski[round])
        print("group secret key:",self.gski)
        print("group public key:",self.gpki)

    def publish_group_key(self,round):
        my_ui = self.tp_key_list[round][1]
        transaction = self.contract.functions.register_group_key(
            point_to_eth(self.gpki[round]),
            self.tp_key_list[round][1],
            round
            ).buildTransaction(
            {
                'chainId':1,
                'gas':1000000,
                'nonce': self.w3.eth.getTransactionCount(self.public_account)
            }
        )
        signed_tx = self.w3.eth.account.signTransaction(transaction, self.public_account_private_key)
        txn_hash = self.w3.eth.sendRawTransaction(signed_tx.rawTransaction)

## main program
if __name__=="__main__":
    host, port, contract_address, private_key = parse_args()
    client = BlockchainClient(contract_address, private_key, port, host)

    filter_group_creation = client.contract.events.GroupCreation.createFilter(fromBlock=0)
    ev_group_creation = filter_group_creation.get_all_entries()

    if(len(ev_group_creation)>=1):
        client.get_contract_Info()
        print("public account:",client.decrypt_public_account(1))
        print("group_size:", client.group_size)
        print("threshold:", client.threshold)
        client.generate_anonymous_id()

        print("my temp key list",client.tp_key_list)

        client.generate_si()
        print("my si:", client.si)

        client.generate_rand_poly(0)
        print("my_poly", client.poly_dict)

        #client.publish_tpk(0)
        client.retrieve_tpki_ui(0)

        shares = client.evaluate_shares(0)
        print("shares for round 0",shares)
        #client.encrypt_shares(0,shares)
        client.retrieve_shares(0)
        fj_ui = client.decrypt_my_shares(0)
        client.compute_group_keys(0,fj_ui)
        client.publish_group_key(0)
