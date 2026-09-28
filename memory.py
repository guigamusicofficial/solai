import json
import re
from config import LIMITE_HISTORICO
from database import obter_conexao

# ============================================================
# MEMÓRIA (POSTGRESQL)
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
            "tipo": "namorada virtual do Guiga"
        }
    }


def carregar_memoria():
    try:
        conn = obter_conexao()
        cursor = conn.cursor()
        
        cursor.execute("SELECT nome, preferencias, projetos, memorias, sol_nome, sol_idade, relacionamento_tipo FROM memoria_usuario ORDER BY id DESC LIMIT 1;")
        row = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        if not row:
            memoria = memoria_padrao()
            salvar_memoria(memoria)
            return memoria
            
        memoria = {
            "nome": row[0] or "",
            "preferencias": row[1] if isinstance(row[1], dict) else json.loads(row[1] or "{}"),
            "projetos": row[2] if isinstance(row[2], list) else json.loads(row[2] or "[]"),
            "memorias": row[3] if isinstance(row[3], list) else json.loads(row[3] or "[]"),
            "sol": {
                "nome": row[4] or "Sol Almeida",
                "idade": row[5] or 28
            },
            "relacionamento": {
                "tipo": row[6] or "namorada virtual do Guiga"
            }
        }
        return memoria
    except Exception as e:
        print(f"Erro ao carregar memória do banco: {e}")
        return memoria_padrao()


def salvar_memoria(memoria):
    try:
        conn = obter_conexao()
        cursor = conn.cursor()
        
        # Garante que existe pelo menos uma linha na tabela
        cursor.execute("SELECT COUNT(*) FROM memoria_usuario;")
        count = cursor.fetchone()[0]
        
        nome = memoria.get("nome", "")
        prefs = json.dumps(memoria.get("preferencias", {}), ensure_ascii=False)
        projs = json.dumps(memoria.get("projetos", []), ensure_ascii=False)
        mems = json.dumps(memoria.get("memorias", []), ensure_ascii=False)
        sol_nome = memoria.get("sol", {}).get("nome", "Sol Almeida")
        sol_idade = memoria.get("sol", {}).get("idade", 28)
        rel_tipo = memoria.get("relacionamento", {}).get("tipo", "namorada virtual do Guiga")
        
        if count == 0:
            cursor.execute("""
                INSERT INTO memoria_usuario (nome, preferencias, projetos, memorias, sol_nome, sol_idade, relacionamento_tipo)
                VALUES (%s, %s::jsonb, %s::jsonb, %s::jsonb, %s, %s, %s);
            """, (nome, prefs, projs, mems, sol_nome, sol_idade, rel_tipo))
        else:
            cursor.execute("""
                UPDATE memoria_usuario 
                SET nome = %s, preferencias = %s::jsonb, projetos = %s::jsonb, memorias = %s::jsonb, 
                    sol_nome = %s, sol_idade = %s, relacionamento_tipo = %s
                WHERE id = (SELECT id FROM memoria_usuario ORDER BY id DESC LIMIT 1);
            """, (nome, prefs, projs, mems, sol_nome, sol_idade, rel_tipo))
            
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Erro ao salvar memória no banco: {e}")


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

    if isinstance(memoria.get("nome"), str):
        memoria["nome"] = corrigir_texto_mojibake(memoria["nome"])

    for chave in ("projetos", "memorias"):
        valores = memoria.get(chave, [])
        if isinstance(valores, list):
            memoria[chave] = [
                corrigir_texto_mojibake(valor) if isinstance(valor, str) else valor
                for valor in valores
            ]

    preferencias = memoria.get("preferencias", {})
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
    texto = re.sub(r"\s+", " ", texto).strip()
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

    nome = memoria.get("nome", "")
    if isinstance(nome, str):
        base["nome"] = normalizar_texto(nome)

    preferencias = memoria.get("preferencias", {})
    if isinstance(preferencias, dict):
        novas_preferencias = {}
        for chave, valor in preferencias.items():
            chave = normalizar_texto(str(chave))
            if chave:
                novas_preferencias[chave] = valor
        base["preferencias"] = novas_preferencias

    base["projetos"] = remover_duplicatas_lista(memoria.get("projetos", []))
    base["memorias"] = remover_duplicatas_lista(memoria.get("memorias", []))

    sol = memoria.get("sol", {})
    if isinstance(sol, dict):
        base["sol"]["nome"] = sol.get("nome", "Sol Almeida")
        base["sol"]["idade"] = sol.get("idade", 28)

    relacionamento = memoria.get("relacionamento", {})
    if isinstance(relacionamento, dict):
        base["relacionamento"]["tipo"] = relacionamento.get("tipo", "namorada virtual do Guiga")

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

    padroes_nome = [
        r"^\s*meu nome é\s+(.+?)[.!?]?\s*$",
        r"^\s*pode me chamar de\s+(.+?)[.!?]?\s*$",
        r"^\s*quero que me chame de\s+(.+?)[.!?]?\s*$"
    ]
    for padrao in padroes_nome:
        resultado = re.search(padrao, mensagem, re.IGNORECASE)
        if resultado:
            nome = normalizar_texto(resultado.group(1))
            if nome:
                memoria["nome"] = nome
            return memoria

    padroes_gosto = [
        r"^\s*eu gosto de\s+(.+?)[.!?]?\s*$",
        r"^\s*gosto muito de\s+(.+?)[.!?]?\s*$",
        r"^\s*eu curto\s+(.+?)[.!?]?\s*$",
        r"^\s*curto muito\s+(.+?)[.!?]?\s*$",
        r"^\s*adoro\s+(.+?)[.!?]?\s*$"
    ]
    for padrao in padroes_gosto:
        resultado = re.search(padrao, mensagem, re.IGNORECASE)
        if resultado:
            gosto = normalizar_texto(resultado.group(1))
            if gosto:
                chave = gosto.casefold()
                memoria["preferencias"][chave] = True
            return memoria

    padroes_nao_gosto = [
        r"^\s*não gosto de\s+(.+?)[.!?]?\s*$",
        r"^\s*odeio\s+(.+?)[.!?]?\s*$"
    ]
    for padrao in padroes_nao_gosto:
        resultado = re.search(padrao, mensagem, re.IGNORECASE)
        if resultado:
            item = normalizar_texto(resultado.group(1))
            if item:
                chave = item.casefold()
                memoria["preferencias"][chave] = False
            return memoria

    padroes_projeto = [
        r"^\s*meu projeto é\s+(.+?)[.!?]?\s*$",
        r"^\s*meu projeto\s+(.+?)[.!?]?\s*$",
        r"^\s*estou construindo\s+(.+?)[.!?]?\s*$"
    ]
    for padrao in padroes_projeto:
        resultado = re.search(padrao, mensagem, re.IGNORECASE)
        if resultado:
            projeto = normalizar_texto(resultado.group(1))
            if projeto:
                memoria["projetos"].append(projeto)
                memoria["projetos"] = remover_duplicatas_lista(memoria["projetos"])
            return memoria

    return memoria


