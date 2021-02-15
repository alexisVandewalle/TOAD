from Crypto.PublicKey import ECC

def compute_public_key(private_key):
    private_key_int = int(private_key,0)
    ECC_key = ECC.construct(curve='NIST P-256', d=private_key_int)
    pk_x = ECC_key.pointQ.x
    pk_y = ECC_key.pointQ.y
    return pk_x,pk_y
