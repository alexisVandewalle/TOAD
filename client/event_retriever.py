from web3 import Web3
import json
import sys, getopt
import sqlite3
from Crypto.PublicKey import ECC

def parse_args():
    opts, args = getopt.getopt(sys.argv[1:], 'c:h:p:')
    port = '8545'
    host = 'http://127.0.0.1'
    contract_address = None

    for opt, value in opts:
        if opt == '-p':
            port = value
        elif opt == '-c':
            contract_address = value
        elif opt == '-h':
            host = 'http://'+host
    if contract_address is None:
        sys.exit('You must provide a contract address')

    return host, port, contract_address

class EncryptedAccount:
    def __init__(self, account):
        if len(account)!=3:
            raise ValueError('size of account must be 3')

        self.e_sk = account[0]
        self.tag = account[1]
        self.nonce = account[2]

class BlockchainClient:
    def __init__(self, contract_address, port='8545', host='http://127.0.0.1'):
        """
        Connect the user to the ethereum blockchain and espacially to
        the TOAD contract.

        Args:
            contract_address : address of CipherETHDKG contract
            port(str) : the port of the host who run a node of the blockchain
            host(str) : the host runnig a node of the bockchain
        """
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

    def get_db(self):
        db = sqlite3.connect('./instance/webapp.db',detect_types=sqlite3.PARSE_DECLTYPES)
        db.row_factory = sqlite3.Row
        return db

    def get_contract_Info(self):
        self.group_size = self.contract.caller().N()
        self.threshold = self.contract.caller().t()
        self.public_account = self.contract.caller().public_account();

        db = self.get_db()
        pk_sql = db.execute(
            'SELECT * FROM eth_public_key WHERE account_address=?',
            [self.public_account,]
        ).fetchone()
        db.close()
        self.public_account_pk = ECC.EccPoint(int(pk_sql['pk_x'],0), int(pk_sql['pk_y'],0))
        print(self.public_account_pk)
        self.encrypted_public_account = []
        for i in range(self.group_size):
            self.encrypted_public_account.append(EncryptedAccount(self.contract.caller().get_encrypted_public_account(i)))


    def decrypt_account(self, encrypted_account):
        pass


host, port, contract_address = parse_args()
client = BlockchainClient(contract_address, port, host)

filter_group_creation = client.contract.events.GroupCreation.createFilter(fromBlock=0)
ev_group_creation = filter_group_creation.get_all_entries()
if(len(ev_group_creation)>=1):
    client.get_contract_Info()
