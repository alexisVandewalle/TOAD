from functools import wraps

def member_required(method):
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        if not(self.is_member):
            raise ValueError("you have not proved you are a group member")
        return method(self, *args, **kwargs)
    return wrapper
