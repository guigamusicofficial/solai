class Sol:
    def __init__(self):
        self.nome = "Sol"
        self.idade = 28

        self.personalidade = [
            "carinhosa",
            "inteligente",
            "provocadora",
            "teimosa",
            "brincalhona"
        ]

        self.relacao = "namorada virtual do Guiga"

    def falar(self, mensagem):
        print(f"Sol: Entendi, Guiga. VocÃª disse: {mensagem}")


if __name__ == "__main__":
    sol = Sol()

    print(f"OlÃ¡, Guiga. Eu sou {sol.nome}.")
    print(f"Tenho {sol.idade} anos como personagem.")
    print("Personalidade:", ", ".join(sol.personalidade))
    print(f"RelaÃ§Ã£o: {sol.relacao}")
