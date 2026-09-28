import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from memory import (
    carregar_memoria,
    corrigir_memoria_mojibake,
    organizar_memoria,
    salvar_memoria,
    carregar_historico,
    salvar_historico,
    atualizar_memoria,
    criar_contexto_memoria,
    limitar_historico,
)

from personality import criar_instrucoes
from core import gerar_resposta


HOST = "127.0.0.1"
PORTA = 8080
MAX_HISTORICO_WEB = 12


HTML = r"""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Sol AI</title>

<style>
* {
    box-sizing: border-box;
}

body {
    margin: 0;
    background:
        radial-gradient(circle at top, #24142f 0%, #0b0810 42%, #050507 100%);
    color: #f4f0f6;
    font-family: Arial, Helvetica, sans-serif;
    height: 100vh;
    overflow: hidden;
}

.app {
    width: 100%;
    height: 100vh;
    display: flex;
    flex-direction: column;
}

.header {
    height: 74px;
    display: flex;
    align-items: center;
    padding: 0 28px;
    border-bottom: 1px solid rgba(255,255,255,.08);
    background: rgba(8,6,11,.88);
    backdrop-filter: blur(14px);
}

.logo {
    font-size: 25px;
    font-weight: 700;
    letter-spacing: 4px;
}

.status {
    margin-left: 18px;
    font-size: 12px;
    color: #9dffbd;
}

.status::before {
    content: "";
    display: inline-block;
    width: 8px;
    height: 8px;
    background: #58e88b;
    border-radius: 50%;
    margin-right: 7px;
    box-shadow: 0 0 12px #58e88b;
}

.chat {
    flex: 1;
    overflow-y: auto;
    padding: 30px max(20px, calc((100% - 900px) / 2));
}

.welcome {
    text-align: center;
    margin-top: 15vh;
    opacity: .9;
}

.welcome h1 {
    font-size: 42px;
    margin: 0 0 12px;
    letter-spacing: 3px;
}

.welcome p {
    color: #aaa2b0;
    margin: 0;
}

.message {
    display: flex;
    margin: 16px 0;
}

.message.user {
    justify-content: flex-end;
}

.bubble {
    max-width: 78%;
    padding: 14px 18px;
    border-radius: 18px;
    line-height: 1.5;
    white-space: pre-wrap;
}

.message.sol .bubble {
    background: rgba(255,255,255,.075);
    border: 1px solid rgba(255,255,255,.07);
    border-bottom-left-radius: 5px;
}

.message.user .bubble {
    background: linear-gradient(135deg, #6c2d82, #49205d);
    border-bottom-right-radius: 5px;
}

.typing {
    color: #aaa2b0;
    font-size: 13px;
    padding: 8px 4px;
}

.input-area {
    padding: 18px 20px 22px;
    background: rgba(7,6,9,.92);
    border-top: 1px solid rgba(255,255,255,.08);
}

.input-box {
    max-width: 900px;
    margin: auto;
    display: flex;
    gap: 10px;
}

textarea {
    flex: 1;
    resize: none;
    min-height: 52px;
    max-height: 150px;
    border: 1px solid rgba(255,255,255,.12);
    border-radius: 16px;
    padding: 15px 17px;
    background: rgba(255,255,255,.06);
    color: white;
    outline: none;
    font-size: 15px;
}

textarea:focus {
    border-color: rgba(190,100,230,.65);
}

button {
    width: 58px;
    border: 0;
    border-radius: 16px;
    background: #7b3d91;
    color: white;
    font-size: 21px;
    cursor: pointer;
}

button:hover {
    background: #914bb0;
}

button:disabled {
    opacity: .45;
    cursor: default;
}

@media (max-width: 650px) {
    .header {
        padding: 0 16px;
    }

    .logo {
        font-size: 21px;
    }

    .bubble {
        max-width: 88%;
    }

    .welcome h1 {
        font-size: 32px;
    }
}
</style>
</head>

<body>

<div class="app">

    <header class="header">
        <div class="logo">SOL AI</div>
        <div class="status">online</div>
    </header>

    <main class="chat" id="chat">

        <div class="welcome" id="welcome">
            <h1>Sol</h1>
            <p>Estou aqui. Pode falar.</p>
        </div>

    </main>

    <div class="input-area">
        <div class="input-box">

            <textarea
                id="mensagem"
                placeholder="Digite sua mensagem..."
                rows="1"
            ></textarea>

            <button id="enviar">➤</button>

        </div>
    </div>

</div>

<script>

const chat = document.getElementById("chat");
const mensagem = document.getElementById("mensagem");
const enviar = document.getElementById("enviar");

function adicionarMensagem(tipo, texto) {

    const welcome = document.getElementById("welcome");

    if (welcome) {
        welcome.remove();
    }

    const div = document.createElement("div");

    div.className = "message " + tipo;

    const bubble = document.createElement("div");

    bubble.className = "bubble";

    bubble.textContent = texto;

    div.appendChild(bubble);

    chat.appendChild(div);

    chat.scrollTop = chat.scrollHeight;
}


function mostrarDigitando() {

    const div = document.createElement("div");

    div.id = "digitando";
    div.className = "typing";
    div.textContent = "Sol está digitando...";

    chat.appendChild(div);

    chat.scrollTop = chat.scrollHeight;
}


function removerDigitando() {

    const div = document.getElementById("digitando");

    if (div) {
        div.remove();
    }
}


async function enviarMensagem() {

    const texto = mensagem.value.trim();

    if (!texto) {
        return;
    }

    mensagem.value = "";

    adicionarMensagem("user", texto);

    enviar.disabled = true;

    mostrarDigitando();

    try {

        const resposta = await fetch("/api/chat", {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                mensagem: texto
            })

        });

        const dados = await resposta.json();

        removerDigitando();

        if (!resposta.ok) {
            throw new Error(dados.erro || "Erro desconhecido.");
        }

        adicionarMensagem(
            "sol",
            dados.resposta
        );

    } catch (erro) {

        removerDigitando();

        adicionarMensagem(
            "sol",
            "Tive um problema para responder: " + erro.message
        );

    } finally {

        enviar.disabled = false;

        mensagem.focus();
    }
}


enviar.addEventListener(
    "click",
    enviarMensagem
);


mensagem.addEventListener(
    "keydown",
    function(event) {

        if (
            event.key === "Enter"
            && !event.shiftKey
        ) {

            event.preventDefault();

            enviarMensagem();
        }
    }
);


mensagem.focus();

</script>

</body>
</html>
"""


