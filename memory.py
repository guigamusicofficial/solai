import json
import os
import re

from config import LIMITE_HISTORICO, MODELO_SOL
from core import client


ARQUIVO_MEMORIA = "memoria.json"
ARQUIVO_HISTORICO = "historico.json"


# ============================================================
# MEMÓRIA
# ============================================================

def memoria_padrao():
    return {
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


def carregar_memoria():
    if not os.path.exists(ARQUIVO_MEMORIA):
        memoria = memoria_padrao()
        salvar_memoria(memoria)
        return memoria

    try:
        with open(
            ARQUIVO_MEMORIA,
            "r",
            encoding="utf-8"
        ) as arquivo:
            memoria = json.load(arquivo)

        if not isinstance(memoria, dict):
            return memoria_padrao()

        return memoria

    except Exception:
        return memoria_padrao()


def salvar_memoria(memoria):
    with open(
        ARQUIVO_MEMORIA,
        "w",
        encoding="utf-8"
    ) as arquivo:
        json.dump(
            memoria,
            arquivo,
            ensure_ascii=False,
            indent=4
        )


# ============================================================
# CORREÇÃO DE MOJIBAKE
# ============================================================

def corrigir_texto_mojibake(texto):
    if not isinstance(texto, str):
        return texto

    if any(
        trecho in texto
        for trecho in (
            "Ã",
            "Â",
            "â€",
            "ðŸ"
        )
    ):
        try:
            corrigido = texto.encode(
                "latin1"
            ).decode(
                "utf-8"
            )

            return corrigido

        except Exception:
            return texto

    return texto


def corrigir_memoria_mojibake(memoria):

    if not isinstance(memoria, dict):
        return memoria

    for chave in (
        "nome",
    ):
        if isinstance(memoria.get(chave), str):
            memoria[chave] = corrigir_texto_mojibake(
                memoria[chave]
            )

    for chave in (
        "projetos",
        "memorias"
    ):
        valores = memoria.get(chave, [])

        if isinstance(valores, list):
            memoria[chave] = [
                corrigir_texto_mojibake(valor)
                if isinstance(valor, str)
                else valor
                for valor in valores
            ]

    preferencias = memoria.get(
        "preferencias",
        {}
    )

    if isinstance(preferencias, dict):

        memoria["preferencias"] = {
            corrigir_texto_mojibake(str(chave)): valor
            for chave, valor in preferencias.items()
        }

    return memoria


# ============================================================
# NORMALIZAÇÃO
# ============================================================

def normalizar_texto(texto):
    if not isinstance(texto, str):
        return ""

    texto = corrigir_texto_mojibake(texto)

    texto = re.sub(
        r"\s+",
        " ",
        texto
    ).strip()

    return texto


def remover_duplicatas_lista(lista):

    if not isinstance(lista, list):
        return []

    resultado = []
    vistos = set()

    for item in lista:

        if not isinstance(item, str):
            continue

        item = normalizar_texto(item)

        if not item:
            continue

        chave = item.casefold()

        if chave in vistos:
            continue

        vistos.add(chave)
        resultado.append(item)

    return resultado


# ============================================================
# ORGANIZAR MEMÓRIA
# ============================================================

def organizar_memoria(memoria):

    if not isinstance(memoria, dict):
        memoria = memoria_padrao()

    base = memoria_padrao()

    # --------------------------------------------------------
    # CAMPOS PRINCIPAIS
    # --------------------------------------------------------

    nome = memoria.get(
        "nome",
        ""
    )

    if isinstance(nome, str):
        base["nome"] = normalizar_texto(nome)

    # --------------------------------------------------------
    # PREFERÊNCIAS
    # --------------------------------------------------------

    preferencias = memoria.get(
        "preferencias",
        {}
    )

    if isinstance(preferencias, dict):

        novas_preferencias = {}

        for chave, valor in preferencias.items():

            chave = normalizar_texto(
                str(chave)
            )

            if chave:
                novas_preferencias[chave] = valor

        base["preferencias"] = novas_preferencias

    # --------------------------------------------------------
    # PROJETOS
    # --------------------------------------------------------

    base["projetos"] = remover_duplicatas_lista(
        memoria.get(
            "projetos",
            []
        )
    )

    # --------------------------------------------------------
    # MEMÓRIAS
    # --------------------------------------------------------

    base["memorias"] = remover_duplicatas_lista(
        memoria.get(
            "memorias",
            []
        )
    )

    # --------------------------------------------------------
    # CONFIGURAÇÃO DA SOL
    # --------------------------------------------------------

    sol = memoria.get(
        "sol",
        {}
    )

    if isinstance(sol, dict):

        base["sol"]["nome"] = sol.get(
            "nome",
            "Sol Almeida"
        )

        base["sol"]["idade"] = sol.get(
            "idade",
            28
        )

    relacionamento = memoria.get(
        "relacionamento",
        {}
    )

    if isinstance(relacionamento, dict):

        base["relacionamento"]["tipo"] = relacionamento.get(
            "tipo",
            "companheira virtual"
        )

    return base


# ============================================================
# ATUALIZAÇÃO INTELIGENTE
# ============================================================

def atualizar_memoria(mensagem, memoria):

    if not isinstance(mensagem, str):
        return memoria

    mensagem = mensagem.strip()

    if not mensagem:
        return memoria

    memoria = organizar_memoria(memoria)

    # --------------------------------------------------------
    # NOME
    # --------------------------------------------------------

    padroes_nome = [
        r"^\s*meu nome é\s+(.+?)[.!?]?\s*$",
        r"^\s*pode me chamar de\s+(.+?)[.!?]?\s*$",
        r"^\s*quero que me chame de\s+(.+?)[.!?]?\s*$"
    ]

    for padrao in padroes_nome:

        resultado = re.search(
            padrao,
            mensagem,
            re.IGNORECASE
        )

        if resultado:

            nome = normalizar_texto(
                resultado.group(1)
            )

            if nome:
                memoria["nome"] = nome

            return memoria

    # --------------------------------------------------------
    # GOSTOS
    # --------------------------------------------------------

    padroes_gosto = [
        r"^\s*eu gosto de\s+(.+?)[.!?]?\s*$",
        r"^\s*gosto muito de\s+(.+?)[.!?]?\s*$",
        r"^\s*eu curto\s+(.+?)[.!?]?\s*$",
        r"^\s*curto muito\s+(.+?)[.!?]?\s*$",
        r"^\s*adoro\s+(.+?)[.!?]?\s*$"
    ]

    for padrao in padroes_gosto:

        resultado = re.search(
            padrao,
            mensagem,
            re.IGNORECASE
        )

        if resultado:

            gosto = normalizar_texto(
                resultado.group(1)
            )

            if gosto:

                chave = gosto.casefold()

                memoria["preferencias"][chave] = True

            return memoria

    # --------------------------------------------------------
    # NÃO GOSTO
    # --------------------------------------------------------

    padroes_nao_gosto = [
        r"^\s*não gosto de\s+(.+?)[.!?]?\s*$",
        r"^\s*odeio\s+(.+?)[.!?]?\s*$"
    ]

    for padrao in padroes_nao_gosto:

        resultado = re.search(
            padrao,
            mensagem,
            re.IGNORECASE
        )

        if resultado:

            item = normalizar_texto(
                resultado.group(1)
            )

            if item:

                chave = item.casefold()

                memoria["preferencias"][chave] = False

            return memoria

    # --------------------------------------------------------
    # PROJETOS
    # --------------------------------------------------------

    padroes_projeto = [
        r"^\s*meu projeto é\s+(.+?)[.!?]?\s*$",
        r"^\s*meu projeto\s+(.+?)[.!?]?\s*$",
        r"^\s*estou construindo\s+(.+?)[.!?]?\s*$"
    ]

    for padrao in padroes_projeto:

        resultado = re.search(
            padrao,
            mensagem,
            re.IGNORECASE
        )

        if resultado:

            projeto = normalizar_texto(
                resultado.group(1)
            )

            if projeto:

                memoria["projetos"].append(
                    projeto
                )

                memoria["projetos"] = remover_duplicatas_lista(
                    memoria["projetos"]
                )

            return memoria

    # --------------------------------------------------------
    # OUTRAS MEMÓRIAS
    # --------------------------------------------------------

    padroes_memoria = [
        r"^\s*estou aprendendo\s+(.+?)[.!?]?\s*$",
        r"^\s*estou estudando\s+(.+?)[.!?]?\s*$",
        r"^\s*estou trabalhando\s+(.+?)[.!?]?\s*$",
        r"^\s*estou fazendo\s+(.+?)[.!?]?\s*$"
    ]

    for padrao in padroes_memoria:

        resultado = re.search(
            padrao,
            mensagem,
            re.IGNORECASE
        )

        if resultado:

            assunto = normalizar_texto(
                resultado.group(1)
            )

            if assunto:

                memoria["memorias"].append(
                    f"O usuário está {padrao.split('estou ')[1].split(r'\\s')[0] if False else 'envolvido com'} {assunto}."
                )

                memoria["memorias"] = remover_duplicatas_lista(
                    memoria["memorias"]
                )

            return memoria

    return memoria


# ============================================================
# CONTEXTO DA MEMÓRIA
# ============================================================

def criar_contexto_memoria(memoria):

    memoria = organizar_memoria(
        memoria
    )

    linhas = []

    nome = memoria.get(
        "nome",
        ""
    ).strip()

    if nome:
        linhas.append(
            f"Nome: {nome}"
        )

    preferencias = memoria.get(
        "preferencias",
        {}
    )

    if preferencias:

        positivas = [
            chave
            for chave, valor in preferencias.items()
            if valor is True
        ]

        negativas = [
            chave
            for chave, valor in preferencias.items()
            if valor is False
        ]

        if positivas:
            linhas.append(
                "Preferências: "
                + ", ".join(positivas)
            )

        if negativas:
            linhas.append(
                "Não gosta de: "
                + ", ".join(negativas)
            )

    projetos = memoria.get(
        "projetos",
        []
    )

    if projetos:
        linhas.append(
            "Projetos: "
            + ", ".join(projetos)
        )

    memorias = memoria.get(
        "memorias",
        []
    )

    if memorias:

        linhas.append(
            "Memórias:"
        )

        linhas.extend(
            f"- {memoria_item}"
            for memoria_item in memorias
        )

    if not linhas:
        return "Nenhuma memória permanente registrada."

    return "\n".join(linhas)


# ============================================================
# HISTÓRICO
# ============================================================

def carregar_historico():

    if not os.path.exists(
        ARQUIVO_HISTORICO
    ):
        return []

    try:

        with open(
            ARQUIVO_HISTORICO,
            "r",
            encoding="utf-8"
        ) as arquivo:

            historico = json.load(
                arquivo
            )

        if not isinstance(
            historico,
            list
        ):
            return []

        return historico

    except Exception:
        return []


def salvar_historico(historico):

    with open(
        ARQUIVO_HISTORICO,
        "w",
        encoding="utf-8"
    ) as arquivo:

        json.dump(
            historico,
            arquivo,
            ensure_ascii=False,
            indent=4
        )


def limitar_historico(historico):

    if not isinstance(
        historico,
        list
    ):
        return []

    limite = max(
        1,
        int(LIMITE_HISTORICO)
    )

    return historico[-limite:]
