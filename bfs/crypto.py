from os import urandom
from struct import pack, unpack

def rotate(v, c):
    return ((v << c) & 0xffffffff) | v >> (32 - c)

def quarter(x, a, b, c, d):
    x[a] = (x[a] + x[b]) & 0xffffffff
    x[d] = rotate(x[d] ^ x[a], 16)
    x[c] = (x[c] + x[d]) & 0xffffffff
    x[b] = rotate(x[b] ^ x[c], 12)
    x[a] = (x[a] + x[b]) & 0xffffffff
    x[d] = rotate(x[d] ^ x[a], 8)
    x[c] = (x[c] + x[d]) & 0xffffffff
    x[b] = rotate(x[b] ^ x[c], 7)

def quarters(x):
    quarter(x, 0, 4, 8, 12)
    quarter(x, 1, 5, 9, 13)
    quarter(x, 2, 6, 10, 14)
    quarter(x, 3, 7, 11, 15)
    quarter(x, 0, 5, 10, 15)
    quarter(x, 1, 6, 11, 12)
    quarter(x, 2, 7, 8, 13)
    quarter(x, 3, 4, 9, 14)
    
def state(key):
    xs = [0] * 16
    xs[:4] = [0x61707865, 0x3320646e, 0x79622d32, 0x6b206574]
    xs[4:12] = unpack('<8L', key)
    return xs

def chacha(key, nonce, rounds=20):
    xs = state(key)
    xs[13:] = unpack('<3L', nonce)
    x = list(xs)
    for _ in range(rounds // 2):
        quarters(x)
    for c in pack('<16L', *((x[i] + xs[i]) & 0xffffffff for i in range(16))):
        yield c

def hchacha(key, nonce, rounds=20):
    xs = state(key)
    xs[12:] = unpack('<4L', nonce)
    x = list(xs)
    for _ in range(rounds // 2):
        quarters(x)
    return pack('<8L', *(x[:4] + x[-4:]))

def xchacha_encrypt(data, key, nonce=None, rounds=20):
    if not isinstance(data, bytes) or not isinstance(key, bytes):
        raise TypeError('not bytes')
    if len(key) < 32:
        raise ValueError('short key')
    if len(key) > 32:
        key = key[:32]
    if not nonce:
        nonce = urandom(24)
    subkey = hchacha(key, nonce[:16], rounds)
    subnonce = b"\0\0\0\0" + nonce[16:]
    return nonce + bytes(a ^ b for a, b in zip(data, chacha(subkey, subnonce, rounds)))

def xchacha_decrypt(data, key, rounds=20):
    if not isinstance(data, bytes) or not isinstance(key, bytes):
        raise TypeError('not bytes')
    if len(data) < 24:
        raise ValueError('no nonce')
    if len(key) < 32:
        raise ValueError('short key')
    if len(key) > 32:
        key = key[:32]
    nonce = data[:24]
    subkey = hchacha(key, nonce[:16], rounds)
    subnonce = b"\0\0\0\0" + nonce[16:]
    return bytes(a ^ b for a, b in zip(data[24:], chacha(subkey, subnonce, rounds)))

def encrypt(data, key, algo='xch'):
    if algo == 'xch':
        return xchacha_encrypt(data, key)
    return None

def decrypt(data, key, algo='xch'):
    if algo == 'xch':
        return xchacha_decrypt(data, key)
    return None