class SolHandler(BaseHTTPRequestHandler):

    def log_message(self, format, *args):
        return

    def enviar_json(self, status, dados):

        corpo = json.dumps(
            dados,
            ensure_ascii=False
        ).encode("utf-8")

        self.send_response(status)

        self.send_header(
            "Content-Type",
            "application/json; charset=utf-8"
        )

        self.send_header(
            "Content-Length",
            str(len(corpo))
        )

        self.end_headers()

        self.wfile.write(corpo)

    def do_GET(self):

        if self.path == "/":

            corpo = HTML.encode("utf-8")

            self.send_response(200)

            self.send_header(
                "Content-Type",
                "text/html; charset=utf-8"
            )

            self.send_header(
                "Content-Length",
                str(len(corpo))
            )

            self.end_headers()

            self.wfile.write(corpo)

            return

        self.enviar_json(
            404,
            {
                "erro": "Página não encontrada."
            }
        )

    def do_POST(self):

        if self.path != "/api/chat":

            self.enviar_json(
                404,
                {
                    "erro": "Endpoint não encontrado."
                }
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
                corpo.decode("utf-8")
            )

            mensagem = str(
                dados.get(
                    "mensagem",
                    ""
                )
            ).strip()

            if not mensagem:

                self.enviar_json(
                    400,
                    {
                        "erro": "Mensagem vazia."
                    }
                )

                return

            memoria = carregar_memoria()

            memoria = corrigir_memoria_mojibake(
                memoria
            )

            memoria = organizar_memoria(
                memoria
            )

            memoria = atualizar_memoria(
                mensagem,
                memoria
            )

            salvar_memoria(
                memoria
            )

            historico = carregar_historico()

            historico.append(
                {
                    "role": "user",
                    "content": mensagem
                }
            )

            historico = historico[
                -MAX_HISTORICO_WEB:
            ]

            contexto = criar_contexto_memoria(
                memoria
            )

            instrucoes = criar_instrucoes(
                memoria,
                contexto
            )

            contexto_resposta = historico[
                -MAX_HISTORICO_WEB:
            ]

            resposta = gerar_resposta(
                instrucoes,
                contexto_resposta
            )

            historico.append(
                {
                    "role": "assistant",
                    "content": resposta
                }
            )

            historico = limitar_historico(
                historico
            )

            salvar_historico(
                historico
            )

            self.enviar_json(
                200,
                {
                    "resposta": resposta
                }
            )

        except Exception as erro:

            self.enviar_json(
                500,
                {
                    "erro": str(erro)
                }
            )


def iniciar():

    servidor = ThreadingHTTPServer(
        (HOST, PORTA),
        SolHandler
    )

    print("=" * 55)
    print("                    SOL AI WEB")
    print("=" * 55)
    print()
    print(
        f"Interface disponível em:"
    )
    print(
        f"http://127.0.0.1:{PORTA}"
    )
    print()
    print("Gemini = principal")
    print("FreeLLM = fallback")
    print("Memória = ativa")
    print()
    print("Pressione CTRL+C para encerrar.")
    print()

    try:
        servidor.serve_forever()

    except KeyboardInterrupt:
        print()
        print("Sol AI Web encerrada.")

    finally:
        servidor.server_close()


if __name__ == "__main__":
    iniciar()
