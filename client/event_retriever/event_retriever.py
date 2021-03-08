from web3 import Web3
import json
import sys, getopt
import sqlite3
import time

from py_ecc.optimized_bn128 import add, multiply, neg, normalize, pairing, is_on_curve
from py_ecc.optimized_bn128 import curve_order as CURVE_ORDER
from py_ecc.optimized_bn128 import Z1

import sympy

from crypto_utils import H1, dleq_verify, point_from_eth


def get_db():
    db = sqlite3.connect('../instance/webapp.db',detect_types=sqlite3.PARSE_DECLTYPES)
    db.row_factory = sqlite3.Row
    return db

def get_c1(round):
    """
    Return the c1 parameter of an encrypted message.
    Args:
        round (int): the round associated to the message.

    Returns:
        the point c1 of the encrypted message
    """
    db = get_db()
    file_info = db.execute("SELECT * FROM encrypted_file WHERE round=?", (round,)).fetchone()
    db.close()
    c1 = point_from_eth(
        (int(file_info['c1x']), int(file_info['c1y'])))
    return c1

def get_group_key(round, ui):
    """
    Return the group key of a given user.
    Args:
        sender (str): the address of the user we want the goup key
    Returns:
        The group key of the given user (a point in G2)
    """
    db = get_db()
    gpk = db.execute("SELECT * FROM gpk WHERE round=? AND ui=?", (round,ui)).fetchone()
    db.close()
    if gpk is not None:
        return point_from_eth((int(gpk['a']), int(gpk['b'])))
    return None

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

class EventRetriever:
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

        self.nb_gpk = 0
        self.has_mpk = False
        self.gpk_0 = []

        self.w3 = Web3(Web3.HTTPProvider(self.host+':'+self.port))
        self.connected = True
        if(self.w3.isConnected() == False):
            self.connected = False
            print('ERREUR: connection to the node failed')
        else:
            print('connection to the node succeeded')

        with open('../../build/contracts/TOAD.json','r') as file_abi:
            json_file = file_abi.read()
            abi = json.loads(json_file)['abi']

        self.contract = self.w3.eth.contract(contract_address, abi=abi)
        self.group_size = self.contract.caller().N()
        self.threshold = self.contract.caller().t()

    def retrieve_gpk(self):
        filter_gpk = self.contract.events.GroupKey.createFilter(fromBlock=0)
        events = filter_gpk.get_all_entries()

        if len(events)>self.nb_gpk:
            db = get_db()
            for event in events:
                round = event['args']['round']
                ui = event['args']['anonymous_id']
                if db.execute("SELECT * FROM gpk WHERE round=? AND ui=?",(round,str(ui))).fetchone() is None:
                    args = event['args']
                    value = (
                        str(args['gpk'][0]),str(args['gpk'][1]), str(args['anonymous_id']), args['round']
                    )
                    db.execute(
                        'INSERT INTO gpk (x, y, ui, round) \
                            VALUES (?,?,?,?)', value
                    )
                    if round == 0:
                        point = point_from_eth(args['gpk'])
                        #TODO a l'initialisation remplir la liste avec les gpk existantes
                        self.gpk_0.append((point, args['anonymous_id']))
            db.commit()
            db.close()

    def compute_mpk(self):
        if len(self.gpk_0) > self.threshold and not self.has_mpk:
            self.has_mpk=True
            self.mpk = Z1

            for gpki,ui in self.gpk_0[0:self.threshold+1]:
                coeff = 1
                for gpkj, uj in self.gpk_0[0:self.threshold+1]:
                    if uj!=ui:
                        coeff *= uj * sympy.mod_inverse((uj - ui) % CURVE_ORDER, CURVE_ORDER)
                        coeff %= CURVE_ORDER
                self.mpk = add(self.mpk,multiply(gpki, coeff))
            self.mpk = normalize(self.mpk)
            print("master public key:",self.mpk)

    def retrieve_new_message(self):
        # TODO test this function
        filter_msg = self.contract.events.NewMessage.createFilter(fromBlock=0)
        events = filter_msg.get_all_entries()

        db = get_db()
        for event in events:
            round = event['args']['round']
            if db.execute("SELECT * FROM encrypted_file WHERE round= ?",(round,)).fetchone() is None:
                args = event['args']
                value = (
                    args['round'], args['file_hash'], str(args['c1'][0]), str(args['c1'][1]),
                    str(args['c2'][0]), str(args['c2'][1]), args['sender']
                )
                db.execute(
                    'INSERT INTO encrypted_file (round, hash, c1x, c1x, c1y, c2x, c2y, sender) \
                        VALUES (?,?,?,?,?,?,?,?)',value
                )

        db.commit()
        db.close()

    def retrieve_share(self):
        # TODO test this function
        filter_share = self.contract.events.ShareForDec.createFilter(fromBlock=0)
        events = filter_share.get_all_entries()

        db = get_db()
        for event in events:
            a = event['args']['share'][0]
            if db.execute("SELECT * FROM share WHERE a=?", (str(a),)).fetchone() is None:
                args = event['args']
                share_point = point_from_eth(args['share'])
                c1 = get_c1(args['round'])

                gpk = get_group_key(args['ui'], args['round'])

                if gpk is not None:
                    proof = args['proof']

                    if dleq_verify(c1, share_point, H1, gpk, proof[0], proof[1]):
                        value = (
                            args['round'], str(args['share'][0]), str(args['share'][1]), str(args['ui'])
                        )
                        db.execute(
                            'INSERT INTO share (round, a, b, ui) \
                                VALUES (?,?,?,?)', value
                        )
        db.commit()
        db.close()

    
if __name__=="__main__":
    host, port, contract_address = parse_args()
    ev_retriever = EventRetriever(contract_address)
    while(True):
        ev_retriever.retrieve_gpk()
        ev_retriever.compute_mpk()
        time.sleep(5)
