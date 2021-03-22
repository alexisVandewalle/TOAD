from functools import wraps
import web3
import time

def gas_cost(method):
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        txn_hash = method(self, *args, **kwargs)
        gas_used = self.w3.eth.getTransactionReceipt(txn_hash)['gasUsed']
        function_name = method.__name__
        with open("./gas_cost/gas_cost.csv", "a") as f:
            f.write(function_name+","
                +str(gas_used)+","
                +self.private_key[0:6]+","
                +str(time.time())+"\n")

    return wrapper
