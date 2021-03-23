from functools import wraps
import web3
import time

def member_required(method):
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        if not(self.is_member):
            raise ValueError("you have not proved you are a group member")
        return method(self, *args, **kwargs)
    return wrapper

def gas_cost(method):
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        txn_hash = method(self, *args, **kwargs)
        gas_used = self.w3.eth.getTransactionReceipt(txn_hash)['gasUsed']
        last_block = self.w3.eth.get_block('latest')
        function_name = method.__name__
        with open("../gas_cost/gas_cost.csv", "a") as f:
            f.write(function_name+","
                +str(gas_used)+","
                +self.private_key[0:6]+","
                +str(last_block['number'])+"\n")

    return wrapper
