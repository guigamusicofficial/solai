import os
from http.server import HTTPServer, BaseHTTPRequestHandler

HOST = "0.0.0.0"
PORT = int(os.environ.get("PORT", 10000))

class SolHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
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
        <p>Servidor a operar com sucesso!</p>
    </div>
</body>
</html>"""
        self.wfile.write(html_content.encode("utf-8"))

def run():
    server = HTTPServer((HOST, PORT), SolHandler)
    print(f"Servidor a escutar em {HOST}:{PORT}")
    server.serve_forever()

if __name__ == "__main__":
    run()
