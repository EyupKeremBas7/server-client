alfabe="abcdefghijklmnopqrstuvwxyz"

def sifrele(metin, key):  
    cipher_text=''
    metin=metin.lower()
    for x in metin:
        if x in alfabe: 
            index=alfabe.find(x)
            index=(index+key)%len(alfabe)
            cipher_text=cipher_text+alfabe[index]
        else:
            cipher_text=cipher_text+x
    return cipher_text

def desifrele(cipher_text, key): 
    metin=''
    for x in cipher_text:
        if x in alfabe: 
            index=alfabe.find(x)
            index=(index-key)%len(alfabe)
            metin=metin+alfabe[index]
        else:
            metin=metin+x
    return metin
