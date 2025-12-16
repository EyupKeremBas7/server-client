const ws = new WebSocket(`ws://${window.location.host}/ws`);

document.addEventListener('DOMContentLoaded', function () {
    const methodSelect = document.getElementById('sifrele-yontem');
    methodSelect.addEventListener('change', updateKeyHint);
    updateKeyHint(); // Initial update
});

function updateKeyHint() {
    const method = document.getElementById('sifrele-yontem').value;
    const keyInput = document.getElementById('anahtar');
    const keyHint = document.getElementById('anahtar-aciklama');

    switch (method) {
        case 'caesar':
            keyInput.type = 'number';
            keyInput.placeholder = 'Kaydırma sayısını girin (örn: 3)';
            keyHint.textContent = 'Pozitif bir tam sayı girin';
            break;
        case 'vigenere':
            keyInput.type = 'text';
            keyInput.placeholder = 'Anahtar kelimeyi girin';
            keyHint.textContent = 'Sadece harflerden oluşan bir kelime girin';
            break;
        case 'substitution':
            keyInput.type = 'text';
            keyInput.placeholder = '26 harflik permütasyon girin';
            keyHint.textContent = 'Örnek: QWERTYUIOPASDFGHJKLZXCVBNM';
            break;
        case 'affine':
            keyInput.type = 'text';
            keyInput.placeholder = 'a,b şeklinde iki sayı girin';
            keyHint.textContent = 'Örnek: 5,8 (a ve b sayıları virgülle ayrılmış)';
            break;
        case 'hill':
            keyInput.type = 'text';
            keyInput.placeholder = '2x2 veya 3x3 matris değerleri girin';
            keyHint.textContent = 'Örnek: 3,3,2,5 (2x2) veya 6,24,1,13,16,10,20,17,15 (3x3)';
            break;
        case 'rotate':
            keyInput.type = 'number';
            keyInput.placeholder = 'Kaydırma sayısını girin (örn: 13)';
            keyHint.textContent = 'ROT-13 için 13 girin';
            break;
        case 'sha1':
            keyInput.type = 'text';
            keyInput.placeholder = 'Anahtar gerekmez';
            keyInput.disabled = true;
            keyHint.textContent = 'SHA-1 hash fonksiyonu - anahtar gerekmez';
            break;
        case 'sha2':
            keyInput.type = 'text';
            keyInput.placeholder = 'Anahtar gerekmez';
            keyInput.disabled = true;
            keyHint.textContent = 'SHA-256 hash fonksiyonu - anahtar gerekmez';
            break;
        case 'aes':
            keyInput.type = 'text';
            keyInput.placeholder = '16 karakterlik anahtar girin';
            keyHint.textContent = 'AES-128 için tam 16 karakter uzunluğunda anahtar gereklidir';
            break;
        case 'rsa':
            keyInput.type = 'text';
            keyInput.placeholder = 'Public key (e,n) formatında girin';
            keyHint.textContent = 'Örnek: 65537,123456789 - RSA anahtar çifti kullanın';
            break;
    }

    if (method !== 'sha1' && method !== 'sha2') {
        keyInput.disabled = false;
    }
}

function sifreleVeGonder() {
    const mesaj = document.getElementById('mesaj').value;
    const anahtar = document.getElementById('anahtar').value;
    const yontem = document.getElementById('sifrele-yontem').value;

    const hashYontemleri = ['sha1', 'sha2'];

    if (!mesaj) {
        alert('Lütfen mesaj girin!');
        return;
    }

    if (!hashYontemleri.includes(yontem) && !anahtar) {
        alert('Lütfen anahtar girin!');
        return;
    }

    const data = {
        method: yontem,
        key: hashYontemleri.includes(yontem) ? '' : anahtar,
        message: mesaj,
        encrypted: true
    };

    ws.send(JSON.stringify(data));
    document.getElementById('mesaj').value = '';
    document.getElementById('anahtar').value = '';
    alert('Mesaj gönderildi!');
}