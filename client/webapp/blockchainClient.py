from web3 import Web3
import json

class Client:

    def __init__(self, contract_address, port='8545', host='http://127.0.0.1'):
        """
        Connect the user to the ethereum blockchain and espacially to
        the CipherETHDKG contract.

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

        with open('../build/contracts/TOAD.json','r') as file_abi:
            json_file = file_abi.read()
            abi = json.loads(json_file)['abi']

        self.contract = self.w3.eth.contract(contract_address, abi=abi)

    def login(self,private_key, account_address):
        """
        Register the user account and user private key.

        These information are required to send transactions and so to
        send message, send share and register a group key.

        Args:
            private_key (str): the private key of the user (ex:'d77998d42f85737b2f34ce038780e96391ad93cf345a895cfc50be2541b7f7fb')
            account (str): the account address of the user (ex: '0x00e6e7bCE3a62314450ae79dcfEf27749649362B')
        """
        self.account = account_address
        self.private_key = private_key

    def get_public_info():
        pass

    def group_creation(user_address, threshold):

        pass

    def publish_pk():
        pass

    def publish_share():
        pass

    def register_group_key():
        pass

    def get_group_keys():
        pass

    def send_msg():
        pass

    def share_for_dec():
        pass
