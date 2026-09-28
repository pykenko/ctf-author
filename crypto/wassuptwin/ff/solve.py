from math import isqrt
from Crypto.Util.number import long_to_bytes

def factorize(N):
    p = isqrt(N + 1) - 1
    q = isqrt(N + 1) + 1
    return p, q if p * q == N else None

N = 179539033775512815470521919428301795363
e = 65537
c = 127032915289661010271088911244974251679

p, q = factorize(N)
phi = (p - 1) * (q - 1)
d = pow(e, -1, phi)
r = pow(c, d, N)

L = 23
prefix = b'FF{'
prefix_len = len(prefix)
prefix_int = int.from_bytes(prefix, 'big')
suffix_len = L - prefix_len
power = 2 ** (8 * suffix_len)

a = prefix_int * power - r
k_start = 0 if a <= 0 else (a + N - 1) // N
b = (prefix_int + 1) * power - r - 1
k_end = b // N

m_start = r + k_start * N
m = m_start
for k in range(k_start, k_end + 1):
    try:
        flag_bytes = m.to_bytes(L, 'big')
        if all(32 <= byte <= 126 for byte in flag_bytes) and flag_bytes[-1] == ord('}'):
            print("Found flag:", flag_bytes.decode('utf-8'))
            print(k)
            break
    except OverflowError:
        pass
    m += N
