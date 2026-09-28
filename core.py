import os
import httpx
from openai import OpenAI


# ============================================================
# CONFIGURAÇÃO DO MOTOR (FUSION / NUVEM COM PROXY)
# ============================================================

# Chaves e URLs de configuração vindas do ambiente do Render
API_KEY = os.environ.get("OPENAI_API_KEY", "").strip()
BASE_URL = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1").strip()
PROXY_URL = os.environ.get("PROXY_URL", "").strip()

# Configura o cliente HTTP com ou sem proxy de saída
http_client = None
if PROXY_URL:
    # Se houver um proxy configurado (ex: socks5:// ou http://), o httpx o utiliza
    http_client = httpx.Client(proxy=PROXY_URL)

# Instancia o cliente da OpenAI apontando para o proxy unificado
client = OpenAI(
    api_key=API_KEY,
    base_url=BASE_URL,
    http_client=http_client
)


# ============================================================
# GERAR RESPOSTA USANDO A FUSÃO DE MODELOS
# ============================================================

def gerar_resposta(instrucoes, historico):
    try:
        # Formata o prompt de sistema e o histórico de conversas
        mensagens = [
            {
                "role": "system",
                "content": instrucoes
            },
            *historico
        ]

        # Envia a requisição utilizando o modelo "fusion" do painel
        resposta = client.chat.completions.create(
            model="fusion",
            messages=mensagens,
            temperature=0.7,
            max_tokens=1024
        )

        texto = resposta.choices[0].message.content

        if texto:
            print("[Motor: Painel Fusion (Modelos Múltiplos + Juiz)]")
            return texto.strip()

    except Exception as erro:
        print(f"\n[Erro ao gerar resposta com o Fusion]: {erro}\n")
        return "Tive um problema técnico para processar a resposta com o painel agora."
