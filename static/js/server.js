const ws = new WebSocket(`ws://${window.location.host}/ws`);

ws.onmessage = function (event) {
    const data = JSON.parse(event.data);
    const uniqueId = Date.now();
    const mesajDiv = document.createElement('div');
    mesajDiv.className = 'mesaj';

    const isHash = data.method === 'sha1' || data.method === 'sha2';

    // Get key input details based on method
    const keyDetails = getKeyInputDetails(data.method);

    mesajDiv.innerHTML = `
        <div class="mesaj-header">
            <span class="method-badge">${data.method}</span>
            <span class="timestamp">${new Date().toLocaleTimeString()}</span>
        </div>
        <p><strong>${isHash ? 'Hash Değeri' : 'Şifreli Mesaj'}:</strong> ${data.encrypted_message}</p>
        ${isHash ? '<p class="hash-note"><em>Hash tek yönlüdür, deşifre edilemez.</em></p>' : `
        <div class="decipher-section">
            <input type="${keyDetails.type}" id="key_${uniqueId}" 
                   placeholder="${keyDetails.placeholder}" 
                   class="decipher-input">
            <button class="button" onclick="desifrele('${data.encrypted_message}', '${data.method}', ${uniqueId})">
                <img src="/static/images/lock.webp" alt="Kilit İkonu">
                Deşifre Et
            </button>
        </div>
        <small class="key-hint" style="color: #666; font-size: 0.8em; margin-top: 5px; display: block;">${keyDetails.hint}</small>
        <div id="decrypted_${uniqueId}" class="decrypted-message" style="display: none;"></div>
        `}
    `;

    document.getElementById('mesajlar').prepend(mesajDiv);
};

function getKeyInputDetails(method) {
    switch (method) {
        case 'caesar':
        case 'rotate':
            return {
                type: 'number',
                placeholder: 'Kaydırma sayısı (örn: 3)',
                hint: 'Pozitif bir tam sayı girin'
            };
        case 'vigenere':
            return {
                type: 'text',
                placeholder: 'Anahtar kelime',
                hint: 'Sadece harflerden oluşan bir kelime'
            };
        case 'substitution':
            return {
                type: 'text',
                placeholder: '26 harflik permütasyon',
                hint: 'Örnek: QWERTYUIOPASDFGHJKLZXCVBNM'
            };
        case 'affine':
            return {
                type: 'text',
                placeholder: 'a,b değerleri',
                hint: 'Örnek: 5,8 (virgülle ayrılmış)'
            };
        case 'hill':
            return {
                type: 'text',
                placeholder: 'Matris değerleri',
                hint: 'Örnek: 3,3,2,5 (2x2) veya 6,24,1,13,16,10,20,17,15 (3x3)'
            };
        case 'aes':
            return {
                type: 'text',
                placeholder: '16 karakterlik anahtar',
                hint: 'AES-128 için tam 16 karakter'
            };
        case 'des':
            return {
                type: 'text',
                placeholder: '8 karakterlik anahtar',
                hint: 'DES için tam 8 karakter'
            };
        case 'route':
            return {
                type: 'text',
                placeholder: 'Satır,Sütun (örn: 4,5)',
                hint: 'Matris boyutlarını virgülle ayırarak girin'
            };
        case 'rsa':
            return {
                type: 'text',
                placeholder: 'Private key (d,n)',
                hint: 'Örnek: 2753,3233 (d ve n virgülle ayrılmış)'
            };
        case 'columnar':
            return {
                type: 'text',
                placeholder: 'Anahtar kelime',
                hint: 'Sütunları karıştırmak için kullanılan anahtar kelime'
            };
        default:
            return {
                type: 'text',
                placeholder: 'Deşifreleme anahtarı',
                hint: ''
            };
    }
}

async function desifrele(encryptedMessage, method, uniqueId) {
    try {
        const key = document.getElementById(`key_${uniqueId}`).value;
        if (!key) {
            alert('Lütfen deşifreleme anahtarını girin!');
            return;
        }

        const response = await fetch(`/decrypt?method=${method}&cipher_text=${encryptedMessage}&key=${key}`);
        const result = await response.json();

        if (result.error) {
            alert('Deşifreleme hatası: ' + result.error);
            return;
        }

        const decryptedDiv = document.getElementById(`decrypted_${uniqueId}`);
        decryptedDiv.innerHTML = `
            <p class="success">Deşifreleme Başarılı!</p>
            <p><strong>Deşifrelenmiş Mesaj:</strong> ${result.decrypted_message}</p>
        `;
        decryptedDiv.style.display = 'block';
    } catch (error) {
        console.error('Deşifreleme hatası:', error);
        alert('Deşifreleme sırasında bir hata oluştu!');
    }
}