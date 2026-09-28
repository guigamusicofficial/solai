import json
import os
import re

from config import LIMITE_HISTORICO, MODELO_SOL
from core import client

ARQUIVO_MEMORIA = "memoria.json"
ARQUIVO_HISTORICO = "historico.json"
MAX_MENSAGENS_HISTORICO = LIMITE_HISTORICO

def memoria_padrao():
    return {
        "nome": "",
        "preferencias": {},
        "projetos": [],
        "memorias": [],
        "sol": {"nome": "Sol Almeida", "idade": 28},
        "relacionamento": {"tipo": "companheira virtual"}
    }

def normalizar_memoria(memoria):
    padrao = memoria_padrao()

    if not isinstance(memoria, dict):
        return padrao

    if isinstance(memoria.get("usuario"), dict):
        usuario = memoria["usuario"]

        if not memoria.get("nome"):
            memoria["nome"] = usuario.get("nome", "")

        if not memoria.get("preferencias"):
            memoria["preferencias"] = usuario.get("preferencias", {})

        if not memoria.get("projetos"):
            memoria["projetos"] = usuario.get("projetos", [])

        memoria.pop("usuario", None)

    memoria.setdefault("nome", padrao["nome"])
    memoria.setdefault("preferencias", {})
    memoria.setdefault("projetos", [])
    memoria.setdefault("memorias", [])
    memoria.setdefault("sol", padrao["sol"])
    memoria.setdefault("relacionamento", padrao["relacionamento"])

    if not isinstance(memoria["preferencias"], dict):
        memoria["preferencias"] = {}

    if not isinstance(memoria["projetos"], list):
        memoria["projetos"] = []

    if not isinstance(memoria["memorias"], list):
        memoria["memorias"] = []

    return memoria

def carregar_memoria():
    if not os.path.exists(ARQUIVO_MEMORIA):
        memoria = memoria_padrao()
        salvar_memoria(memoria)
        return memoria

    try:
        with open(ARQUIVO_MEMORIA, "r", encoding="utf-8") as arquivo:
            return normalizar_memoria(json.load(arquivo))
    except Exception:
        return memoria_padrao()

def salvar_memoria(memoria):
    try:
        with open(ARQUIVO_MEMORIA, "w", encoding="utf-8") as arquivo:
            json.dump(memoria, arquivo, ensure_ascii=False, indent=4)
    except Exception as erro:
        print(f"\nAviso ao salvar memória: {erro}\n")

def carregar_historico():
    if not os.path.exists(ARQUIVO_HISTORICO):
        return []

    try:
        with open(ARQUIVO_HISTORICO, "r", encoding="utf-8") as arquivo:
            historico = json.load(arquivo)

        if not isinstance(historico, list):
            return []

        return [
            item for item in historico
            if isinstance(item, dict)
            and item.get("role") in ("user", "assistant")
            and isinstance(item.get("content"), str)
        ][-MAX_MENSAGENS_HISTORICO:]

    except Exception:
        return []

def salvar_historico(historico):
    try:
        with open(ARQUIVO_HISTORICO, "w", encoding="utf-8") as arquivo:
            json.dump(
                historico[-MAX_MENSAGENS_HISTORICO:],
                arquivo,
                ensure_ascii=False,
                indent=4
            )
    except Exception as erro:
        print(f"\nAviso ao salvar histórico: {erro}\n")

def lista_sem_duplicatas(lista):
    resultado = []
    vistos = set()

    for item in lista:
        if not isinstance(item, str):
            continue

        item = item.strip()

        if not item:
            continue

        chave = item.casefold()

        if chave not in vistos:
            vistos.add(chave)
            resultado.append(item)

    return resultado

def corrigir_mojibake(valor):
    if not isinstance(valor, str):
        return valor

    resultado = valor

    for _ in range(2):
        if not any(x in resultado for x in ("Ã", "Â", "â", "ð", "�")):
            break

        try:
            candidato = resultado.encode("latin1").decode("utf-8")
        except (UnicodeEncodeError, UnicodeDecodeError):
            break

        if candidato == resultado:
            break

        resultado = candidato

    return resultado

