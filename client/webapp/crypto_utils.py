import secrets

import sympy
from Crypto.PublicKey import ECC
from Crypto.Protocol.KDF import HKDF
from Crypto.Cipher import AES
from Crypto.Hash import SHA256
from py_ecc.optimized_bn128 import add, multiply, neg, normalize
from py_ecc.optimized_bn128 import curve_order as CURVE_ORDER
from py_ecc.optimized_bn128 import Z1
from py_ecc.fields import optimized_bn128_FQ as FQ

H1 = (
    FQ(9727523064272218541460723335320998459488975639302513747055235660443850046724),
    FQ(5031696974169251245229961296941447383441169981934237515842977230762345915487),
    FQ(1),
)


def point_to_eth(p):
    """
    Transform a point of py-ecc in G1 to a tuple
    Args:
        p (Tuple(py_ecc.fields.optimized_bn128_FQ2)): a point in G1

    Returns:
        A tuple of 2 int containing the coefficients of the point
    """
    pn = normalize(p)
    return int(pn[0]), int(pn[1])


def point_from_eth(p):
    """
    Convert a tuple point in G1 to a point in G1 compatible with py-ecc.
    Args:
        p (Tuple(int,int,int,int)): A tuple representing the point in G1

    Returns:
        A point in G1 which is compatible with py-ecc
    """
    x, y = p
    return (FQ(x), FQ(y), FQ(1))

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


class Cipher:
    """
    This class allows to compute the shares and to encrypt and decrypt messages.
    Attributes:
    pk: the public used to encrypt a message
    """

    def __init__(self, pk):
        self.pk = pk

    def __rand_int(self):
        """
        Return a random number between 0 and CURVE_ORDER
        Returns:
            a random int
        """
        return secrets.randbelow(CURVE_ORDER)

    def build_share(self, c1, gsk):
        """
        Compute the share of an encrypted message
        Args:
            c1: a point corresponding to the c1 item returned by the encrypt method
            gsk (int): secret key of the user

        Returns:
            A tuple corresponding to the share
        """
        return normalize(multiply(c1, gsk))

    def recover_c1(shares):
        """
        Compute :math:`c_1^{\\text{gsk}}`, this point is useful for decryption.
        gsk is the secret key of the group, unknown by every member of the group.
        Args:
            shares: a dictionnary containning id an shares ({user_id:share}).

        Returns:
            :math:`c_1^{\\text{gsk}}`
        """
        c1 = Z1
        i = 0
        for id in shares:
            coeff = 1
            for j in shares:
                if j != id:
                    coeff *= j * sympy.mod_inverse((j - id) % CURVE_ORDER, CURVE_ORDER)
                    coeff %= CURVE_ORDER
            c1 = add(c1, multiply(shares[id], coeff))
            i += 1
        return c1

    def encrypt(self, file_to_encrypt):
        """
        Encrypt a given message.
        Args:
            file_to_encrypt (bytes): the file to encrypt.

        Returns:
            A dict such that
            .. code-block:: python
                {'ciphertext':..., 'c1':..., 'c2':... }
        """
        r = self.__rand_int()
        key_point = multiply(H1, r)
        key = HKDF(str(normalize(key_point)).encode(), 32, b'', SHA256)

        # ciphering of the message
        aes = AES.new(key, AES.MODE_CCM)
        nonce = aes.nonce
        ciphertext, tag = aes.encrypt_and_digest(file_to_encrypt)
        result = {'cipher_file': b"".join([nonce, tag, ciphertext])}

        # ciphering of the key
        r = self.__rand_int()
        c1 = multiply(H1, r)
        c2 = add(key_point, multiply(self.pk, r))
        result['c1'] = c1
        result['c2'] = c2
        return result

    def decrypt(ciphertext):
        """
        Decrypt a message.
        Args:
            ciphertext (dict): The message to decrypt of this shape:

                .. code-block:: python
                    {'nonce':(bytestring), 'ciphertext':(bytestring), 'c2': (point),'c1':gsk*c1}

        Returns:
            decrypted message as bytestring
        """
        # reconstruction de la clé
        c1 = ciphertext['c1']
        c2 = ciphertext['c2']

        key_point = add(c2, neg(c1))
        key = HKDF(str(normalize(key_point)).encode(), 32, b'', SHA256)

        nonce = ciphertext['cipher_file'][0:11]
        tag = ciphertext['cipher_file'][11:11 + 16]
        ciphertext = ciphertext['cipher_file'][11 + 16:]
        aes = AES.new(key, AES.MODE_CCM, nonce=nonce)
        return aes.decrypt_and_verify(ciphertext, tag)