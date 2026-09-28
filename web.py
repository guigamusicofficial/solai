import json
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse

from core import gerar_resposta
from personality import criar_instrucoes
from database import (
    salvar_mensagem,
    carregar_historico,
    carregar_memoria_usuario,
    obter_conexao
)


HOST = "0.0.0.0"
PORTA = int(os.environ.get("PORT", 8080))

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
WEB_DIR = os.path.join(BASE_DIR, "web")


# ============================================================
# MEMÓRIA (ADAPTADA PARA SUPABASE)
# ============================================================

def contexto_memoria(memoria):
    partes = []

    nome = memoria.get("nome", "")
    if nome:
        partes.append(f"Nome do usuário: {nome}")

    preferencias = memoria.get("preferencias", {})
    if preferencias:
        lista = [str(chave) for chave, valor in preferencias.items() if valor]
        if lista:
            partes.append("Preferências: " + ", ".join(lista))

    projetos = memoria.get("projetos", [])
    if projetos:
        partes.append("Projetos: " + ", ".join(str(x) for x in projetos))

    memorias = memoria.get("memorias", [])
    if memorias:
        partes.append("Memórias registradas:\n- " + "\n- ".join(str(x) for x in memorias))

    if not partes:
        return "Nenhuma memória permanente registrada."

    return "\n".join(partes)


def atualizar_memoria(mensagem, memoria):
    texto = mensagem.strip()
    texto_lower = texto.lower()

    # --------------------------------------------------------
    # NOME
    # --------------------------------------------------------
    import re
    padroes_nome = [
        r"meu nome é\s+(.+)",
        r"meu nome e\s+(.+)",
        r"eu sou o\s+(.+)",
        r"eu sou a\s+(.+)"
    ]

    for padrao in padroes_nome:
        encontrado = re.search(padrao, texto, re.IGNORECASE)
        if encontrado:
            nome = encontrado.group(1).strip().rstrip(".!?,;")
            if nome and len(nome) <= 60 and len(nome.split()) <= 5:
                memoria["nome"] = nome
                # Atualiza no Supabase
                conexao = obter_conexao()
                if conexao:
                    try:
                        with conexao.cursor() as cursor:
                            cursor.execute(
                                "UPDATE memoria_usuario SET nome = %s WHERE id = (SELECT MAX(id) FROM memoria_usuario);",
                                (nome,)
                            )
                            conexao.commit()
                    except Exception as e:
                        print(f"[Erro ao atualizar nome no Supabase]: {e}")
                    finally:
                        conexao.close()
            break

    # --------------------------------------------------------
    # ROCK
    # --------------------------------------------------------
    if "gosto de rock" in texto_lower or "adoro rock" in texto_lower or "amo rock" in texto_lower:
        prefs = memoria.get("preferencias", {}) or {}
        prefs["rock"] = True
        memoria["preferencias"] = prefs
        conexao = obter_conexao()
        if conexao:
            try:
                with conexao.cursor() as cursor:
                    cursor.execute(
                        "UPDATE memoria_usuario SET preferencias = %s WHERE id = (SELECT MAX(id) FROM memoria_usuario);",
                        (json.dumps(prefs),)
                    )
                    conexao.commit()
            except Exception as e:
                print(f"[Erro ao atualizar preferências no Supabase]: {e}")
            finally:
                conexao.close()

    # --------------------------------------------------------
    # PROJETO SOL AI
    # --------------------------------------------------------
    if "sol ai" in texto_lower and ("projeto" in texto_lower or "criando" in texto_lower or "construindo" in texto_lower):
        projs = memoria.get("projetos", []) or []
        if "Sol AI" not in projs:
            projs.append("Sol AI")
            memoria["projetos"] = projs
            conexao = obter_conexao()
            if conexao:
                try:
                    with conexao.cursor() as cursor:
                        cursor.execute(
                            "UPDATE memoria_usuario SET projetos = %s WHERE id = (SELECT MAX(id) FROM memoria_usuario);",
                            (json.dumps(projs),)
                        )
                        conexao.commit()
                except Exception as e:
                    print(f"[Erro ao atualizar projetos no Supabase]: {e}")
                finally:
                    conexao.close()


# ============================================================
# RESPOSTA
# ============================================================

def processar_chat(mensagem):
    # Carrega memória e histórico do Supabase
    memoria = carregar_memoria_usuario()
    if not memoria:
        memoria = {
            "nome": "",
            "preferencias": {},
            "projetos": [],
            "memorias": [],
            "sol_nome": "Sol Almeida",
            "sol_idade": 28,
            "relacionamento_tipo": "companheira virtual"
        }

    historico = carregar_historico(limite=100)

    atualizar_memoria(mensagem, memoria)

    contexto = contexto_memoria(memoria)
    instrucoes = criar_instrucoes(memoria, contexto)

    # Mantém somente contexto recente enviado ao modelo
    historico_contexto = historico[-12:]
    historico_contexto = [
        item for item in historico_contexto
        if isinstance(item, dict) and item.get("role") in ("user", "assistant")
    ]

    historico_contexto.append({
        "role": "user",
        "content": mensagem
    })

    resposta = gerar_resposta(instrucoes, historico_contexto)

    # Salva nova mensagem do usuário e resposta do assistente no Supabase
    salvar_mensagem("user", mensagem)
    salvar_mensagem("assistant", resposta)

    return resposta


