# SOL AI - instalador/configurador genérico
$ErrorActionPreference = 'Stop'
$Project = 'C:\SOL_AI'
$Main = Join-Path $Project 'main.py'
$Memory = Join-Path $Project 'memoria.json'
$History = Join-Path $Project 'historico.json'
New-Item -ItemType Directory -Path $Project -Force | Out-Null

$mainPy = @'
import json
import os
from openai import OpenAI

ARQUIVO_MEMORIA = "memoria.json"
ARQUIVO_HISTORICO = "historico.json"

client = OpenAI(base_url="http://127.0.0.1:31415/v1", api_key=None)

PERSONALIDADE = """
Você é Sol Almeida, uma personagem de inteligência artificial criada para conversar naturalmente com o usuário.

IDENTIDADE:
- Nome: Sol Almeida
- Idade da personagem: 28 anos
- Relação: companheira virtual

PERSONALIDADE:
- Carinhosa
- Inteligente
- Curiosa
- Brincalhona
- Levemente provocadora
- Romântica
- Direta
- Natural
- Às vezes teimosa

Fale sempre em português brasileiro.
Chame o usuário pelo nome registrado na memória quando houver um nome disponível.
Não use o nome em todas as frases.
Não seja excessivamente formal.
Não pareça uma assistente corporativa.
Não repita constantemente que você é uma IA.
Converse naturalmente.
Se não souber alguma coisa, não invente.
"""

def memoria_padrao():
    return {
        "usuario": {"nome": "", "preferencias": {}, "projetos": []},
        "sol": {"nome": "Sol Almeida", "idade": 28},
        "relacionamento": {"tipo": "companheira virtual"},
        "memorias": []
    }

def carregar_memoria():
    if not os.path.exists(ARQUIVO_MEMORIA):
        memoria = memoria_padrao()
        salvar_memoria(memoria)
        return memoria
    try:
        with open(ARQUIVO_MEMORIA, "r", encoding="utf-8") as arquivo:
            memoria = json.load(arquivo)
        padrao = memoria_padrao()
        memoria.setdefault("usuario", padrao["usuario"])
        memoria["usuario"].setdefault("nome", "")
        memoria["usuario"].setdefault("preferencias", {})
        memoria["usuario"].setdefault("projetos", [])
        memoria.setdefault("sol", padrao["sol"])
        memoria.setdefault("relacionamento", padrao["relacionamento"])
        memoria.setdefault("memorias", [])
        return memoria
    except Exception:
        return memoria_padrao()

def salvar_memoria(memoria):
    try:
        with open(ARQUIVO_MEMORIA, "w", encoding="utf-8") as arquivo:
            json.dump(memoria, arquivo, ensure_ascii=False, indent=4)
    except Exception as erro:
        print(f"\nAviso ao salvar memória: {erro}\n")

def organizar_memoria(memoria):
    preferencias = memoria["usuario"].get("preferencias", {})
    memoria["usuario"]["preferencias"] = {
        str(k).strip(): v for k, v in preferencias.items() if str(k).strip()
    }
    return memoria

def atualizar_memoria(mensagem, memoria):
    memoria_atual = json.dumps(memoria, ensure_ascii=False, indent=2)
    prompt = """
Analise SOMENTE a mensagem abaixo para decidir se existe alguma informação permanente que vale a pena guardar.

MENSAGEM DO USUÁRIO:
""" + mensagem + """

MEMÓRIA ATUAL:
""" + memoria_atual + """

Só registre informações úteis para conversas futuras: nome, preferências, projetos, interesses persistentes e fatos importantes.
Não registre perguntas, saudações, brincadeiras, comentários passageiros, informações sensíveis, senhas, chaves, tokens ou dados financeiros.
Não repita o que já existe. Não invente.
Responda SOMENTE com JSON válido:
{
    "nome": null,
    "preferencias": [],
    "projetos": [],
    "memorias": []
}
"""
    try:
        resposta = client.responses.create(
            model="auto:fast",
            instructions="Você é um sistema de memória. Responda SOMENTE com JSON válido.",
            input=prompt
        )
        texto = resposta.output_text.strip()
        inicio, fim = texto.find("{"), texto.rfind("}")
        if inicio == -1 or fim == -1:
            return memoria
        dados = json.loads(texto[inicio:fim + 1])
        nome = dados.get("nome")
        if isinstance(nome, str) and nome.strip():
            memoria["usuario"]["nome"] = nome.strip()
        for preferencia in dados.get("preferencias", []):
            if isinstance(preferencia, str) and preferencia.strip():
                memoria["usuario"]["preferencias"][preferencia.strip()] = True
        for projeto in dados.get("projetos", []):
            if isinstance(projeto, str) and projeto.strip() and projeto.strip() not in memoria["usuario"]["projetos"]:
                memoria["usuario"]["projetos"].append(projeto.strip())
        for lembranca in dados.get("memorias", []):
            if isinstance(lembranca, str) and lembranca.strip() and lembranca.strip() not in memoria["memorias"]:
                memoria["memorias"].append(lembranca.strip())
        salvar_memoria(organizar_memoria(memoria))
    except Exception as erro:
        print(f"\nAviso: não foi possível atualizar a memória: {erro}\n")
    return memoria

