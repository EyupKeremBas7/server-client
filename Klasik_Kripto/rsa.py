def _gcd(a, b):
    """En büyük ortak bölen"""
    while b:
        a, b = b, a % b
    return a


def _mod_tersi(a, m):
    """Modüler ters hesaplama (Extended Euclidean Algorithm)"""
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
    """Miller-Rabin asal testi"""
    if n < 2:
        return False
    if n == 2 or n == 3:
        return True
    if n % 2 == 0:
        return False
    
    # n-1 = 2^r * d
    r, d = 0, n - 1
    while d % 2 == 0:
        r += 1
        d //= 2
    
    # Tanıklık testi
    def tanik_testi(a):
        x = pow(a, d, n)
        if x == 1 or x == n - 1:
            return True
        for _ in range(r - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                return True
        return False
    
    # Küçük asal sayılarla test
    taniklar = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37]
    for a in taniklar:
        if a >= n:
            continue
        if not tanik_testi(a):
            return False
    return True


def _rastgele_asal(bit_uzunlugu, seed=None):
    """Basit rastgele asal sayı üreteci"""
    if seed is None:
        import time
        seed = int(time.time() * 1000000)
    
    # Basit LCG (Linear Congruential Generator)
    a = 1103515245
    c = 12345
    m = 2 ** 31
    
    def rastgele():
        nonlocal seed
        seed = (a * seed + c) % m
        return seed
    
    while True:
        # Rastgele tek sayı üret
        n = 0
        for _ in range(bit_uzunlugu // 16 + 1):
            n = (n << 16) | (rastgele() & 0xFFFF)
        n = n % (2 ** bit_uzunlugu)
        n |= (1 << (bit_uzunlugu - 1))  # En yüksek bit 1 olsun
        n |= 1  # Tek sayı olsun
        
        if _asal_mi(n):
            return n


def rsa_anahtar_uret(bit_uzunlugu=512):
    """
    RSA anahtar çifti üretir
    Returns: (public_key, private_key, n)
             public_key: e (şifreleme üssü)
             private_key: d (deşifreleme üssü)
             n: modül
    """
    import time
    
    # İki asal sayı üret
    p = _rastgele_asal(bit_uzunlugu // 2, int(time.time() * 1000000))
    q = _rastgele_asal(bit_uzunlugu // 2, int(time.time() * 1000000) + 12345)
    
    while p == q:
        q = _rastgele_asal(bit_uzunlugu // 2, int(time.time() * 1000000) + 67890)
    
    n = p * q
    phi = (p - 1) * (q - 1)
    
    # e değerini seç (genellikle 65537)
    e = 65537
    while _gcd(e, phi) != 1:
        e += 2
    
    # d değerini hesapla (e'nin mod phi tersi)
    d = _mod_tersi(e, phi)
    
    return (e, n), (d, n)


def rsa_sifrele(metin, public_key):
    """
    RSA Şifreleme
    public_key: (e, n) tuple
    Returns: Şifrelenmiş sayıların listesi
    """
    e, n = public_key
    
    sifreli = []
    for char in metin:
        m = ord(char)
        c = pow(m, e, n)
        sifreli.append(c)
    
    return sifreli


def rsa_desifre(sifreli_liste, private_key):
    """
    RSA Deşifreleme
    private_key: (d, n) tuple
    sifreli_liste: Şifrelenmiş sayıların listesi
    Returns: Deşifrelenmiş metin
    """
    d, n = private_key
    
    cozulmus_metin = ""
    for c in sifreli_liste:
        m = pow(c, d, n)
        cozulmus_metin += chr(m)
    
    return cozulmus_metin


def rsa_sifrele_metin(metin, public_key):
    """
    RSA Şifreleme - Metin çıktısı
    Şifrelenmiş sayıları virgülle ayrılmış string olarak döndürür
    """
    sifreli = rsa_sifrele(metin, public_key)
    return ','.join(map(str, sifreli))


def rsa_desifre_metin(sifreli_metin, private_key):
    """
    RSA Deşifreleme - Metin girişi
    Virgülle ayrılmış string'den deşifreler
    """
    sifreli_liste = [int(x) for x in sifreli_metin.split(',')]
    return rsa_desifre(sifreli_liste, private_key)
