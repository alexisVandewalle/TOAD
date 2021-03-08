from py_ecc.fields import optimized_bn128_FQ as FQ
from py_ecc.optimized_bn128 import add, multiply, neg, normalize, pairing, is_on_curve
import web3

keccak_256 = web3.Web3.solidityKeccak

H1 = (
    FQ(9727523064272218541460723335320998459488975639302513747055235660443850046724),
    FQ(5031696974169251245229961296941447383441169981934237515842977230762345915487),
    FQ(1),
)

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


def dleq_verify(x1, y1, x2, y2, challenge, response):
    """
    Verify the proof computed with the dleq function in G1
    Args:
        x1: a point in G1
        y1: a point in G1
        x2: a point in G1
        y2: a point in G1
        challenge (int): the first coefficient of the proof
        response (int): the second coefficient of the proof

    Returns:
        True if the proof is correct, False else
    """
    a1 = add(multiply(x1, response), multiply(y1, challenge))
    a2 = add(multiply(x2, response), multiply(y2, challenge))
    c = keccak_256(  # pylint: disable=E1120
        abi_types=["uint256"] * 12,  # 12,
        values=[
            int(v)
            for v in normalize(a1)
                     + normalize(a2)
                     + normalize(x1)
                     + normalize(y1)
                     + normalize(x2)
                     + normalize(y2)
        ],
    )
    c = int.from_bytes(c, "big")
    return c == challenge