from Crypto.PublicKey import ECC
import sqlite3
from Crypto.Protocol.KDF import HKDF
from Crypto.Cipher import AES
from Crypto.Hash import SHA256

# saving a public key in the database
db = sqlite3.connect('../instance/webapp.db', detect_types=sqlite3.PARSE_DECLTYPES)
db.row_factory = sqlite3.Row

private_key = '0x6c840373e6da50ef9fabb1d69c46066fb9b194cf34ca8c87110f9602c749f490'
account_address = '0xbc9e67e40661Cb5a076cE4BaF82b4bb46E0d0F8D'

# computing of G^private_key
private_key_int = int(private_key,0)
ECC_key = ECC.construct(curve='NIST P-256', d=private_key_int)

# saving public key in db
pk_x = ECC_key.pointQ.x
pk_y = ECC_key.pointQ.y
db.execute(
    "INSERT INTO eth_public_key (account_address, pk_x, pk_y) VALUES (?,?,?)",
    [account_address, hex(pk_x), hex(pk_y)]
)

# retrieving of a list of public keys
address = [account_address, ]
placeholders = ', '.join('?' for account in address)
public_keys = db.execute(
    "SELECT * from eth_public_key WHERE account_address IN (%s)"%placeholders,
    address
).fetchall()

# ciphering of public account
public_account_private_key = '0x0d1f7c294e32490c48eaf6e9bbcc24380227334624bfad2f79736116a5408103'
cipher_account_list = []
for row in public_keys:
    pk_x = int(row['pk_x'],0)
    pk_y = int(row['pk_y'],0)
    key_point = ECC.EccPoint(pk_x, pk_y)*int(public_account_private_key,0)
    sym_key = HKDF((str(key_point.x)+str(key_point.y)).encode(),32,b'',SHA256)
    aes = AES.new(sym_key, AES.MODE_CCM)
    nonce = aes.nonce
    enc_private_key = aes.encrypt(public_account_private_key.encode())
    tag = aes.digest()
    encryption = {
        'private_key':enc_private_key,
        'tag':tag,
        'nonce':nonce
    }
    cipher_account_list.append(encryption)
