from functools import wraps
import web3

def gas_cost(method):
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        txn_hash = method(self, *args, **kwargs)
        gas_used = self.w3.eth.getTransactionReceipt(txn_hash)['gasUsed']
        function_name = method.__name__
        with open("./gas_cost/gas_cost.csv", "a") as f:
            f.write(function_name+","+str(gas_used)+"\n")

    return wrapper
