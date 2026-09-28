$ErrorActionPreference = "Stop"

$root = "C:\SOL_AI"
$index = Join-Path $root "web\index.html"
$assets = Join-Path $root "web\assets"

if (!(Test-Path $index)) {
    Write-Host "ERRO: C:\SOL_AI\web\index.html não encontrado." -ForegroundColor Red
    Read-Host "Pressione Enter"
    exit 1
}

New-Item -ItemType Directory -Force -Path $assets | Out-Null

Copy-Item ".\jade.png" (Join-Path $assets "jade.png") -Force

$backup = Join-Path $root "web\index_before_jade_image.html"
Copy-Item $index $backup -Force

$html = Get-Content $index -Raw -Encoding UTF8

if ($html -match 'data-character="jade"') {
    Write-Host "A Jade já existe no HTML. A imagem foi atualizada." -ForegroundColor Yellow
}
else {
    $marker = '      <button class="right-card" data-character="valentina"><img src="/web/assets/valentina.png"><div><b>Valentina ♥</b><span>A intensa</span><em>● Online</em><strong>▣ &nbsp; Conversar</strong></div></button>'
    $jadeCard = '      <button class="right-card" data-character="jade"><img src="/web/assets/jade.png" alt="Jade"><div><b>Jade ♣</b><span>A elegante</span><em>● Online</em><strong>▣ &nbsp; Conversar</strong></div></button>'

    if (!$html.Contains($marker)) {
        Write-Host "ERRO: o card da Valentina não foi encontrado. Nenhuma alteração no HTML." -ForegroundColor Red
        Read-Host "Pressione Enter"
        exit 1
    }

    $html = $html.Replace($marker, $marker + "`r`n" + $jadeCard)
    Set-Content $index $html -Encoding UTF8
    Write-Host "Card da Jade adicionado ao painel PERSONAGENS." -ForegroundColor Green
}

Write-Host ""
Write-Host "JADE INSTALADA" -ForegroundColor Magenta
Write-Host "Imagem: C:\SOL_AI\web\assets\jade.png" -ForegroundColor Green
Write-Host "Backup: C:\SOL_AI\web\index_before_jade_image.html" -ForegroundColor DarkGray
Write-Host ""
Write-Host "Agora abra/recarregue o SOL AI e pressione CTRL+F5."
Read-Host "Pressione Enter para fechar"
