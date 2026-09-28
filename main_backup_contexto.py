import re

from config import CONFIG

from memory import (
    carregar_memoria,
    corrigir_memoria_mojibake,
    organizar_memoria,
    salvar_memoria,
    carregar_historico,
    salvar_historico,
    atualizar_memoria,
    criar_contexto_memoria,
    limitar_historico,
)

from personality import criar_instrucoes
from core import gerar_resposta


# ============================================================
# MODO TURBO
# ============================================================

MAX_HISTORICO_TURBO = 12


PADRAO_MEMORIA_TURBO = re.compile(
    r"\b(?:"
    r"meu nome é|"
    r"pode me chamar de|"
    r"quero que me chame de|"
    r"eu gosto|"
    r"também gosto|"
    r"gosto muito|"
    r"não gosto|"
    r"adoro|"
    r"odeio|"
    r"eu curto|"
    r"curto muito|"
    r"sou fã de|"
    r"meu hobby|"
    r"meus hobbies|"
    r"estou aprendendo|"
    r"estou estudando|"
    r"estou trabalhando|"
    r"estou fazendo|"
    r"estou construindo|"
    r"meu projeto|"
    r"minha profissão|"
    r"eu trabalho|"
    r"moro em|"
    r"sou de|"
    r"tenho preferência|"
    r"minha música favorita|"
    r"meu filme favorito|"
    r"meu artista favorito|"
    r"meu estilo favorito|"
    r"minha banda favorita|"
    r"meu cantor favorito"
    r")\b",
    re.IGNORECASE,
)


def parece_informacao_de_memoria(mensagem):
    """
    Decide se a mensagem provavelmente contém uma informação
    permanente sobre o usuário.

    Se não houver indícios, evitamos uma chamada adicional
    ao sistema inteligente de memória.
    """

    return bool(PADRAO_MEMORIA_TURBO.search(mensagem))


def limitar_historico_turbo(historico):
    """
    Mantém somente as últimas mensagens relevantes.

    A função original continua sendo usada primeiro para
    preservar a arquitetura existente.
    """

    historico = limitar_historico(historico)

    if len(historico) > MAX_HISTORICO_TURBO:
        historico = historico[-MAX_HISTORICO_TURBO:]

    return historico


def main():

    # ========================================================
    # MEMÓRIA
    # ========================================================

    memoria = carregar_memoria()
    memoria = corrigir_memoria_mojibake(memoria)
    memoria = organizar_memoria(memoria)
    salvar_memoria(memoria)

    # ========================================================
    # HISTÓRICO
    # ========================================================

    historico = carregar_historico()
    historico = limitar_historico_turbo(historico)

    # ========================================================
    # INTERFACE
    # ========================================================

    print("=" * 55)
    print("                    SOL AI")
    print("=" * 55)
    print("Sol está online através do FreeLLM.")
    print("Memória inteligente ativada.")
    print("Histórico persistente ativado.")
    print("Personalidade carregada.")
    print("Arquitetura modular ativada.")
    print("Modo Turbo ativado.")
    print("Digite 'sair' para encerrar.")
    print()

    # ========================================================
    # LOOP PRINCIPAL
    # ========================================================

    while True:

        try:
            mensagem = input("Você: ")

        except (KeyboardInterrupt, EOFError):

            print()

            nome = memoria.get("nome", "").strip()

            if nome:
                print(f"Sol: Até depois, {nome}.")
            else:
                print("Sol: Até depois.")

            break

        mensagem = mensagem.strip()

        # ----------------------------------------------------
        # Ignora ENTER vazio
        # ----------------------------------------------------

        if not mensagem:
            continue

        # ----------------------------------------------------
        # Saída
        # ----------------------------------------------------

        if mensagem.lower() in ("sair", "exit", "quit"):

            print()

            nome = memoria.get("nome", "").strip()

            if nome:
                print(f"Sol: Até depois, {nome}.")
            else:
                print("Sol: Até depois.")

            break

        # ====================================================
        # MEMÓRIA TURBO
        # ====================================================

        if parece_informacao_de_memoria(mensagem):

            memoria = atualizar_memoria(
                mensagem,
                memoria
            )

        # ====================================================
        # HISTÓRICO DO USUÁRIO
        # ====================================================

        historico.append({
            "role": "user",
            "content": mensagem
        })

        historico = limitar_historico_turbo(historico)

        salvar_historico(historico)

        # ====================================================
        # CONTEXTO
        # ====================================================

        contexto = criar_contexto_memoria(memoria)

        instrucoes = criar_instrucoes(
            memoria,
            contexto
        )

        # ====================================================
        # RESPOSTA DA SOL
        # ====================================================

        try:

            texto = gerar_resposta(
                instrucoes,
                historico
            )

            print()
            print(f"Sol: {texto}")
            print()

            # ------------------------------------------------
            # Histórico da resposta
            # ------------------------------------------------

            historico.append({
                "role": "assistant",
                "content": texto
            })

            historico = limitar_historico_turbo(
                historico
            )

            salvar_historico(historico)

        except Exception as erro:

            print()
            print("Sol: Tive um problema para responder.")
            print(f"Erro: {erro}")
            print()


# ============================================================
# EXECUÇÃO
# ============================================================

if __name__ == "__main__":
    main()