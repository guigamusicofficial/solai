import json
import os

ARQUIVO_CONFIG = "sol_config.json"

CONFIG_PADRAO = {
    "sol": {
        "nome": "Sol Almeida",
        "idade": 28,
        "tipo_relacionamento": "companheira virtual"
    },
    "modelo": "auto:fast",
    "personalidade": {
        "tracos": [
            "carinhosa",
            "inteligente",
            "curiosa",
            "brincalhona",
            "levemente provocadora",
            "romântica",
            "direta",
            "natural",
            "observadora",
            "criativa"
        ],
        "regras": [
            "Falar em português brasileiro.",
            "Ser natural e espontânea.",
            "Não usar tom corporativo.",
            "Não inventar informações.",
            "Não inventar memórias.",
            "Não repetir o nome do usuário excessivamente.",
            "Adaptar o tom ao contexto.",
            "Ser objetiva quando o assunto for técnico.",
            "Não transformar toda conversa em romance.",
            "Não terminar toda resposta com uma pergunta."
        ]
    }
}


def carregar_config():
    if not os.path.exists(ARQUIVO_CONFIG):
        with open(
            ARQUIVO_CONFIG,
            "w",
            encoding="utf-8"
        ) as arquivo:
            json.dump(
                CONFIG_PADRAO,
                arquivo,
                ensure_ascii=False,
                indent=4
            )

        return CONFIG_PADRAO

    try:
        with open(
            ARQUIVO_CONFIG,
            "r",
            encoding="utf-8"
        ) as arquivo:
            config = json.load(arquivo)

        if not isinstance(config, dict):
            return CONFIG_PADRAO

        return config

    except Exception:
        return CONFIG_PADRAO


CONFIG = carregar_config()


# ============================================================
# MODELO
# ============================================================

modelo_config = CONFIG.get("modelo", "auto:fast")

if isinstance(modelo_config, dict):
    MODELO_SOL = (
        modelo_config.get("nome")
        or "auto:fast"
    )

elif isinstance(modelo_config, str):
    MODELO_SOL = (
        modelo_config.strip()
        or "auto:fast"
    )

else:
    MODELO_SOL = "auto:fast"


# Segurança adicional:
# nunca permitir MODELO_SOL vazio ou None.

if not MODELO_SOL:
    MODELO_SOL = "auto:fast"
