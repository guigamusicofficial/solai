import os
import psycopg2
from urllib.parse import urlparse

def obter_conexao():
    database_url = os.environ.get("DATABASE_URL")
    
    if not database_url:
        # Fallback local caso queira testar na sua máquina com Postgres local
        database_url = "postgresql://postgres:postgres@localhost:5432/solai"

    url = urlparse(database_url)
    
    conn = psycopg2.connect(
        database=url.path[1:],
        user=url.username,
        password=url.password,
        host=url.hostname,
        port=url.port
    )
    return conn

def inicializar_banco():
    conn = obter_conexao()
    cursor = conn.cursor()
    
    # Tabela de Memória do Usuário
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS memoria_usuario (
            id SERIAL PRIMARY KEY,
            nome TEXT,
            preferencias JSONB,
            projetos JSONB,
            memorias JSONB,
            sol_nome TEXT,
            sol_idade INT,
            relacionamento_tipo TEXT
        );
    """)
    
    # Tabela de Histórico de Conversas
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS historico_chat (
            id SERIAL PRIMARY KEY,
            role TEXT,
            content TEXT,
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    
    conn.commit()
    cursor.close()
    conn.close()

# Inicializa as tabelas automaticamente ao importar
try:
    inicializar_banco()
except Exception as e:
    print(f"Aviso ao inicializar tabelas do banco: {e}")
