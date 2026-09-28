from openai import OpenAI
from config import MODELO_SOL

client = OpenAI(
    base_url="http://127.0.0.1:31415/v1",
    api_key=None
)

def gerar_resposta(instrucoes, historico):
    resposta = client.responses.create(
        model=MODELO_SOL,
        instructions=instrucoes,
        input=historico
    )
    return resposta.output_text.strip()