def corrigir_memoria_mojibake(memoria):
    memoria["nome"] = corrigir_mojibake(memoria.get("nome", ""))

    memoria["preferencias"] = {
        corrigir_mojibake(chave): valor
        for chave, valor in memoria["preferencias"].items()
    }

    memoria["projetos"] = [
        corrigir_mojibake(item)
        for item in memoria["projetos"]
    ]

    memoria["memorias"] = [
        corrigir_mojibake(item)
        for item in memoria["memorias"]
    ]

    return memoria

def organizar_memoria(memoria):
    memoria = normalizar_memoria(memoria)

    novas_preferencias = {}

    for chave, valor in memoria["preferencias"].items():
        chave_limpa = str(chave).strip()

        chave_limpa = re.sub(
            r"^(?:o usuário|usuário|eu|ele)\s+"
            r"gosta(?:\s+muito)?\s+"
            r"(?:de|do|da|dos|das)\s+",
            "",
            chave_limpa,
            flags=re.IGNORECASE
        ).strip()

        if chave_limpa:
            novas_preferencias[chave_limpa] = valor

    memoria["preferencias"] = novas_preferencias
    memoria["projetos"] = lista_sem_duplicatas(memoria["projetos"])
    memoria["memorias"] = lista_sem_duplicatas(memoria["memorias"])

    return memoria