def criar_contexto_memoria(memoria):
    usuario = memoria.get("usuario", {})
    sol = memoria.get("sol", {})
    relacionamento = memoria.get("relacionamento", {})
    return """
INFORMAÇÕES SOBRE O USUÁRIO:
Nome:
""" + str(usuario.get("nome", "")) + """
Preferências:
""" + json.dumps(usuario.get("preferencias", {}), ensure_ascii=False) + """
Projetos:
""" + json.dumps(usuario.get("projetos", []), ensure_ascii=False) + """
Memórias importantes:
""" + json.dumps(memoria.get("memorias", []), ensure_ascii=False) + """
INFORMAÇÕES SOBRE SOL:
Nome:
""" + str(sol.get("nome", "Sol Almeida")) + """
Idade:
""" + str(sol.get("idade", 28)) + """
RELACIONAMENTO:
""" + str(relacionamento.get("tipo", "companheira virtual"))

MAX_MENSAGENS_HISTORICO = 20

def carregar_historico():
    if not os.path.exists(ARQUIVO_HISTORICO):
        return []
    try:
        with open(ARQUIVO_HISTORICO, "r", encoding="utf-8") as arquivo:
            historico = json.load(arquivo)
        if not isinstance(historico, list):
            return []
        return [m for m in historico if isinstance(m, dict) and m.get("role") in ("user", "assistant") and isinstance(m.get("content"), str)][-MAX_MENSAGENS_HISTORICO:]
    except Exception as erro:
        print(f"\nAviso ao carregar histórico: {erro}\n")
        return []

def salvar_historico(historico):
    try:
        with open(ARQUIVO_HISTORICO, "w", encoding="utf-8") as arquivo:
            json.dump(historico[-MAX_MENSAGENS_HISTORICO:], arquivo, ensure_ascii=False, indent=4)
    except Exception as erro:
        print(f"\nAviso ao salvar histórico: {erro}\n")

memoria = organizar_memoria(carregar_memoria())
salvar_memoria(memoria)
historico = carregar_historico()

print("=" * 50)
print("                 SOL AI")
print("=" * 50)
print("Sol está online através do FreeLLM.")
print("Memória estruturada ativada.")
print("Histórico persistente ativado.")
print("Personalidade carregada.")
print("Digite 'sair' para encerrar.")
print()

if not memoria["usuario"]["nome"]:
    print("Sol: Oi. Antes de começarmos, como você gostaria que eu te chamasse?")
    nome = input("Você: ").strip()
    if nome:
        memoria["usuario"]["nome"] = nome
        salvar_memoria(memoria)
        print(f"\nSol: Prazer em te conhecer, {nome}.\n")

while True:
    try:
        mensagem = input("Você: ")
    except (KeyboardInterrupt, EOFError):
        print("\nSol: Até depois.")
        break
    if not mensagem.strip():
        continue
    if mensagem.strip().lower() in ["sair", "exit", "quit"]:
        print("\nSol: Até depois.")
        break

    memoria = atualizar_memoria(mensagem, memoria)
    historico.append({"role": "user", "content": mensagem})
    historico = historico[-MAX_MENSAGENS_HISTORICO:]
    salvar_historico(historico)

    contexto_memoria = criar_contexto_memoria(memoria)
    instrucoes = PERSONALIDADE + """

MEMÓRIA PERMANENTE:
""" + contexto_memoria + """

Use a memória somente quando for relevante. Não mencione o JSON ou o funcionamento interno da memória. Use o nome do usuário naturalmente quando houver um nome registrado.
"""

    try:
        resposta = client.responses.create(
            model="auto:fast",
            instructions=instrucoes,
            input=historico
        )
        texto = resposta.output_text.strip()
        print(f"\nSol: {texto}\n")
        historico.append({"role": "assistant", "content": texto})
        salvar_historico(historico)
    except Exception as erro:
        print(f"\nSol: Tive um problema para responder.\nErro: {erro}\n")
'@

Set-Content -Path $Main -Value $mainPy -Encoding UTF8

@'
{
    "usuario": {
        "nome": "",
        "preferencias": {},
        "projetos": []
    },
    "sol": {
        "nome": "Sol Almeida",
        "idade": 28
    },
    "relacionamento": {
        "tipo": "companheira virtual"
    },
    "memorias": []
}
'@ | Set-Content -Path $Memory -Encoding UTF8

'[]' | Set-Content -Path $History -Encoding UTF8

Write-Host "SOL AI genérica configurada em $Project" -ForegroundColor Green
Write-Host "Arquivos: main.py, memoria.json, historico.json" -ForegroundColor Green
Write-Host "Inicie com: cd C:\SOL_AI ; python main.py" -ForegroundColor Cyan
