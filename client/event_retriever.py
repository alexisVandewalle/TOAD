from web3 import Web3
import json
import sys, getopt
import sqlite3
from Crypto.PublicKey import ECC
from Crypto.Cipher import AES
from Crypto.Hash import SHA256
from Crypto.Protocol.KDF import HKDF


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

    def decrypt_public_account(self,index):
        sym_key = HKDF((str(self.key_point.x)+str(self.key_point.y)).encode(),32,b'',SHA256)
        encrypted_account_eth = self.contract.caller().get_encrypted_public_account(index)

        e_sk = encrypted_account_eth[0]
        tag = encrypted_account_eth[1]
        nonce = encrypted_account_eth[2]
        aes = AES.new(sym_key, AES.MODE_CCM, nonce=nonce)
        try:
             self.public_account_private_key = str(aes.decrypt_and_verify(e_sk, tag))
             return True
        except ValueError:
            return False


## main program
if __name__=="main":
    host, port, contract_address, private_key = parse_args()
    client = BlockchainClient(contract_address, private_key, port, host)

    filter_group_creation = client.contract.events.GroupCreation.createFilter(fromBlock=0)
    ev_group_creation = filter_group_creation.get_all_entries()
    if(len(ev_group_creation)>=1):
        client.get_contract_Info()
        client.decrypt_public_account(0)