# ============================================================
# CONTEXTO DA MEMÓRIA
# ============================================================

def criar_contexto_memoria(memoria):
    memoria = organizar_memoria(memoria)
    linhas = []

    nome = memoria.get("nome", "").strip()
    if nome:
        linhas.append(f"Nome: {nome}")

    preferencias = memoria.get("preferencias", {})
    if preferencias:
        positivas = [chave for chave, valor in preferencias.items() if valor is True]
        negativas = [chave for chave, valor in preferencias.items() if valor is False]
        if positivas:
            linhas.append("Preferências: " + ", ".join(positivas))
        if negativas:
            linhas.append("Não gosta de: " + ", ".join(negativas))

    projetos = memoria.get("projetos", [])
    if projetos:
        linhas.append("Projetos: " + ", ".join(projetos))

    memorias = memoria.get("memorias", [])
    if memorias:
        linhas.append("Memórias:")
        linhas.extend(f"- {item}" for item in memorias)

    if not linhas:
        return "Nenhuma memória permanente registrada."

    return "\n".join(linhas)


# ============================================================
# HISTÓRICO (POSTGRESQL)
# ============================================================

def carregar_historico():
    try:
        conn = obter_conexao()
        cursor = conn.cursor()
        
        cursor.execute("SELECT role, content FROM historico_chat ORDER BY id ASC;")
        rows = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        historico = [{"role": row[0], "content": row[1]} for row in rows]
        return historico
    except Exception as e:
        print(f"Erro ao carregar histórico do banco: {e}")
        return []


def salvar_historico(historico):
    try:
        conn = obter_conexao()
        cursor = conn.cursor()
        
        # Limpa e reinsere para manter sincronizado com o limite atual
        cursor.execute("DELETE FROM historico_chat;")
        
        for msg in historico:
            cursor.execute(
                "INSERT INTO historico_chat (role, content) VALUES (%s, %s);",
                (msg.get("role"), msg.get("content"))
            )
            
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Erro ao salvar histórico no banco: {e}")


def limitar_historico(historico):
    if not isinstance(historico, list):
        return []
    limite = max(1, int(LIMITE_HISTORICO))
    return historico[-limite:]
