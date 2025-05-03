import http.server
import socketserver
import webbrowser
import json
import uuid
import os
import hashlib
import threading
import base64
from datetime import datetime
from cryptography.fernet import Fernet

PORT = 8080
DATA_DIR = "form_data"
KEY_FILE = "rg_encryption.key"

# Carrega ou gera a chave de criptografia
if not os.path.exists(KEY_FILE):
    key = Fernet.generate_key()
    with open(KEY_FILE, 'wb') as kf:
        kf.write(key)
else:
    with open(KEY_FILE, 'rb') as kf:
        key = kf.read()
fernet = Fernet(key)

class MyHandler(http.server.SimpleHTTPRequestHandler):
    def do_POST(self):
        # Só processa a rota '/submit'
        if self.path != '/submit':
            return super().do_GET()

        # Lê o corpo da requisição como JSON
        content_length = int(self.headers.get('Content-Length', 0))
        raw_body = self.rfile.read(content_length).decode('utf-8')
        try:
            dados = json.loads(raw_body)
        except json.JSONDecodeError:
            self.send_error(400, "Bad Request: JSON inválido")
            return

        # Hash do CPF
        cpf_original = dados.get('cpf')
        if cpf_original:
            dados['cpf'] = hashlib.sha256(cpf_original.encode('utf-8')).hexdigest()
        else:
            print("Aviso: 'cpf' não enviado.")

        # Extrai imagens em Base64 do JSON
        rg_base64     = dados.pop('rgImagem_base64', None)
        selfie_base64 = dados.pop('selfieImagem_base64', None)

        # Adiciona timestamp de submissão
        dados['submitted_at'] = datetime.utcnow().isoformat() + 'Z'

        # Gera ID único e prepara diretório
        user_id = str(uuid.uuid4())
        os.makedirs(DATA_DIR, exist_ok=True)

        # Criptografa e salva RG como arquivo .enc
        if rg_base64:
            try:
                rg_bytes = base64.b64decode(rg_base64)
                encrypted = fernet.encrypt(rg_bytes)
                enc_filename = f"{user_id}_rg.enc"
                enc_path = os.path.join(DATA_DIR, enc_filename)
                with open(enc_path, 'wb') as ef:
                    ef.write(encrypted)
                dados['rgImagem_encrypted'] = enc_filename
            except Exception as e:
                print(f"Erro ao criptografar/salvar RG: {e}")

        # Salva selfie como PNG (ou também criptografe se desejar)
        if selfie_base64:
            try:
                selfie_bytes = base64.b64decode(selfie_base64)
                selfie_filename = f"{user_id}_selfie.png"
                selfie_path = os.path.join(DATA_DIR, selfie_filename)
                with open(selfie_path, 'wb') as imgf:
                    imgf.write(selfie_bytes)
                dados['selfieImagem_file'] = selfie_filename
            except Exception as e:
                print(f"Erro ao salvar Selfie: {e}")

        # Grava JSON de metadados de forma atômica
        file_path = os.path.join(DATA_DIR, f"{user_id}.json")
        temp_path = file_path + ".tmp"
        try:
            with open(temp_path, 'w', encoding='utf-8') as f:
                json.dump(dados, f, indent=4, ensure_ascii=False)
            os.replace(temp_path, file_path)
        except Exception as e:
            print(f"Erro ao salvar JSON: {e}")
            self.send_error(500, "Internal Server Error: falha ao salvar dados")
            return
        
        try:
            user_id_info = {'last_user_id': user_id}
            with open(os.path.join(DATA_DIR, 'last_user_id.json'), 'w', encoding='utf-8') as f:
                json.dump(user_id_info, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Erro ao salvar last_user_id.json: {e}")

        # Envia resposta de sucesso
        response = {
            'status': 'success',
            'message': 'Dados eviados e criptografados com sucesso!',
            'user_id': user_id
        }
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(response).encode('utf-8'))

        # Desliga o servidor após 4 segundos
        threading.Timer(4.0, self.server.shutdown).start()


def run_server():
    with socketserver.TCPServer(("", PORT), MyHandler) as httpd:
        print(f"Servidor rodando em http://localhost:{PORT}")
        webbrowser.open(f"http://localhost:{PORT}/Form/form.html")
        httpd.serve_forever()

if __name__ == "__main__":
    run_server()