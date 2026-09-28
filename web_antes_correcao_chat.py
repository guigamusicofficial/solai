import json
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse

from core import gerar_resposta
from personality import criar_instrucoes


HOST = "127.0.0.1"
PORTA = 8080

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
WEB_DIR = os.path.join(BASE_DIR, "web")

MEMORIA_FILE = os.path.join(BASE_DIR, "memoria.json")
HISTORICO_FILE = os.path.join(BASE_DIR, "historico.json")


# ============================================================
# ARQUIVOS
# ============================================================

def carregar_json(caminho, padrao):

    try:
        if not os.path.exists(caminho):
            return padrao

        with open(caminho, "r", encoding="utf-8") as arquivo:
            dados = json.load(arquivo)

        return dados

    except Exception:
        return padrao


def salvar_json(caminho, dados):

    with open(
        caminho,
        "w",
        encoding="utf-8"
    ) as arquivo:

        json.dump(
            dados,
            arquivo,
            ensure_ascii=False,
            indent=4
        )


def carregar_memoria():

    memoria = carregar_json(
        MEMORIA_FILE,
        {
            "nome": "",
            "preferencias": {},
            "projetos": [],
            "memorias": [],
            "sol": {
                "nome": "Sol Almeida",
                "idade": 28
            },
            "relacionamento": {
                "tipo": "companheira virtual"
            }
        }
    )

    if not isinstance(memoria, dict):
        memoria = {}

    memoria.setdefault("nome", "")
    memoria.setdefault("preferencias", {})
    memoria.setdefault("projetos", [])
    memoria.setdefault("memorias", [])

    return memoria


def carregar_historico():

    historico = carregar_json(
        HISTORICO_FILE,
        []
    )

    if not isinstance(historico, list):
        historico = []

    return historico


def salvar_historico(historico):

    salvar_json(
        HISTORICO_FILE,
        historico
    )


# ============================================================
# MEMÓRIA
# ============================================================

def contexto_memoria(memoria):

    partes = []

    nome = memoria.get("nome", "")

    if nome:
        partes.append(
            f"Nome do usuário: {nome}"
        )

    preferencias = memoria.get(
        "preferencias",
        {}
    )

    if preferencias:

        lista = []

        for chave, valor in preferencias.items():

            if valor:
                lista.append(str(chave))

        if lista:

            partes.append(
                "Preferências: "
                + ", ".join(lista)
            )

    projetos = memoria.get(
        "projetos",
        []
    )

    if projetos:

        partes.append(
            "Projetos: "
            + ", ".join(str(x) for x in projetos)
        )

    memorias = memoria.get(
        "memorias",
        []
    )

    if memorias:

        partes.append(
            "Memórias registradas:\n- "
            + "\n- ".join(
                str(x) for x in memorias
            )
        )

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

        encontrado = re.search(
            padrao,
            texto,
            re.IGNORECASE
        )

        if encontrado:

            nome = encontrado.group(1).strip()

            nome = nome.rstrip(
                ".!?,;"
            )

            if (
                nome
                and len(nome) <= 60
                and len(nome.split()) <= 5
            ):

                memoria["nome"] = nome

                salvar_json(
                    MEMORIA_FILE,
                    memoria
                )

            break


    # --------------------------------------------------------
    # ROCK
    # --------------------------------------------------------

    if (
        "gosto de rock" in texto_lower
        or "adoro rock" in texto_lower
        or "amo rock" in texto_lower
    ):

        memoria.setdefault(
            "preferencias",
            {}
        )

        memoria["preferencias"]["rock"] = True


    # --------------------------------------------------------
    # PROJETO SOL AI
    # --------------------------------------------------------

    if (
        "sol ai" in texto_lower
        and (
            "projeto" in texto_lower
            or "criando" in texto_lower
            or "construindo" in texto_lower
        )
    ):

        memoria.setdefault(
            "projetos",
            []
        )

        if "Sol AI" not in memoria["projetos"]:

            memoria["projetos"].append(
                "Sol AI"
            )


    salvar_json(
        MEMORIA_FILE,
        memoria
    )


# ============================================================
# RESPOSTA
# ============================================================

def processar_chat(mensagem):

    memoria = carregar_memoria()

    historico = carregar_historico()

    atualizar_memoria(
        mensagem,
        memoria
    )

    contexto = contexto_memoria(
        memoria
    )

    instrucoes = criar_instrucoes(
        memoria,
        contexto
    )

    # Mantém somente contexto recente enviado ao modelo.
    historico_contexto = historico[-12:]

    historico_contexto = [
        item
        for item in historico_contexto
        if isinstance(item, dict)
        and item.get("role") in (
            "user",
            "assistant"
        )
    ]

    historico_contexto.append(
        {
            "role": "user",
            "content": mensagem
        }
    )

    resposta = gerar_resposta(
        instrucoes,
        historico_contexto
    )

    # Histórico permanente.
    historico.append(
        {
            "role": "user",
            "content": mensagem
        }
    )

    historico.append(
        {
            "role": "assistant",
            "content": resposta
        }
    )

    # Mantém histórico em tamanho controlado.
    if len(historico) > 100:

        historico = historico[-100:]

    salvar_historico(
        historico
    )

    return resposta


# ============================================================
# HTTP
# ============================================================

