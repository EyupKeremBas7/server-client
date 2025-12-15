def hill_sifrele(metin, anahtar_matris):
    """
    Hill Cipher - Şifreleme
    anahtar_matris: 2x2 veya 3x3 matris (liste olarak)
    Örnek: [[3, 3], [2, 5]] veya [[6, 24, 1], [13, 16, 10], [20, 17, 15]]
    """
    # Sadece harfleri al ve büyük harfe çevir
    metin = ''.join([c.upper() for c in metin if c.isalpha()])
    
    n = len(anahtar_matris)  # Matris boyutu
    
    # Metni n'in katına tamamla
    dolgu = (n - len(metin) % n) % n
    metin += 'X' * dolgu
    
    sifreli_metin = ""
    
    # Her n karakterlik bloğu şifrele
    for i in range(0, len(metin), n):
        blok = metin[i:i + n]
        blok_sayilar = [ord(c) - ord('A') for c in blok]
        
        # Matris çarpımı
        sonuc = []
        for satir in range(n):
            toplam = 0
            for sutun in range(n):
                toplam += anahtar_matris[satir][sutun] * blok_sayilar[sutun]
            sonuc.append(toplam % 26)
        
        # Sayıları harfe çevir
        for s in sonuc:
            sifreli_metin += chr(s + ord('A'))
    
    return sifreli_metin


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
        return None  # Modüler ters yok
    return (x % m + m) % m


def _determinant_2x2(matris):
    """2x2 matris determinantı"""
    return matris[0][0] * matris[1][1] - matris[0][1] * matris[1][0]


def _determinant_3x3(matris):
    """3x3 matris determinantı"""
    return (matris[0][0] * (matris[1][1] * matris[2][2] - matris[1][2] * matris[2][1])
            - matris[0][1] * (matris[1][0] * matris[2][2] - matris[1][2] * matris[2][0])
            + matris[0][2] * (matris[1][0] * matris[2][1] - matris[1][1] * matris[2][0]))


def _ters_matris_2x2(matris):
    """2x2 matrisin mod 26 tersi"""
    det = _determinant_2x2(matris) % 26
    det_tersi = _mod_tersi(det, 26)
    
    if det_tersi is None:
        return None
    
    # Adjoint matris
    ters = [
        [(matris[1][1] * det_tersi) % 26, ((-matris[0][1]) * det_tersi) % 26],
        [((-matris[1][0]) * det_tersi) % 26, (matris[0][0] * det_tersi) % 26]
    ]
    
    return ters


def _ters_matris_3x3(matris):
    """3x3 matrisin mod 26 tersi"""
    det = _determinant_3x3(matris) % 26
    det_tersi = _mod_tersi(det, 26)
    
    if det_tersi is None:
        return None
    
    # Kofaktör matrisi hesapla
    kofaktor = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]
    
    for i in range(3):
        for j in range(3):
            # 2x2 minor matris
            minor = []
            for mi in range(3):
                if mi == i:
                    continue
                satir = []
                for mj in range(3):
                    if mj == j:
                        continue
                    satir.append(matris[mi][mj])
                minor.append(satir)
            
            kofaktor[i][j] = ((-1) ** (i + j)) * _determinant_2x2(minor)
    
    # Adjoint (kofaktörün transpozu)
    adjoint = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]
    for i in range(3):
        for j in range(3):
            adjoint[i][j] = kofaktor[j][i]
    
    # Ters matris
    ters = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]
    for i in range(3):
        for j in range(3):
            ters[i][j] = (adjoint[i][j] * det_tersi) % 26
    
    return ters


def hill_desifre(sifreli_metin, anahtar_matris):
    """
    Hill Cipher - Deşifreleme
    """
    n = len(anahtar_matris)
    
    # Ters matrisi hesapla
    if n == 2:
        ters_matris = _ters_matris_2x2(anahtar_matris)
    elif n == 3:
        ters_matris = _ters_matris_3x3(anahtar_matris)
    else:
        return "Sadece 2x2 ve 3x3 matrisler destekleniyor"
    
    if ters_matris is None:
        return "Anahtar matrisin tersi bulunamadı"
    
    # Sadece harfleri al
    sifreli_metin = ''.join([c.upper() for c in sifreli_metin if c.isalpha()])
    
    cozulmus_metin = ""
    
    # Her n karakterlik bloğu deşifrele
    for i in range(0, len(sifreli_metin), n):
        blok = sifreli_metin[i:i + n]
        blok_sayilar = [ord(c) - ord('A') for c in blok]
        
        # Matris çarpımı (ters matris ile)
        sonuc = []
        for satir in range(n):
            toplam = 0
            for sutun in range(n):
                toplam += ters_matris[satir][sutun] * blok_sayilar[sutun]
            sonuc.append(toplam % 26)
        
        # Sayıları harfe çevir
        for s in sonuc:
            cozulmus_metin += chr(s + ord('A'))
    
    return cozulmus_metin