# ============================================================
# HTTP
# ============================================================

class SolHandler(BaseHTTPRequestHandler):

    def enviar_bytes(self, conteudo, content_type, status=200):
        if isinstance(conteudo, str):
            conteudo = conteudo.encode("utf-8")

        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(conteudo)))
        self.send_header("Cache-Control", "no-cache")
        self.end_headers()
        self.wfile.write(conteudo)

    def do_GET(self):
        caminho = urlparse(self.path).path

        if caminho == "/":
            caminho = "/web/index.html"

        if caminho.startswith("/web/"):
            relativo = caminho[len("/web/"):]
            arquivo = os.path.abspath(os.path.join(WEB_DIR, relativo))

            if not arquivo.startswith(os.path.abspath(WEB_DIR)):
                self.enviar_bytes("Acesso negado.", "text/plain; charset=utf-8", 403)
                return

            if not os.path.isfile(arquivo):
                self.enviar_bytes("Arquivo não encontrado.", "text/plain; charset=utf-8", 404)
                return

            extensao = os.path.splitext(arquivo)[1].lower()
            tipos = {
                ".html": "text/html; charset=utf-8",
                ".css": "text/css; charset=utf-8",
                ".js": "application/javascript; charset=utf-8",
                ".json": "application/json; charset=utf-8",
                ".png": "image/png",
                ".jpg": "image/jpeg",
                ".jpeg": "image/jpeg",
                ".webp": "image/webp",
                ".svg": "image/svg+xml",
                ".ico": "image/x-icon"
            }

            content_type = tipos.get(extensao, "application/octet-stream")

            try:
                with open(arquivo, "rb") as f:
                    conteudo = f.read()
                self.enviar_bytes(conteudo, content_type)
            except Exception as erro:
                print(f"[WEB] Erro ao servir arquivo: {erro}")
                self.enviar_bytes("Erro interno.", "text/plain; charset=utf-8", 500)
            return

        if caminho == "/api/status":
            resposta = {
                "online": True,
                "database": bool(os.environ.get("DATABASE_URL", "").strip()),
                "gemini": bool(os.environ.get("OPENAI_API_KEY", "").strip())
            }
            self.enviar_bytes(
                json.dumps(resposta, ensure_ascii=False),
                "application/json; charset=utf-8"
            )
            return

        self.enviar_bytes("Not Found", "text/plain; charset=utf-8", 404)

    def do_POST(self):
        caminho = urlparse(self.path).path

        if caminho != "/api/chat":
            self.enviar_bytes("Not Found", "text/plain; charset=utf-8", 404)
            return

        try:
            tamanho = int(self.headers.get("Content-Length", "0"))
            corpo = self.rfile.read(tamanho)
            dados = json.loads(corpo.decode("utf-8", errors="replace"))

            mensagem = str(
                dados.get("message", dados.get("mensagem", ""))
            ).strip()

            if not mensagem:
                self.enviar_bytes(
                    json.dumps({"erro": "Mensagem vazia."}, ensure_ascii=False),
                    "application/json; charset=utf-8",
                    400
                )
                return

            resposta = processar_chat(mensagem)

            self.enviar_bytes(
                json.dumps({"resposta": resposta}, ensure_ascii=False),
                "application/json; charset=utf-8"
            )

        except Exception as erro:
            print(f"[WEB] Erro no chat: {erro}")
            self.enviar_bytes(
                json.dumps({"erro": "Erro interno ao processar a mensagem."}, ensure_ascii=False),
                "application/json; charset=utf-8",
                500
            )

    def log_message(self, formato, *args):
        pass


# ============================================================
# SERVIDOR
# ============================================================

def iniciar():
    servidor = HTTPServer((HOST, PORTA), SolHandler)

    print()
    print("=" * 55)
    print("            SOL AI WEB (CLOUD / RENDER)")
    print("=" * 55)
    print()
    print(f"Servidor a escutar em {HOST}:{PORTA}")
    print("Banco de dados = Supabase (PostgreSQL)")
    print("Motor = Fusion API")
    print()
    print("Pressione CTRL+C para encerrar.")
    print()

    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        print("\nSOL AI WEB encerrado.")
    finally:
        servidor.server_close()


if __name__ == "__main__":
    iniciar()
