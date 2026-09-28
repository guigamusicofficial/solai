# ==========================================
# SOL AI - Inicialização do projeto
# ==========================================

$Projeto = "C:\SOL_AI"

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "        CRIANDO A SOL AI" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Criar pasta principal
if (-not (Test-Path $Projeto)) {
    New-Item -ItemType Directory -Path $Projeto | Out-Null
    Write-Host "[OK] Pasta criada: $Projeto" -ForegroundColor Green
}
else {
    Write-Host "[OK] Pasta já existe: $Projeto" -ForegroundColor Green
}

# Criar personalidade.py
$Personalidade = @'
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
        print(f"Sol: Entendi, Guiga. Você disse: {mensagem}")


if __name__ == "__main__":
    sol = Sol()

    print(f"Olá, Guiga. Eu sou {sol.nome}.")
    print(f"Tenho {sol.idade} anos como personagem.")
    print("Personalidade:", ", ".join(sol.personalidade))
    print(f"Relação: {sol.relacao}")
'@

$Arquivo = Join-Path $Projeto "personalidade.py"
Set-Content -Path $Arquivo -Value $Personalidade -Encoding UTF8

Write-Host "[OK] personalidade.py criado." -ForegroundColor Green

# Criar main.py
$Main = @'
from personalidade import Sol

sol = Sol()

print("")
print("===================================")
print("          SOL AI")
print("===================================")
print("")
print("Digite 'sair' para encerrar.")
print("")

while True:

    mensagem = input("Guiga: ")

    if mensagem.lower() == "sair":
        print("Sol: Até depois, Guiga. ❤️")
        break

    sol.falar(mensagem)
'@

$MainArquivo = Join-Path $Projeto "main.py"
Set-Content -Path $MainArquivo -Value $Main -Encoding UTF8

Write-Host "[OK] main.py criado." -ForegroundColor Green

# Criar iniciar_sol.ps1
$Inicializador = @'
Set-Location "C:\SOL_AI"

Write-Host ""
Write-Host "===================================" -ForegroundColor Cyan
Write-Host "          INICIANDO SOL AI" -ForegroundColor Cyan
Write-Host "===================================" -ForegroundColor Cyan
Write-Host ""

python main.py
'@

$StartArquivo = Join-Path $Projeto "iniciar_sol.ps1"
Set-Content -Path $StartArquivo -Value $Inicializador -Encoding UTF8

Write-Host "[OK] iniciar_sol.ps1 criado." -ForegroundColor Green

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "       PROJETO CRIADO COM SUCESSO" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Local: $Projeto"
Write-Host ""
Write-Host "Arquivos:"
Write-Host "  personalidade.py"
Write-Host "  main.py"
Write-Host "  iniciar_sol.ps1"
Write-Host ""
Write-Host "Para iniciar a Sol:"
Write-Host ""
Write-Host "  cd C:\SOL_AI"
Write-Host "  python main.py"
Write-Host ""