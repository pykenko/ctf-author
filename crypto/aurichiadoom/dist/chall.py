from secret import FLAG
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from Crypto.PublicKey.RSA import RsaKey
from typing import Type

class auric:
    def __init__(self, bits: int):
        self.key: RsaKey = RSA.generate(bits)
        self.cipher = PKCS1_OAEP.new(self.key)

    def encrypt(self, m: bytes) -> bytes:
        return self.cipher.encrypt(m)

    def decrypt(self, c: bytes) -> bytes:
        return self.cipher.decrypt(c)

def generatecui(flag: bytes, size: int, output: str = 'output.txt') -> None:
    rsa_instance: Type[auric] = auric(size)
    c: bytes = rsa_instance.encrypt(flag)

    n: int = rsa_instance.key.n
    cthex: str = c.hex()
    
    q_str: str = str(rsa_instance.key.q)
    p_str: str = str(rsa_instance.key.p)
    
    qlik: str = q_str[::2]
    plik: str = p_str[1::2]

    with open(output, 'w') as f:
        f.write(f'n = {n}\n')
        f.write(f'ct = {cthex}\n')
        f.write(f'q = {qlik}\n')
        f.write(f'p = {plik}')
    
    print(f"Challenge output written to {output}")

if __name__ == "__main__":
    try:
        from secret import FLAG as current_flag 
    except ImportError:
        print("error coi")

    generatecui(flag=current_flag, size=1024, output='output.txt')