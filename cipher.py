from Klasik_Kripto.sezar import sifrele as sezar_sifrele, desifrele as sezar_desifrele
from Klasik_Kripto.vigenere import vigenere_sifreleme, vigenere_desifreleme
from Klasik_Kripto.substitution import substitution_sifrele, substitution_desifrele
from Klasik_Kripto.affine import affine_sifrele, affine_desifrele
from Klasik_Kripto.hill import hill_sifrele, hill_desifre
from Klasik_Kripto.rotate import rotate_sifrele, rotate_desifre
from Klasik_Kripto.sha1 import sha1_sifrele
from Klasik_Kripto.sha2 import sha2_sifrele
from Klasik_Kripto.aes import aes_sifrele, aes_desifre
from Klasik_Kripto.rsa import rsa_sifrele_metin, rsa_desifre_metin, rsa_anahtar_uret

class CryptoMethods:
    @staticmethod
    def encrypt(method: str, text: str, key: str) -> str:
        try:
            if method == "caesar":
                return sezar_sifrele(text, int(key))
            elif method == "vigenere":
                return vigenere_sifreleme(text, key)
            elif method == "substitution":
                return substitution_sifrele(text, key)
            elif method == "affine":
                a, b = map(int, key.split(','))
                return affine_sifrele(text, a, b)
            elif method == "hill":
                degerler = list(map(int, key.split(',')))
                if len(degerler) == 4:
                    matris = [[degerler[0], degerler[1]], [degerler[2], degerler[3]]]
                elif len(degerler) == 9:
                    matris = [
                        [degerler[0], degerler[1], degerler[2]],
                        [degerler[3], degerler[4], degerler[5]],
                        [degerler[6], degerler[7], degerler[8]]
                    ]
                else:
                    raise ValueError("Hill anahtarı 4 (2x2) veya 9 (3x3) değer olmalıdır!")
                return hill_sifrele(text, matris)
            elif method == "rotate":
                return rotate_sifrele(text, int(key))
            elif method == "sha1":
                return sha1_sifrele(text)
            elif method == "sha2":
                return sha2_sifrele(text)
            elif method == "aes":
                return aes_sifrele(text, key)
            elif method == "rsa":
                # RSA için key formatı: e,n (public key)
                e, n = map(int, key.split(','))
                public_key = (e, n)
                return rsa_sifrele_metin(text, public_key)
            else:
                raise ValueError(f"Unsupported encryption method: {method}")
        except Exception as e:
            print(f"Encryption error: {str(e)}")
            return text

    @staticmethod
    def decrypt(method: str, text: str, key: str) -> str:
        try:
            if method == "caesar":
                return sezar_desifrele(text, int(key))
            elif method == "vigenere":
                return vigenere_desifreleme(text, key)
            elif method == "substitution":
                if len(key) != 26:
                    raise ValueError("Substitution anahtarı 26 karakterli olmalıdır!")
                return substitution_desifrele(text, key)
            elif method == "affine":
                try:
                    a, b = map(int, key.split(','))
                    return affine_desifrele(text, a, b)
                except ValueError:
                    raise ValueError("Affine anahtarı 'a,b' formatında olmalıdır!")
            elif method == "hill":
                degerler = list(map(int, key.split(',')))
                if len(degerler) == 4:
                    matris = [[degerler[0], degerler[1]], [degerler[2], degerler[3]]]
                elif len(degerler) == 9:
                    matris = [
                        [degerler[0], degerler[1], degerler[2]],
                        [degerler[3], degerler[4], degerler[5]],
                        [degerler[6], degerler[7], degerler[8]]
                    ]
                else:
                    raise ValueError("Hill anahtarı 4 (2x2) veya 9 (3x3) değer olmalıdır!")
                return hill_desifre(text, matris)
            elif method == "rotate":
                return rotate_desifre(text, int(key))
            elif method == "aes":
                return aes_desifre(text, key)
            elif method == "rsa":
                # RSA için key formatı: d,n (private key)
                d, n = map(int, key.split(','))
                private_key = (d, n)
                return rsa_desifre_metin(text, private_key)
            else:
                raise ValueError(f"Desteklenmeyen şifreleme yöntemi: {method}")
        except Exception as e:
            raise ValueError(f"Deşifreleme hatası: {str(e)}")