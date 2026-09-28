import os

from openai import OpenAI


# ============================================================
# CONFIGURAÇÃO
# ============================================================

GEMINI_API_KEY = os.environ.get(
    "GEMINI_API_KEY",
    ""
).strip()

MODELO_GEMINI = "gemini-3.5-flash-lite"


# ============================================================
# CLIENTE COMPATÍVEL
# ============================================================

if GEMINI_API_KEY:
    client = OpenAI(
        api_key=GEMINI_API_KEY,
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
    )
else:
    client = OpenAI(
        base_url="http://127.0.0.1:31415/v1",
        api_key=None
    )


# ============================================================
# CLIENTE FREELLM — RESERVA
# ============================================================

freellm_client = OpenAI(
    base_url="http://127.0.0.1:31415/v1",
    api_key=None
)


# ============================================================
# GERAR RESPOSTA
# ============================================================

def gerar_resposta(instrucoes, historico):

    # --------------------------------------------------------
    # GEMINI
    # --------------------------------------------------------

    if GEMINI_API_KEY:

        try:
            resposta = client.chat.completions.create(
                model=MODELO_GEMINI,
                messages=[
                    {
                        "role": "system",
                        "content": instrucoes
                    },
                    *historico
                ]
            )

            texto = resposta.choices[0].message.content

            if texto:
                return texto.strip()

        except Exception as erro_gemini:

            print()
            print("Aviso: Gemini falhou.")
            print("Usando FreeLLM como reserva.")
            print(f"Detalhe: {erro_gemini}")
            print()

    # --------------------------------------------------------
    # FREELLM
    # --------------------------------------------------------

    resposta = freellm_client.responses.create(
        model="auto:fast",
        instructions=instrucoes,
        input=historico
    )

    return resposta.output_text.strip()