class SolHandler(BaseHTTPRequestHandler):

    def enviar_bytes(
        self,
        conteudo,
        content_type,
        status=200
    ):

        if isinstance(
            conteudo,
            str
        ):

            conteudo = conteudo.encode(
                "utf-8"
            )

        self.send_response(status)

        self.send_header(
            "Content-Type",
            content_type
        )

        self.send_header(
            "Content-Length",
            str(len(conteudo))
        )

        self.send_header(
            "Cache-Control",
            "no-cache"
        )

        self.end_headers()

        self.wfile.write(
            conteudo
        )


    def do_GET(self):

        caminho = urlparse(
            self.path
        ).path

        # ----------------------------------------------------
        # PÁGINA PRINCIPAL
        # ----------------------------------------------------

        if caminho == "/":

            caminho = "/web/index.html"


        # ----------------------------------------------------
        # ARQUIVOS DO FRONTEND
        # ----------------------------------------------------

        if caminho.startswith("/web/"):

            relativo = caminho[
                len("/web/"):
            ]

            arquivo = os.path.abspath(
                os.path.join(
                    WEB_DIR,
                    relativo
                )
            )

            # Proteção contra ../
            if not arquivo.startswith(
                os.path.abspath(WEB_DIR)
            ):

                self.enviar_bytes(
                    "Acesso negado.",
                    "text/plain; charset=utf-8",
                    403
                )

                return


            if not os.path.isfile(
                arquivo
            ):

                self.enviar_bytes(
                    "Arquivo não encontrado.",
                    "text/plain; charset=utf-8",
                    404
                )

                return


            extensao = os.path.splitext(
                arquivo
            )[1].lower()


            tipos = {

                ".html":
                    "text/html; charset=utf-8",

                ".css":
                    "text/css; charset=utf-8",

                ".js":
                    "application/javascript; charset=utf-8",

                ".json":
                    "application/json; charset=utf-8",

                ".png":
                    "image/png",

                ".jpg":
                    "image/jpeg",

                ".jpeg":
                    "image/jpeg",

                ".webp":
                    "image/webp",

                ".svg":
                    "image/svg+xml",

                ".ico":
                    "image/x-icon"
            }


            content_type = tipos.get(
                extensao,
                "application/octet-stream"
            )


            try:

                with open(
                    arquivo,
                    "rb"
                ) as f:

                    conteudo = f.read()

                self.enviar_bytes(
                    conteudo,
                    content_type
                )

            except Exception as erro:

                print(
                    f"[WEB] Erro ao servir arquivo: {erro}"
                )

                self.enviar_bytes(
                    "Erro interno.",
                    "text/plain; charset=utf-8",
                    500
                )

            return


        # ----------------------------------------------------
        # STATUS
        # ----------------------------------------------------

        if caminho == "/api/status":

            resposta = {
                "online": True,
                "gemini": bool(
                    os.environ.get(
                        "GEMINI_API_KEY",
                        ""
                    ).strip()
                ),
                "memoria": os.path.exists(
                    MEMORIA_FILE
                )
            }

            self.enviar_bytes(
                json.dumps(
                    resposta,
                    ensure_ascii=False
                ),
                "application/json; charset=utf-8"
            )

            return


        self.enviar_bytes(
            "Not Found",
            "text/plain; charset=utf-8",
            404
        )


    def do_POST(self):

        caminho = urlparse(
            self.path
        ).path

        if caminho != "/api/chat":

            self.enviar_bytes(
                "Not Found",
                "text/plain; charset=utf-8",
                404
            )

            return


        try:

            tamanho = int(
                self.headers.get(
                    "Content-Length",
                    "0"
                )
            )

            corpo = self.rfile.read(
                tamanho
            )

            dados = json.loads(
                corpo.decode(
                    "utf-8"
                )
            )

            mensagem = str(
                dados.get(
                    "mensagem",
                    ""
                )
            ).strip()


            if not mensagem:

                self.enviar_bytes(
                    json.dumps(
                        {
                            "erro":
                                "Mensagem vazia."
                        },
                        ensure_ascii=False
                    ),
                    "application/json; charset=utf-8",
                    400
                )

                return


            resposta = processar_chat(
                mensagem
            )


            self.enviar_bytes(
                json.dumps(
                    {
                        "resposta":
                            resposta
                    },
                    ensure_ascii=False
                ),
                "application/json; charset=utf-8"
            )


        except Exception as erro:

            print()
            print(
                f"[WEB] Erro no chat: {erro}"
            )
            print()

            self.enviar_bytes(
                json.dumps(
                    {
                        "erro":
                            "Erro interno ao processar a mensagem."
                    },
                    ensure_ascii=False
                ),
                "application/json; charset=utf-8",
                500
            )


    def log_message(
        self,
        formato,
        *args
    ):

        # Mantém o terminal limpo.
        pass


# ============================================================
# SERVIDOR
# ============================================================

def iniciar():

    servidor = HTTPServer(
        (
            HOST,
            PORTA
        ),
        SolHandler
    )

    print()
    print("=" * 55)
    print("                    SOL AI WEB")
    print("=" * 55)
    print()
    print(
        "Interface disponível em:"
    )
    print(
        f"http://{HOST}:{PORTA}"
    )
    print()
    print("Gemini = principal")
    print("FreeLLM = fallback")
    print("Memória = ativa")
    print()
    print(
        "Frontend = arquivos separados"
    )
    print(
        "web/index.html"
    )
    print(
        "web/style.css"
    )
    print(
        "web/app.js"
    )
    print()
    print(
        "Pressione CTRL+C para encerrar."
    )
    print()

    try:

        servidor.serve_forever()

    except KeyboardInterrupt:

        print()
        print(
            "SOL AI WEB encerrado."
        )

    finally:

        servidor.server_close()


if __name__ == "__main__":
    iniciar()
