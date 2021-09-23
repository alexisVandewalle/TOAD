import os

from flask import current_app
from web3 import Web3
import json
import webapp.crypto_utils as cru
from webapp.db import get_db
import ipfsApi
from webapp.decorators import gas_cost

from py_ecc.optimized_bn128 import multiply


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
        else:
            print('connection to the node succeeded')

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

    def get_public_keys(self, selected_accounts):
        db = get_db()
        placeholders = ', '.join('?' for account in selected_accounts)
        public_keys = db.execute(
            "SELECT * from eth_public_key WHERE account_address IN (%s)"%placeholders,
            selected_accounts
        ).fetchall()
        return [(int(row['pk_x'],0), int(row['pk_y'],0)) for row in public_keys]

    def group_creation(self, selected_accounts):
        threshold = len(selected_accounts)//2
        public_keys = self.get_public_keys(selected_accounts)
        encrypted_account = cru.encrypt_accounts(self.private_key, public_keys)
        transaction = self.contract.functions.groupCreation(
            encrypted_account, threshold
            ).buildTransaction(
            {
                'chainId':1337,
                'gas':2000000,
                'nonce': self.w3.eth.getTransactionCount(self.account)
            }
        )
        signed_tx = self.w3.eth.account.signTransaction(transaction, self.private_key)
        txn_hash = self.w3.eth.sendRawTransaction(signed_tx.rawTransaction)
        return txn_hash

    def send_file(self, file_to_encrypt):
        """
        Encrypt a file with a random symetric key and put it on ipfs. Then encrypt
        the symetric key with ElGamal cryptosystem and put it on the blockchain
        Warning:
            Call send_msg function on CipherETHDKG, and so create a transaction and send it.
        Args:
            file_to_encrypt (bytes): the file to encrypt
        """
        # ciphering the file
        db = get_db()
        mpk_sql = db.execute("SELECT * FROM mpk").fetchone()
        mpk = cru.point_from_eth((int(mpk_sql['x']), int(mpk_sql['y'])))
        db.close()
        cipher = cru.Cipher(mpk)
        ct = cipher.encrypt(file_to_encrypt)

        # put cipher file in ipfs
        ipfs_api = ipfsApi.Client('192.168.33.107',5001)
        with open(os.path.join(current_app.config['UPLOAD_FOLDER'],'temp_file'), 'wb') as f:
            f.write(ct['cipher_file'])
        res = ipfs_api.add(os.path.join(current_app.config['UPLOAD_FOLDER'],'temp_file'))[0]
        os.remove(os.path.join(current_app.config['UPLOAD_FOLDER'],'temp_file'))

        # send the encryption of symmetric key used in AES to the blockchain
        transaction = self.contract.functions.send_msg(
            res['Hash'].encode(),
            cru.point_to_eth(ct['c1']),
            cru.point_to_eth(ct['c2'])
            ).buildTransaction(
            {
                'chainId':1337,
                'gas':200000,
                'nonce': self.w3.eth.getTransactionCount(self.account)
            }
        )
        signed_tx = self.w3.eth.account.signTransaction(transaction, self.private_key)
        txn_hash = self.w3.eth.sendRawTransaction(signed_tx.rawTransaction)
        return txn_hash

    def send_share(self, file_info):
        """
        Send a share for a specific message along with its proof of correctness.
        Warning:
            Call the function share on CipherETHDKG, and so send a transaction.
        Args:
            row (dict): a row of the database containing the message
            message_id (int): the id of the message
        """
        db = get_db()
        gsk_sql = db.execute("SELECT * FROM gsk WHERE user_pk=? AND round=?", (self.private_key, file_info['round'])).fetchone()
        gsk = int(gsk_sql['gsk'])
        gpk = multiply(cru.H1, gsk)
        ui = int(gsk_sql['ui'])
        db.close()

        c1 = (int(file_info['c1x']), int(file_info['c1y']))
        c1 = cru.point_from_eth(c1)
        share_for_decryption = multiply(c1, gsk)
        proof = cru.dleq(c1, share_for_decryption, cru.H1, gpk, gsk)
        transaction = self.contract.functions.share_for_dec(
            ui,
            file_info['round'],
            cru.point_to_eth(share_for_decryption),
            proof
        ).buildTransaction(
            {
                'chainId': 1337,
                'gas': 200000,
                'nonce': self.w3.eth.getTransactionCount(self.account)
            }
        )
        signed_tx = self.w3.eth.account.signTransaction(transaction, self.private_key)
        txn_hash = self.w3.eth.sendRawTransaction(signed_tx.rawTransaction)
        return txn_hash

    def select_t_valid_share(self, round):
        """
        Select a set of threshold+1 valid shares for a given message.
        The returned dictionnary has the following shape:

        .. code-block:: python

            {id_user1: share1, id_user2: share2}

        Args:
            file_id (int): the id of the message for which we want to select the shares.

        Returns:
            dict: set of :math:`threshold+1` valid shares.
        """
        db = get_db()
        db_shares = db.execute("SELECT * FROM share WHERE round=?", (round,)).fetchall()
        threshold = self.contract.caller().t()
        if len(db_shares) < threshold + 1:
            raise ValueError('Not enough shares available')

        shares={}
        for i in range(threshold+1):
            point = (int(db_shares[i]['a']),int(db_shares[i]['b']))
            shares[int(db_shares[i]['ui'])] = cru.point_from_eth(point)

        return shares

    def decrypt_file(self, round):
        """
        Decrypt a given message if there are at least threshold+1 shares available.
        Args:
            file_id (int): the id of the message

        Returns:
            (bytes) the decrypted message
        """
        shares = self.select_t_valid_share(round)
        c1_power_s = cru.point_from_eth(cru.point_to_eth(cru.Cipher.recover_c1(shares)))

        db = get_db()
        file_info = db.execute('SELECT * FROM encrypted_file WHERE round=?', (round,)).fetchone()

        c2 = (int(file_info['c2x']), int(file_info['c2y']))
        c2 = cru.point_from_eth(c2)

        cid_ipfs = str(file_info['hash'])[2:-1]

        ipfs_api = ipfsApi.Client('192.168.33.107', 8081)
        ipfs_api.get(cid_ipfs)
        with open(cid_ipfs, 'rb') as f:
            cipher_file = f.read()
        os.remove(cid_ipfs)

        encrypt_file = {
            'cipher_file': cipher_file,
            'c1': c1_power_s,
            'c2': c2
        }
        return cru.Cipher.decrypt(encrypt_file)
