def _gcd(a, b):
    while b:
        a, b = b, a % b
    return a


def _mod_tersi(a, m):
    def extended_gcd(a, b):
        if a == 0:
            return b, 0, 1
        gcd, x1, y1 = extended_gcd(b % a, a)
        x = y1 - (b // a) * x1
        y = x1
        return gcd, x, y
    
    gcd, x, _ = extended_gcd(a % m, m)
    if gcd != 1:
        return None
    return (x % m + m) % m


def _asal_mi(n, k=5):
    if n < 2:
        return False
    if n == 2 or n == 3:
        return True
    if n % 2 == 0:
        return False
    
    r, d = 0, n - 1
    while d % 2 == 0:
        r += 1
        d //= 2
    
    def tanik_testi(a):
        x = pow(a, d, n)
        if x == 1 or x == n - 1:
            return True
        for _ in range(r - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                return True
        return False
    
    taniklar = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37]
    for a in taniklar:
        if a >= n:
            continue
        if not tanik_testi(a):
            return False
    return True


def _rastgele_asal(bit_uzunlugu, seed=None):
    if seed is None:
        import time
        seed = int(time.time() * 1000000)
    
    a = 1103515245
    c = 12345
    m = 2 ** 31
    
    def rastgele():
        nonlocal seed
        seed = (a * seed + c) % m
        return seed
    
    while True:
        n = 0
        for _ in range(bit_uzunlugu // 16 + 1):
            n = (n << 16) | (rastgele() & 0xFFFF)
        n = n % (2 ** bit_uzunlugu)
        n |= (1 << (bit_uzunlugu - 1))
        n |= 1
        
        if _asal_mi(n):
            return n


def rsa_anahtar_uret(bit_uzunlugu=512):
    import time
    
    p = _rastgele_asal(bit_uzunlugu // 2, int(time.time() * 1000000))
    q = _rastgele_asal(bit_uzunlugu // 2, int(time.time() * 1000000) + 12345)
    
    while p == q:
        q = _rastgele_asal(bit_uzunlugu // 2, int(time.time() * 1000000) + 67890)
    
    n = p * q
    phi = (p - 1) * (q - 1)
    
    e = 65537
    while _gcd(e, phi) != 1:
        e += 2
    
    d = _mod_tersi(e, phi)
    
    return (e, n), (d, n)


def rsa_sifrele(metin, public_key):
    e, n = public_key
    
    sifreli = []
    for char in metin:
        m = ord(char)
        c = pow(m, e, n)
        sifreli.append(c)
    
    return sifreli


def rsa_desifre(sifreli_liste, private_key):
    d, n = private_key
    
    cozulmus_metin = ""
    for c in sifreli_liste:
        m = pow(c, d, n)
        cozulmus_metin += chr(m)
    
    return cozulmus_metin


def rsa_sifrele_metin(metin, public_key):
    sifreli = rsa_sifrele(metin, public_key)
    return ','.join(map(str, sifreli))


def rsa_desifre_metin(sifreli_metin, private_key):
    sifreli_liste = [int(x) for x in sifreli_metin.split(',')]
    return rsa_desifre(sifreli_liste, private_key)
