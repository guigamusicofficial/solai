# ============================================================
# INSTALADOR SOL AI - ARQUITETURA CONFIGURÁVEL
# Corrigido: não copia arquivos para eles mesmos.
# Preserva memoria.json e historico.json.
# ============================================================

$ErrorActionPreference = "Stop"

$Pasta = "C:\SOL_AI"
$MainDestino = Join-Path $Pasta "main.py"
$ConfigDestino = Join-Path $Pasta "sol_config.json"

Write-Host ""
Write-Host "=======================================================" -ForegroundColor Cyan
Write-Host "              INSTALADOR SOL AI" -ForegroundColor Cyan
Write-Host "=======================================================" -ForegroundColor Cyan
Write-Host ""

if (-not (Test-Path $Pasta)) {
    New-Item -ItemType Directory -Path $Pasta -Force | Out-Null
}

$OrigemMain = Join-Path $PSScriptRoot "main_sol_ai_configurada.py"
$OrigemConfig = Join-Path $PSScriptRoot "sol_config.json"

if (-not (Test-Path $OrigemMain)) {
    Write-Host "ERRO: main_sol_ai_configurada.py não foi encontrado." -ForegroundColor Red
    Write-Host "Coloque o PS1 e o PY na mesma pasta." -ForegroundColor Yellow
    exit 1
}

if (-not (Test-Path $OrigemConfig)) {
    Write-Host "ERRO: sol_config.json não foi encontrado." -ForegroundColor Red
    Write-Host "Coloque o PS1 e o JSON na mesma pasta." -ForegroundColor Yellow
    exit 1
}

# Backup
$BackupDir = Join-Path $Pasta "backups"
if (-not (Test-Path $BackupDir)) {
    New-Item -ItemType Directory -Path $BackupDir -Force | Out-Null
}

$Data = Get-Date -Format "yyyyMMdd_HHmmss"

if ((Test-Path $MainDestino) -and ((Resolve-Path $OrigemMain).Path -ne (Resolve-Path $MainDestino).Path)) {
    Copy-Item $MainDestino (Join-Path $BackupDir "main_antes_config_$Data.py") -Force
}

if ((Test-Path $ConfigDestino) -and ((Resolve-Path $OrigemConfig).Path -ne (Resolve-Path $ConfigDestino).Path)) {
    Copy-Item $ConfigDestino (Join-Path $BackupDir "sol_config_antes_config_$Data.json") -Force
}

# Instala main.py somente se a origem não for o próprio destino.
if ((Resolve-Path $OrigemMain).Path -ne (Resolve-Path $MainDestino -ErrorAction SilentlyContinue).Path) {
    Copy-Item $OrigemMain $MainDestino -Force
}
else {
    Write-Host "main.py já está no destino; nenhuma cópia desnecessária." -ForegroundColor DarkGray
}

# Instala sol_config.json somente se a origem não for o próprio destino.
if ((Resolve-Path $OrigemConfig).Path -ne (Resolve-Path $ConfigDestino -ErrorAction SilentlyContinue).Path) {
    Copy-Item $OrigemConfig $ConfigDestino -Force
}
else {
    Write-Host "sol_config.json já está no destino; nenhuma cópia desnecessária." -ForegroundColor DarkGray
}

# Validação
Push-Location $Pasta
try {
    python -m py_compile .\main.py
    if ($LASTEXITCODE -ne 0) {
        throw "A validação do main.py falhou."
    }

    python -c "import json; json.load(open('sol_config.json', encoding='utf-8')); print('Config JSON: OK')"
    if ($LASTEXITCODE -ne 0) {
        throw "A validação do sol_config.json falhou."
    }
}
finally {
    Pop-Location
}

Write-Host ""
Write-Host "=======================================================" -ForegroundColor Green
Write-Host "              INSTALAÇÃO CONCLUÍDA" -ForegroundColor Green
Write-Host "=======================================================" -ForegroundColor Green
Write-Host ""
Write-Host "main.py: OK" -ForegroundColor Green
Write-Host "sol_config.json: OK" -ForegroundColor Green
Write-Host "memoria.json: preservado" -ForegroundColor Green
Write-Host "historico.json: preservado" -ForegroundColor Green
Write-Host ""
Write-Host "Para iniciar:" -ForegroundColor Cyan
Write-Host "cd C:\SOL_AI"
Write-Host "python main.py"
Write-Host ""
