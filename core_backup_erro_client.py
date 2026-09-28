import os

from openai import OpenAI


# ============================================================
# GEMINI — MOTOR PRINCIPAL
# ============================================================

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "").strip()

MODELO_GEMINI = "gemini-3.5-flash-lite"

gemini_client = None

if GEMINI_API_KEY:
    gemini_client = OpenAI(
        api_key=GEMINI_API_KEY,
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
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

    mensagens = [
        {
            "role": "system",
            "content": instrucoes
        }
    ]

    mensagens.extend(historico)

    # --------------------------------------------------------
    # TENTA GEMINI PRIMEIRO
    # --------------------------------------------------------

    if gemini_client is not None:

        try:

            resposta = gemini_client.chat.completions.create(
                model=MODELO_GEMINI,
                messages=mensagens
            )

            texto = resposta.choices[0].message.content

            if texto:
                return texto.strip()

        except Exception as erro_gemini:

            print()
            print("Aviso: Gemini falhou. Usando FreeLLM como reserva.")
            print(f"Detalhe Gemini: {erro_gemini}")
            print()

    # --------------------------------------------------------
    # FALLBACK FREELLM
    # --------------------------------------------------------

    resposta = freellm_client.responses.create(
        model="auto:fast",
        instructions=instrucoes,
        input=historico
    )

    return resposta.output_text.strip()