def atualizar_memoria(mensagem, memoria):
    if isinstance(mensagem, dict) and isinstance(memoria, str):
        mensagem, memoria = memoria, mensagem

    if not isinstance(mensagem, str):
        return memoria

    mensagem = mensagem.strip()

    if not mensagem:
        return memoria

    memoria = normalizar_memoria(memoria)

    memoria_atual = json.dumps(memoria, ensure_ascii=False, indent=2)

    prompt = """
Você é o módulo de memória do Sol AI.

Analise SOMENTE a mensagem atual do usuário.

Extraia informações permanentes que possam ser úteis em
conversas futuras.

REGISTRE preferências explícitas.

"Eu gosto de rock." => preferencias: ["rock"]
"Também gosto de fotografia." => preferencias: ["fotografia"]
"Estou aprendendo edição de vídeo." =>
memorias: ["O usuário está aprendendo edição de vídeo."]
"Meu projeto se chama Projeto X." => projetos: ["Projeto X"]

Se o usuário disser explicitamente o próprio nome, não coloque
o nome em preferencias. O programa cuida da identidade.

NÃO registre perguntas, saudações, brincadeiras passageiras,
opiniões momentâneas, informações temporárias, senhas,
tokens, chaves ou dados financeiros.

Não invente.
Não apague.
Não duplique.

Responda SOMENTE com JSON válido:

{
  "preferencias": [],
  "projetos": [],
  "memorias": []
}

MENSAGEM ATUAL:
""" + mensagem + """

MEMÓRIA ATUAL:
""" + memoria_atual

    dados = {
        "preferencias": [],
        "projetos": [],
        "memorias": []
    }

    try:
        resposta = client.responses.create(
            model=MODELO_SOL,
            instructions=(
                "Você é um extrator de memória. "
                "Responda SOMENTE com JSON válido."
            ),
            input=prompt
        )

        texto = corrigir_mojibake(resposta.output_text.strip())
        inicio = texto.find("{")
        fim = texto.rfind("}")

        if inicio >= 0 and fim > inicio:
            extraido = json.loads(texto[inicio:fim + 1])

            if isinstance(extraido, dict):
                for chave in dados:
                    if chave in extraido:
                        dados[chave] = extraido[chave]

    except Exception:
        pass

    preferencias = re.findall(
        r"(?:eu\s+)?gosto(?:\s+muito)?\s+"
        r"(?:de|do|da|dos|das)\s+([^.!?]+)",
        mensagem,
        flags=re.IGNORECASE
    )

    for item in preferencias:
        item = item.strip(" ,;:")
        if item:
            dados["preferencias"].append(item)

    aprendendo = re.findall(
        r"(?:estou|tô|to)\s+aprendendo\s+([^.!?]+)",
        mensagem,
        flags=re.IGNORECASE
    )

    for item in aprendendo:
        item = item.strip(" ,;:")
        if item:
            dados["memorias"].append(
                "O usuário está aprendendo " + item + "."
            )

    novas_preferencias = dados.get("preferencias", [])

    if isinstance(novas_preferencias, dict):
        novas_preferencias = list(novas_preferencias.keys())

    if isinstance(novas_preferencias, list):
        for preferencia in novas_preferencias:
            if not isinstance(preferencia, str):
                continue

            preferencia = preferencia.strip(" ,;:.")

            preferencia = re.sub(
                r"^(?:eu\s+)?gosto(?:\s+muito)?\s+"
                r"(?:de|do|da|dos|das)\s+",
                "",
                preferencia,
                flags=re.IGNORECASE
            ).strip()

            if not preferencia:
                continue

            existente = {
                str(chave).casefold()
                for chave in memoria["preferencias"]
            }

            if preferencia.casefold() not in existente:
                memoria["preferencias"][preferencia] = True

    novos_projetos = dados.get("projetos", [])

    if isinstance(novos_projetos, list):
        for projeto in novos_projetos:
            if not isinstance(projeto, str):
                continue

            projeto = projeto.strip()

            if projeto and not any(
                item.casefold() == projeto.casefold()
                for item in memoria["projetos"]
            ):
                memoria["projetos"].append(projeto)

    novas_memorias = dados.get("memorias", [])

    if isinstance(novas_memorias, list):
        for lembranca in novas_memorias:
            if not isinstance(lembranca, str):
                continue

            lembranca = lembranca.strip()

            if lembranca and not any(
                item.casefold() == lembranca.casefold()
                for item in memoria["memorias"]
            ):
                memoria["memorias"].append(lembranca)

    padroes_nome = [
        r"\bmeu nome é\s+([A-Za-zÀ-ÿ][A-Za-zÀ-ÿ'-]{1,40}?)(?=\s+(?:e|mas|que)\b|[,.!?;:]|$)",
        r"\bpode me chamar de\s+([A-Za-zÀ-ÿ][A-Za-zÀ-ÿ'-]{1,40}?)(?=\s+(?:e|mas|que)\b|[,.!?;:]|$)",
        r"\bquero que me chame de\s+([A-Za-zÀ-ÿ][A-Za-zÀ-ÿ'-]{1,40}?)(?=\s+(?:e|mas|que)\b|[,.!?;:]|$)"
    ]

    for padrao in padroes_nome:
        encontrado = re.search(
            padrao,
            mensagem,
            flags=re.IGNORECASE
        )

        if encontrado:
            nome = encontrado.group(1).strip()

            nome = re.split(
                r"\s+(?:e|mas|que)\s+",
                nome,
                maxsplit=1,
                flags=re.IGNORECASE
            )[0].strip()

            nome = re.sub(r"[.!?,;:]+$", "", nome).strip()

            if nome:
                memoria["nome"] = nome
                break

    memoria = organizar_memoria(memoria)
    salvar_memoria(memoria)

    return memoria

def criar_contexto_memoria(memoria):
    nome = memoria.get("nome", "").strip()
    preferencias = memoria.get("preferencias", {})
    projetos = memoria.get("projetos", [])
    memorias = memoria.get("memorias", [])
    sol = memoria.get("sol", {})
    relacionamento = memoria.get("relacionamento", {})

    return (
        "INFORMAÇÕES DO USUÁRIO:\n\n"
        f"Nome: {nome if nome else 'ainda não informado'}\n\n"
        "Preferências:\n"
        + json.dumps(preferencias, ensure_ascii=False)
        + "\n\nProjetos:\n"
        + json.dumps(projetos, ensure_ascii=False)
        + "\n\nMemórias importantes:\n"
        + json.dumps(memorias, ensure_ascii=False)
        + "\n\nINFORMAÇÕES DA SOL:\n\n"
        f"Nome: {sol.get('nome', 'Sol Almeida')}\n"
        f"Idade da personagem: {sol.get('idade', 28)}\n\n"
        "RELACIONAMENTO:\n\n"
        + str(relacionamento.get("tipo", "companheira virtual"))
    )

def limitar_historico(historico):
    return historico[-MAX_MENSAGENS_HISTORICO:]
