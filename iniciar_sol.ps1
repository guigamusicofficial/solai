[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

Set-Location "C:\SOL_AI"

Write-Host ""
Write-Host "===================================" -ForegroundColor Cyan
Write-Host "          INICIANDO SOL AI" -ForegroundColor Cyan
Write-Host "===================================" -ForegroundColor Cyan
Write-Host ""

python main.py