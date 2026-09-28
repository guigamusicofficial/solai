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
# CLIENTE
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
# FREELLM — FALLBACK
# ============================================================

freellm_client = OpenAI(
    base_url="http://127.0.0.1:31415/v1",
    api_key=None
)


# ============================================================
# GERAR RESPOSTA
# ============================================================

def gerar_resposta(instrucoes, historico):

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
                print("[Motor: Gemini]")
                return texto.strip()

        except Exception as erro_gemini:

            print()
            print("[Gemini falhou — usando FreeLLM]")
            print(f"Detalhe: {erro_gemini}")
            print()

    resposta = freellm_client.responses.create(
        model="auto:fast",
        instructions=instrucoes,
        input=historico
    )

    print("[Motor: FreeLLM]")

    return resposta.output_text.strip()
