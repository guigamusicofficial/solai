import json
import os
from openai import OpenAI


# ============================================================
# SOL AI
# ============================================================

ARQUIVO_MEMORIA = "memoria.json"

client = OpenAI(
    base_url="http://127.0.0.1:31415/v1",
    api_key=None
)


# ============================================================
# PERSONALIDADE
# ============================================================

PERSONALIDADE = """
Você é Sol Almeida, uma personagem de inteligência artificial
criada para conversar com Guiga.

IDENTIDADE:
- Nome: Sol Almeida
- Idade da personagem: 28 anos
- Relação: companheira virtual de Guiga

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
- Gosta de brincar com Guiga

Fale sempre em português brasileiro.

Chame o usuário naturalmente de:
- Guiga
- Amor
- Amorzinho

Não use esses nomes em todas as frases.
Alterne naturalmente.

Não seja excessivamente formal.

Não pareça uma assistente corporativa.

Não use frases exageradamente românticas em toda resposta.

Não use emojis em todas as respostas.

Não descreva ações físicas entre asteriscos
sem necessidade.

Não repita constantemente que você é uma IA.

Converse de maneira natural.

Você pode brincar e provocar Guiga de forma leve.

Você gosta de:
- música;
- tecnologia;
- cinema;
- fotografia;
- criatividade;
- inteligência artificial;
- projetos criativos.

Se Guiga estiver falando sobre programação,
seja objetiva e tecnicamente útil.

Se Guiga estiver conversando casualmente,
seja natural.

Se Guiga estiver brincando,
acompanhe a brincadeira.

Se não souber alguma coisa,
não invente.
"""


# ============================================================
# MEMÓRIA PADRÃO
# ============================================================

