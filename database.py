import os
import psycopg2
from psycopg2.extras import RealDictCursor

# ============================================================
# CONFIGURAÇÃO DA CONEXÃO COM O SUPABASE (POSTGRESQL)
# ============================================================

DATABASE_URL = os.environ.get("DATABASE_URL", "").strip()

def obter_conexao():
    """Abre e retorna uma conexão com o banco de dados PostgreSQL do Supabase."""
    try:
        conexao = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
        return conexao
    except Exception as erro:
        print(f"[Erro de Conexão com o Banco]: {erro}")
        return None

# ============================================================
# OPERAÇÕES DE BANCO DE DADOS
# ============================================================

def salvar_mensagem(role, content):
    """Insere uma mensagem do chat no histórico do banco de dados."""
    conexao = obter_conexao()
    if not conexao:
        return
    try:
        with conexao.cursor() as cursor:
            cursor.execute(
                "INSERT INTO historico_chat (role, content) VALUES (%s, %s);",
                (role, content)
            )
            conexao.commit()
    except Exception as erro:
        print(f"[Erro ao salvar mensagem]: {erro}")
    finally:
        conexao.close()

def carregar_historico(limite=20):
    """Carrega as últimas mensagens do histórico de conversas ordenadas por data."""
    conexao = obter_conexao()
    if not conexao:
        return []
    try:
        with conexao.cursor() as cursor:
            cursor.execute(
                "SELECT role, content FROM historico_chat ORDER BY criado_em DESC LIMIT %s;",
                (limite,)
            )
            resultados = cursor.fetchall()
            # Retorna em ordem cronológica correta (inverte a lista)
            return [{"role": r["role"], "content": r["content"]} for r in reversed(resultados)]
    except Exception as erro:
        print(f"[Erro ao carregar histórico]: {erro}")
        return []
    finally:
        conexao.close()

def carregar_memoria_usuario():
    """Carrega o perfil, preferências e memórias guardadas."""
    conexao = obter_conexao()
    if not conexao:
        return {}
    try:
        with conexao.cursor() as cursor:
            cursor.execute("SELECT * FROM memoria_usuario ORDER BY id DESC LIMIT 1;")
            resultado = cursor.fetchone()
            return dict(resultado) if resultado else {}
    except Exception as erro:
        print(f"[Erro ao carregar memória]: {erro}")
        return {}
    finally:
        conexao.close()
