from Crypto.PublicKey import ECC
from Crypto.Protocol.KDF import HKDF
from Crypto.Cipher import AES
from Crypto.Hash import SHA256

def compute_public_key(private_key):
    private_key_int = int(private_key,0)
    ECC_key = ECC.construct(curve='NIST P-256', d=private_key_int)
    pk_x = ECC_key.pointQ.x
    pk_y = ECC_key.pointQ.y
    return pk_x,pk_y

def encrypt_accounts(private_key, public_keys):
    cipher_account_list = []
    for public_key in public_keys:
        pk_x = public_key[0]
        pk_y = public_key[1]
        key_point = ECC.EccPoint(pk_x, pk_y)*int(private_key,0)
        sym_key = HKDF((str(key_point.x)+str(key_point.y)).encode(),32,b'',SHA256)
        aes = AES.new(sym_key, AES.MODE_CCM)
        nonce = aes.nonce
        enc_private_key = aes.encrypt(private_key.encode())
        tag = aes.digest()
        encryption = [
            enc_private_key,
            tag,
            nonce
        ]
        cipher_account_list.append(encryption)
    return cipher_account_list