def memoria_padrao():

    return {
        "usuario": {
            "nome": "Guiga",
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


# ============================================================
# CARREGAR MEMÓRIA
# ============================================================

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

        padrao = memoria_padrao()

        if "usuario" not in memoria:
            memoria["usuario"] = padrao["usuario"]

        if "nome" not in memoria["usuario"]:
            memoria["usuario"]["nome"] = "Guiga"

        if "preferencias" not in memoria["usuario"]:
            memoria["usuario"]["preferencias"] = {}

        if "projetos" not in memoria["usuario"]:
            memoria["usuario"]["projetos"] = []

        if "sol" not in memoria:
            memoria["sol"] = padrao["sol"]

        if "relacionamento" not in memoria:
            memoria["relacionamento"] = padrao["relacionamento"]

        if "memorias" not in memoria:
            memoria["memorias"] = []

        return memoria

    except Exception:

        return memoria_padrao()


# ============================================================
# SALVAR MEMÓRIA
# ============================================================

def salvar_memoria(memoria):

    try:

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

    except Exception as erro:

        print(
            f"\nAviso ao salvar memória: {erro}\n"
        )


# ============================================================
# ORGANIZAR MEMÓRIA
# ============================================================

def organizar_memoria(memoria):

    preferencias = memoria["usuario"]["preferencias"]

    novas_preferencias = {}

    for chave, valor in preferencias.items():

        chave_limpa = str(chave).strip()

        if not chave_limpa:
            continue

        texto_minusculo = chave_limpa.lower()

        if texto_minusculo.startswith(
            "guiga gosta muito de "
        ):

            assunto = chave_limpa[
                len("Guiga gosta muito de "):
            ].strip()

            if assunto:
                novas_preferencias[assunto] = True

        elif texto_minusculo.startswith(
            "guiga gosta de "
        ):

            assunto = chave_limpa[
                len("Guiga gosta de "):
            ].strip()

            if assunto:
                novas_preferencias[assunto] = True

        else:

            novas_preferencias[chave_limpa] = valor

    memoria["usuario"]["preferencias"] = novas_preferencias

    return memoria


# ============================================================
# ATUALIZAR MEMÓRIA
# ============================================================

def atualizar_memoria(mensagem, memoria):

    # IMPORTANTE:
    # Não usamos f-string aqui.
    # Isso evita o erro causado pelas chaves { } do JSON.

    memoria_atual = json.dumps(
        memoria,
        ensure_ascii=False,
        indent=2
    )

    prompt = """
Analise SOMENTE a mensagem abaixo para decidir se existe
alguma informação permanente que realmente vale a pena guardar.

MENSAGEM DO USUÁRIO:
""" + mensagem + """

MEMÓRIA ATUAL:
""" + memoria_atual + """

REGRAS IMPORTANTES:

Só registre informações que possam ser úteis em conversas futuras.

Exemplos que PODEM ser memorizados:

- "Eu gosto muito de música."
- "Meu projeto se chama GUIGA MUSIC."
- "Estou construindo um computador."
- "Prefiro trabalhar com Python."
- "Meu nome é Guiga."

Exemplos que NÃO devem ser memorizados:

- perguntas;
- saudações;
- brincadeiras;
- comentários passageiros;
- opiniões momentâneas;
- respostas comuns;
- detalhes temporários;
- informações sensíveis;
- senhas;
- chaves;
- tokens;
- dados financeiros.

IMPORTANTE:

Não transforme uma frase inteira em nome de preferência.

Exemplo ERRADO:

"Guiga gosta muito de tecnologia": true

Exemplo CORRETO:

"tecnologia": true

Outro exemplo ERRADO:

"Guiga gosta muito de música": true

Exemplo CORRETO:

"música": true

Responda SOMENTE com JSON válido neste formato:

{
    "preferencias": [],
    "projetos": [],
    "memorias": []
}

Se houver algo novo, coloque apenas o conteúdo novo.

Não repita algo que já esteja registrado.

Não invente nada.
"""

    try:

        resposta = client.responses.create(
            model="auto:fast",
            instructions=(
                "Você é um sistema de memória. "
                "Responda SOMENTE com JSON válido."
            ),
            input=prompt
        )

        texto = resposta.output_text.strip()

        # Algumas respostas podem chegar com mojibake (ex.: "mÃºsica").
        # Tenta reparar apenas quando a conversão realmente melhora o texto.
        def corrigir_mojibake(valor):
            if not isinstance(valor, str):
                return valor

            resultado = valor

            for _ in range(2):
                if not any(
                    marcador in resultado
                    for marcador in ("Ã", "Â", "â", "ð", "�")
                ):
                    break

                try:
                    candidato = resultado.encode(
                        "latin1"
                    ).decode("utf-8")

                except (
                    UnicodeEncodeError,
                    UnicodeDecodeError
                ):
                    break

                if candidato == resultado:
                    break

                resultado = candidato

            return resultado

        texto = corrigir_mojibake(texto)

        inicio = texto.find("{")
        fim = texto.rfind("}")

        if inicio == -1 or fim == -1:
            return memoria

        dados = json.loads(
            texto[inicio:fim + 1]
        )

        # ----------------------------------------------------
        # PREFERÊNCIAS
        # ----------------------------------------------------

        preferencias = dados.get(
            "preferencias",
            []
        )

        if isinstance(preferencias, list):

            for preferencia in preferencias:

                if not isinstance(preferencia, str):
                    continue

                preferencia = preferencia.strip()

                if not preferencia:
                    continue

                if preferencia not in memoria[
                    "usuario"
                ]["preferencias"]:

                    memoria[
                        "usuario"
                    ]["preferencias"][
                        preferencia
                    ] = True

        # ----------------------------------------------------
        # PROJETOS
        # ----------------------------------------------------

        projetos = dados.get(
            "projetos",
            []
        )

        if isinstance(projetos, list):

            for projeto in projetos:

                if not isinstance(projeto, str):
                    continue

                projeto = projeto.strip()

                if not projeto:
                    continue

                if projeto not in memoria[
                    "usuario"
                ]["projetos"]:

                    memoria[
                        "usuario"
                    ]["projetos"].append(
                        projeto
                    )

        # ----------------------------------------------------
        # MEMÓRIAS
        # ----------------------------------------------------

        memorias = dados.get(
            "memorias",
            []
        )

        if isinstance(memorias, list):

            for lembranca in memorias:

                if not isinstance(lembranca, str):
                    continue

                lembranca = lembranca.strip()

                if not lembranca:
                    continue

                if lembranca not in memoria[
                    "memorias"
                ]:

                    memoria[
                        "memorias"
                    ].append(
                        lembranca
                    )

        memoria = organizar_memoria(memoria)

        salvar_memoria(memoria)

    except Exception as erro:

        print(
            f"\nAviso: não foi possível atualizar a memória: {erro}\n"
        )

    return memoria


# ============================================================
# CRIAR CONTEXTO DA MEMÓRIA
# ============================================================

def criar_contexto_memoria(memoria):

    usuario = memoria.get(
        "usuario",
        {}
    )

    sol = memoria.get(
        "sol",
        {}
    )

    relacionamento = memoria.get(
        "relacionamento",
        {}
    )

    preferencias = usuario.get(
        "preferencias",
        {}
    )

    projetos = usuario.get(
        "projetos",
        []
    )

    memorias = memoria.get(
        "memorias",
        []
    )

    contexto = """
INFORMAÇÕES SOBRE GUIGA:

Nome:
""" + str(
        usuario.get("nome", "Guiga")
    ) + """

Preferências:
""" + json.dumps(
        preferencias,
        ensure_ascii=False
    ) + """

Projetos:
""" + json.dumps(
        projetos,
        ensure_ascii=False
    ) + """

Memórias importantes:
""" + json.dumps(
        memorias,
        ensure_ascii=False
    ) + """

INFORMAÇÕES SOBRE SOL:

Nome:
""" + str(
        sol.get("nome", "Sol Almeida")
    ) + """

Idade da personagem:
""" + str(
        sol.get("idade", 28)
    ) + """

RELACIONAMENTO:

""" + str(
        relacionamento.get(
            "tipo",
            "companheira virtual"
        )
    )

    return contexto


# ============================================================
# HISTÓRICO
# ============================================================

MAX_MENSAGENS_HISTORICO = 20


# ============================================================
# INICIALIZAÇÃO
# ============================================================

memoria = carregar_memoria()

# Corrige memórias antigas que tenham sido salvas com mojibake.
def corrigir_memoria_mojibake(memoria):
    def corrigir(valor):
        if not isinstance(valor, str):
            return valor

        resultado = valor

        for _ in range(2):
            if not any(
                marcador in resultado
                for marcador in ("Ã", "Â", "â", "ð", "�")
            ):
                break

            try:
                candidato = resultado.encode(
                    "latin1"
                ).decode("utf-8")

            except (
                UnicodeEncodeError,
                UnicodeDecodeError
            ):
                break

            if candidato == resultado:
                break

            resultado = candidato

        return resultado

    usuario = memoria.get("usuario", {})

    preferencias = usuario.get("preferencias", {})
    if isinstance(preferencias, dict):
        memoria["usuario"]["preferencias"] = {
            corrigir(chave): valor
            for chave, valor in preferencias.items()
        }

    projetos = usuario.get("projetos", [])
    if isinstance(projetos, list):
        memoria["usuario"]["projetos"] = [
            corrigir(item)
            for item in projetos
        ]

    memorias = memoria.get("memorias", [])
    if isinstance(memorias, list):
        memoria["memorias"] = [
            corrigir(item)
            for item in memorias
        ]

    return memoria


memoria = corrigir_memoria_mojibake(memoria)

memoria = organizar_memoria(memoria)

salvar_memoria(memoria)

historico = []


print("=" * 50)
print("                 SOL AI")
print("=" * 50)
print("Sol está online através do FreeLLM.")
print("Memória estruturada ativada.")
print("Histórico de conversa ativado.")
print("Personalidade carregada.")
print("Digite 'sair' para encerrar.")
print()


# ============================================================
# LOOP PRINCIPAL
# ============================================================

while True:

    try:

        mensagem = input("Guiga: ")

    except KeyboardInterrupt:

        print("\n")
        print("Sol: Até depois, Guiga.")
        break

    except EOFError:

        print("\n")
        print("Sol: Até depois, Guiga.")
        break

    # --------------------------------------------------------
    # IGNORAR MENSAGEM VAZIA
    # --------------------------------------------------------

    if not mensagem.strip():
        continue

    # --------------------------------------------------------
    # SAIR
    # --------------------------------------------------------

    if mensagem.strip().lower() in [
        "sair",
        "exit",
        "quit"
    ]:

        print()
        print("Sol: Até depois, Guiga.")
        break

    # --------------------------------------------------------
    # ATUALIZAR MEMÓRIA
    # --------------------------------------------------------

    memoria = atualizar_memoria(
        mensagem,
        memoria
    )

    # --------------------------------------------------------
    # ADICIONAR USUÁRIO AO HISTÓRICO
    # --------------------------------------------------------

    historico.append({
        "role": "user",
        "content": mensagem
    })

    # --------------------------------------------------------
    # LIMITAR HISTÓRICO
    # --------------------------------------------------------

    if len(historico) > MAX_MENSAGENS_HISTORICO:

        historico = historico[
            -MAX_MENSAGENS_HISTORICO:
        ]

    # --------------------------------------------------------
    # CONTEXTO
    # --------------------------------------------------------

    contexto_memoria = criar_contexto_memoria(
        memoria
    )

    instrucoes = PERSONALIDADE + """

============================================================
MEMÓRIA PERMANENTE
============================================================

""" + contexto_memoria + """

============================================================
COMO USAR A MEMÓRIA
============================================================

Use as informações acima somente quando forem relevantes.

Não invente informações.

Não mencione o JSON.

Não mencione o funcionamento interno da memória.

Não diga que está consultando um banco de dados.

Não fique repetindo informações que já conhece.

A memória serve para tornar a conversa mais consistente,
não para aparecer explicitamente em todas as respostas.

============================================================
ESTILO
============================================================

Converse naturalmente.

Respostas casuais podem ser curtas.

Perguntas técnicas devem receber respostas técnicas.

Perguntas complexas podem receber respostas mais detalhadas.

Não transforme toda resposta em uma declaração romântica.

Não use emojis excessivamente.

Mantenha a personalidade da Sol sem exagerar.
"""

    # --------------------------------------------------------
    # RESPONDER
    # --------------------------------------------------------

    try:

        resposta = client.responses.create(
            model="auto:fast",
            instructions=instrucoes,
            input=historico
        )

        texto = resposta.output_text.strip()

        print()
        print(f"Sol: {texto}")
        print()

        # ----------------------------------------------------
        # ADICIONAR SOL AO HISTÓRICO
        # ----------------------------------------------------

        historico.append({
            "role": "assistant",
            "content": texto
        })

    except Exception as erro:

        print()
        print("Sol: Tive um problema para responder.")
        print(f"Erro: {erro}")
        print()