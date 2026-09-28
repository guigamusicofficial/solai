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

def main():
    memoria = carregar_memoria()
    memoria = corrigir_memoria_mojibake(memoria)
    memoria = organizar_memoria(memoria)
    salvar_memoria(memoria)

    historico = carregar_historico()

    print("=" * 55)
    print("                    SOL AI")
    print("=" * 55)
    print("Sol está online através do FreeLLM.")
    print("Memória inteligente ativada.")
    print("Histórico persistente ativado.")
    print("Personalidade carregada.")
    print("Arquitetura modular ativada.")
    print("Digite 'sair' para encerrar.")
    print()

    while True:
        try:
            mensagem = input("Você: ")
        except (KeyboardInterrupt, EOFError):
            print()
            nome = memoria.get("nome", "").strip()
            print(f"Sol: {f'Até depois, {nome}.' if nome else 'Até depois.'}")
            break

        mensagem = mensagem.strip()

        if not mensagem:
            continue

        if mensagem.lower() in ("sair", "exit", "quit"):
            print()
            nome = memoria.get("nome", "").strip()
            print(f"Sol: {f'Até depois, {nome}.' if nome else 'Até depois.'}")
            break

        memoria = atualizar_memoria(mensagem, memoria)

        historico.append({
            "role": "user",
            "content": mensagem
        })
        historico = limitar_historico(historico)
        salvar_historico(historico)

        contexto = criar_contexto_memoria(memoria)
        instrucoes = criar_instrucoes(memoria, contexto)

        try:
            texto = gerar_resposta(instrucoes, historico)

            print()
            print(f"Sol: {texto}")
            print()

            historico.append({
                "role": "assistant",
                "content": texto
            })
            historico = limitar_historico(historico)
            salvar_historico(historico)

        except Exception as erro:
            print()
            print("Sol: Tive um problema para responder.")
            print(f"Erro: {erro}")
            print()

if __name__ == "__main__":
    main()

