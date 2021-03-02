
from py_ecc.optimized_bn128 import G1, G2, Z2
from py_ecc.optimized_bn128 import add, multiply, neg, normalize, pairing, is_on_curve
from py_ecc.optimized_bn128 import curve_order as CURVE_ORDER
from py_ecc.fields import optimized_bn128_FQ2 as FQ2
from py_ecc.fields import optimized_bn128_FQ as FQ
from Crypto.Cipher import Salsa20
from Crypto.Hash import SHA256
from Crypto.Protocol.KDF import HKDF

H2 = (
    FQ2((
        9110522554455888802745409460679507850660709404525090688071718755658817738702,
        14120302265976430476300156362541817133873389322564306174224598966336605751189
        )),
    FQ2((
        8015061597608194114184122605728732604411275728909990814600934336120589400179,
        21550838471174089343030649382112381550278244756451022825185015902639198926789
        )),
    FQ2.one()
)

H1 = (
    FQ(9727523064272218541460723335320998459488975639302513747055235660443850046724),
    FQ(5031696974169251245229961296941447383441169981934237515842977230762345915487),
    FQ(1),
)

class IntPoly:
    def __init__(self, coeffs):
        self.coeffs = [coeff%CURVE_ORDER for coeff in coeffs]

    def evaluate(self,x):
        return sum([coeff*pow(x,i,CURVE_ORDER) for i, coeff in enumerate(self.coeffs)])%CURVE_ORDER

def encrypt_int(x, key_point):
    sym_key = HKDF((str(key_point.x)+str(key_point.y)).encode(),32,b'',SHA256)
    salsa20 = Salsa20.new(sym_key, bytes(8))
    enc_x = salsa20.encrypt(hex(x).encode())
    return enc_x
