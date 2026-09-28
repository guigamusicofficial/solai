import os
import sys
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.request
import urllib.error

# Configuração do Host e Porta exigidos pelo Render e ambiente local
HOST = "0.0.0.0"
PORT = int(os.environ.get("PORT", 10000))

OPENAI_BASE_URL = os.environ.get("OPENAI_BASE_URL", "https://api.guigamusic.com.br/v1")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")

class SolHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith("/v1/") or self.path == "/v1":
            self.handle_proxy("GET")
        else:
            self.serve_frontend()

    def do_POST(self):
        if self.path.startswith("/v1/") or self.path == "/v1":
            self.handle_proxy("POST")
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"Not Found")

    def handle_proxy(self, method):
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length) if content_length > 0 else None

            target_url = OPENAI_BASE_URL.rstrip('/') + self.path
            
            req_headers = {
                "Content-Type": self.headers.get("Content-Type", "application/json"),
                "Authorization": f"Bearer {OPENAI_API_KEY}" if OPENAI_API_KEY else self.headers.get("Authorization", "")
            }

            req = urllib.request.Request(target_url, data=body, headers=req_headers, method=method)

            with urllib.request.urlopen(req) as response:
                resp_body = response.read()
                self.send_response(response.status)
                for key, value in response.headers.items():
                    if key.lower() not in ['content-encoding', 'transfer-encoding', 'connection']:
                        self.send_header(key, value)
                self.end_headers()
                self.wfile.write(resp_body)

        except urllib.error.HTTPError as e:
            self.send_response(e.code)
            self.end_headers()
            self.wfile.write(e.read())
        except Exception as e:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(str(e).encode('utf-8'))

    def serve_frontend(self):
        # Página HTML padrão de resposta caso o frontend estático não esteja mapeado no diretório
        html_content = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <title>Sol AI - Companheira Virtual</title>
    <style>
        body { font-family: Arial, sans-serif; background: #0f172a; color: #f8fafc; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
        .card { background: #1e293b; padding: 2rem; border-radius: 1rem; box-shadow: 0 4px 6px rgba(0,0,0,0.3); text-align: center; max-width: 400px; width: 100%; }
        h1 { color: #38bdf8; margin-bottom: 0.5rem; }
        p { color: #94a3b8; }
    </style>
</head>
<body>
    <div class="card">
        <h1>Sol AI</h1>
        <p>Servidor a operar com sucesso nos domínios personalizados.</p>
    </div>
</body>
</html>"""
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(html_content.encode("utf-8"))

def run():
    server = HTTPServer((HOST, PORT), SolHandler)
    print(f"Servidor a escutar em {HOST}:{PORT}")
    server.serve_forever()

if __name__ == "__main__":
    run()
