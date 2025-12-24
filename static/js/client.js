const ws = new WebSocket(`ws://${window.location.host}/ws`);

let localKeyPair;
let sharedSecret;

ws.onopen = function () {
    console.log("WS Connected, initiating handshake...");
    initiateHandshake();
};

ws.onmessage = async function (event) {
    const data = JSON.parse(event.data);
    if (data.type === 'handshake_response') {
        try {
            const pubX = BigInt(data.public_key_x);
            const pubY = BigInt(data.public_key_y);

            // Construct Raw Key Buffer: 0x04 + X + Y
            const xHex = pubX.toString(16).padStart(64, '0');
            const yHex = pubY.toString(16).padStart(64, '0');
            const rawKeyHex = '04' + xHex + yHex;

            const rawKey = hex2buf(rawKeyHex);

            const serverKey = await window.crypto.subtle.importKey(
                "raw",
                rawKey,
                { name: "ECDH", namedCurve: "P-256" },
                false,
                []
            );

            const bits = await window.crypto.subtle.deriveBits(
                { name: "ECDH", public: serverKey },
                localKeyPair.privateKey,
                256
            );

            // Use SHA-256 of the secret as the Session Key
            const hashBuffer = await window.crypto.subtle.digest('SHA-256', bits);
            const hashArray = Array.from(new Uint8Array(hashBuffer));
            const hashHex = hashArray.map(b => b.toString(16).padStart(2, '0')).join('');

            sharedSecret = hashHex;

            // Auto-fill key input with a portion of the secret
            const method = document.getElementById('sifrele-yontem').value;
            if (method !== 'sha1' && method !== 'sha2') {
                const keyInput = document.getElementById('anahtar');
                // Use first 16 chars for AES/Columnar/etc as a demo default
                keyInput.value = sharedSecret.substring(0, 16);
            }

            console.log("Handshake successful. Shared Secret Established.");
        } catch (error) {
            console.error("Handshake failed:", error);
        }
    }
};

async function initiateHandshake() {
    try {
        localKeyPair = await window.crypto.subtle.generateKey(
            { name: "ECDH", namedCurve: "P-256" },
            true,
            ["deriveKey", "deriveBits"]
        );

        const exported = await window.crypto.subtle.exportKey("raw", localKeyPair.publicKey);
        const keyBytes = new Uint8Array(exported);

        // P-256 Raw format: 0x04 || X (32) || Y (32)
        const x = BigInt('0x' + buf2hex(keyBytes.slice(1, 33)));
        const y = BigInt('0x' + buf2hex(keyBytes.slice(33, 65)));

        ws.send(JSON.stringify({
            type: 'handshake',
            public_key_x: x.toString(),
            public_key_y: y.toString()
        }));
    } catch (e) {
        console.error("Crypto error:", e);
    }
}

function buf2hex(buffer) {
    return [...new Uint8Array(buffer)]
        .map(x => x.toString(16).padStart(2, '0'))
        .join('');
}

function hex2buf(hexString) {
    return new Uint8Array(hexString.match(/.{1,2}/g).map(byte => parseInt(byte, 16)));
}

document.addEventListener('DOMContentLoaded', function () {
    const methodSelect = document.getElementById('sifrele-yontem');
    methodSelect.addEventListener('change', updateKeyHint);
    updateKeyHint();
});

function updateKeyHint() {
    const method = document.getElementById('sifrele-yontem').value;
    const keyInput = document.getElementById('anahtar');
    const keyHint = document.getElementById('anahtar-aciklama');

    keyInput.disabled = false; // Reset disabled state by default
    keyInput.value = ''; // Clear previous value

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
        case 'des':
            keyInput.type = 'text';
            keyInput.placeholder = '8 karakterlik anahtar girin';
            keyHint.textContent = 'DES için tam 8 karakter uzunluğunda anahtar gereklidir';
            break;
        case 'route':
            keyInput.type = 'text';
            keyInput.placeholder = 'Satır,Sütun sayısı (örn: 4,5)';
            keyHint.textContent = 'Matris boyutlarını virgülle ayırarak girin';
            break;
        case 'rsa':
            keyInput.type = 'text';
            keyInput.placeholder = 'Public key (e,n) formatında girin';
            keyHint.textContent = 'Örnek: 65537,123456789 - RSA anahtar çifti kullanın';
            break;
        case 'columnar':
            keyInput.type = 'text';
            keyInput.placeholder = 'Anahtar kelimeyi girin';
            keyHint.textContent = 'Sütunları karıştırmak için bir anahtar kelime girin';
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

async function dosyaSifreleIndir() {
    const fileInput = document.getElementById('dosya-input');
    const file = fileInput.files[0];
    const key = document.getElementById('anahtar').value;
    const method = document.getElementById('sifrele-yontem').value;

    if (!file) {
        alert("Lütfen bir dosya seçin!");
        return;
    }

    if (!key && method !== 'sha1' && method !== 'sha2') {
        alert("Lütfen anahtar girin (veya handshake bekleyin)!");
        return;
    }

    const formData = new FormData();
    formData.append('file', file);
    formData.append('method', method);
    formData.append('key', key);

    try {
        const response = await fetch('/upload-encrypt', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            throw new Error("Upload failed");
        }

        // Trigger download
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `encrypted_${file.name}`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);

    } catch (e) {
        console.error(e);
        alert("Dosya şifreleme hatası!");
    }
}