from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request, File, UploadFile, Form
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import json
import io
from cipher import CryptoMethods
from typing import List, Dict

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.sessions: Dict[WebSocket, Dict] = {}

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        self.sessions[websocket] = {}

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        if websocket in self.sessions:
            del self.sessions[websocket]

    def set_session_data(self, websocket: WebSocket, key: str, value):
        if websocket in self.sessions:
            self.sessions[websocket][key] = value

    async def broadcast(self, message: Dict, sender: WebSocket):
        for connection in self.active_connections:
            if connection != sender:
                await connection.send_text(json.dumps(message))

class CryptoServer:
    def __init__(self):
        self.app = FastAPI()
        self.crypto = CryptoMethods()
        self.manager = ConnectionManager()
        self.templates = Jinja2Templates(directory="templates")
        self.setup_routes()
        self.setup_static()

    def setup_static(self):
        self.app.mount("/static", StaticFiles(directory="static"), name="static")

    def setup_routes(self):
        @self.app.get("/")
        async def client_page(request: Request):
            return self.templates.TemplateResponse("client.html", {"request": request})

        @self.app.get("/server")
        async def server_page(request: Request):
            return self.templates.TemplateResponse("server.html", {"request": request})

        @self.app.websocket("/ws")
        async def websocket_endpoint(websocket: WebSocket):
            await self.manager.connect(websocket)
            try:
                await self.handle_websocket_connection(websocket)
            except WebSocketDisconnect:
                self.manager.disconnect(websocket)

        @self.app.get("/decrypt")
        async def decrypt_message(method: str, cipher_text: str, key: str):
            return await self.handle_decryption(method, cipher_text, key)

        @self.app.post("/upload-encrypt")
        async def upload_encrypt(
            file: UploadFile = File(...),
            method: str = Form(...),
            key: str = Form(...)
        ):
            content = await file.read()
            
            # Try to decode as text, assume binary if fails
            try:
                text_content = content.decode('utf-8')
            except UnicodeDecodeError:
                # For binary files, only AES handles bytes input correctly in our implementation
                if method == 'aes':
                    text_content = content
                else:
                    return {"error": "Binary files only supported with AES"}

            # Encrypt
            try:
                encrypted = self.crypto.encrypt(method, text_content, key)
            except Exception as e:
                return {"error": str(e)}
            
            # Convert result to bytes for download
            # AES returns hex string, others return text. 
            # We save the OUTPUT as text file (hex or ciphertext).
            return StreamingResponse(
                io.BytesIO(encrypted.encode('utf-8')),
                media_type="application/octet-stream",
                headers={"Content-Disposition": f"attachment; filename=encrypted_{file.filename}.txt"}
            )

    async def handle_websocket_connection(self, websocket: WebSocket):
        while True:
            data = await websocket.receive_text()
            await self.process_message(json.loads(data), websocket)

    async def process_message(self, data: Dict, websocket: WebSocket):
        msg_type = data.get('type')
        
        if msg_type == 'handshake':
            await self.handle_handshake(data, websocket)
            return

        if data.get('encrypted'):
            data = await self.encrypt_message(data)
        await self.manager.broadcast(data, websocket)

    async def handle_handshake(self, data: Dict, websocket: WebSocket):
        try:
            client_pub_x = int(data.get('public_key_x'))
            client_pub_y = int(data.get('public_key_y'))
            client_pub = (client_pub_x, client_pub_y)
            
            priv_s, pub_s = self.crypto.generate_ecc_keypair()
            secret = self.crypto.compute_ecdh_secret(priv_s, client_pub)
            
            # Store secret (optional context)
            self.manager.set_session_data(websocket, 'shared_secret', secret)
            
            response = {
                'type': 'handshake_response',
                'public_key_x': str(pub_s[0]),
                'public_key_y': str(pub_s[1])
            }
            await websocket.send_text(json.dumps(response))
        except Exception as e:
            print(f"Handshake error: {e}")
            await websocket.send_text(json.dumps({'error': 'Handshake failed'}))

    async def encrypt_message(self, data: Dict) -> Dict:
        encrypted_message = self.crypto.encrypt(
            data['method'],
            data['message'],
            data['key']
        )
        data['encrypted_message'] = encrypted_message
        data['original_message'] = data['message']
        return data

    async def handle_decryption(self, method: str, cipher_text: str, key: str) -> Dict:
        try:
            decrypted_message = self.crypto.decrypt(method, cipher_text, key)
            return {"decrypted_message": decrypted_message}
        except Exception as e:
            return {"error": str(e)}

# Create server instance
server = CryptoServer()
app = server.app