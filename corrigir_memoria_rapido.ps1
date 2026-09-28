$ErrorActionPreference = "Stop"

Set-Location "C:\SOL_AI"

$main = Join-Path (Get-Location) "main.py"
$backup = Join-Path (Get-Location) ("main_backup_memoria_" + (Get-Date -Format "yyyyMMdd_HHmmss") + ".py")

Copy-Item $main $backup -Force

$code = Get-Content $main -Raw -Encoding UTF8

$inicio = $code.IndexOf("def atualizar_memoria(")
if ($inicio -lt 0) {
    throw "A função atualizar_memoria() não foi encontrada."
}

$proximo = $code.IndexOf("def ", $inicio + 10)
if ($proximo -lt 0) {
    throw "Não foi possível localizar a próxima função."
}

$novaFuncao = @'
def atualizar_memoria(mensagem, memoria):

    """
    Atualiza a memória sem apagar informações existentes.

    A memória é tratada como acumulativa:
    - novas preferências são adicionadas;
    - novos projetos são adicionados;
    - novas memórias são adicionadas;
    - nome só muda quando a mensagem atual indicar explicitamente um novo nome.
    """

    texto = mensagem.strip()

    if not texto:
        return memoria

    # --------------------------------------------------------
    # Compatibilidade com a estrutura atual
    # --------------------------------------------------------

    usuario = memoria.get("usuario")

    if isinstance(usuario, dict):
        preferencias = usuario.setdefault("preferencias", {})
        projetos = usuario.setdefault("projetos", [])
    else:
        preferencias = memoria.setdefault("preferencias", {})
        projetos = memoria.setdefault("projetos", [])

    memorias = memoria.setdefault("memorias", [])

    # --------------------------------------------------------
    # Extrator por modelo
    # --------------------------------------------------------

    memoria_atual = json.dumps(
        memoria,
        ensure_ascii=False,
        indent=2
    )

    prompt = """
Você é o módulo de memória do Sol AI.

Analise SOMENTE a mensagem atual do usuário.

Extraia informações permanentes que possam ser úteis em
conversas futuras.

É OBRIGATÓRIO registrar preferências explícitas.

Exemplos:
"Eu gosto de rock."
=> preferencias: ["rock"]

"Também gosto muito de fotografia."
=> preferencias: ["fotografia"]

"Estou aprendendo edição de vídeo."
=> memorias: ["O usuário está aprendendo edição de vídeo."]

"Meu projeto se chama Projeto X."
=> projetos: ["Projeto X"]

Não transforme a frase inteira em preferência.

Não apague nada da memória atual.

Não repita informações que já estejam registradas.

Não invente informações.

Não registre perguntas, saudações, brincadeiras ou comentários
sem valor futuro.

Não registre senhas, tokens, chaves ou dados financeiros.

Responda SOMENTE com JSON válido:

{
  "preferencias": [],
  "projetos": [],
  "memorias": []
}

MENSAGEM ATUAL:
""" + texto + """

MEMÓRIA ATUAL:
""" + memoria_atual + """
"""

    dados = {
        "preferencias": [],
        "projetos": [],
        "memorias": []
    }

    try:
        resposta = client.responses.create(
            model="auto:fast",
            instructions=(
                "Você é um extrator de memória. "
                "Responda SOMENTE com JSON válido. "
                "Nunca explique a resposta."
            ),
            input=prompt
        )

        saida = resposta.output_text.strip()

        inicio_json = saida.find("{")
        fim_json = saida.rfind("}")

        if inicio_json >= 0 and fim_json > inicio_json:
            dados_modelo = json.loads(
                saida[inicio_json:fim_json + 1]
            )

            if isinstance(dados_modelo, dict):
                dados.update(dados_modelo)

    except Exception:
        pass

    # --------------------------------------------------------
    # Fallback determinístico
    # Garante que frases explícitas como:
    # "gosto de rock"
    # "estou aprendendo edição de vídeo"
    # não sejam perdidas caso o modelo não extraia.
    # --------------------------------------------------------

    import re

    frases_preferencia = re.findall(
        r"(?:eu\s+)?gosto(?:\s+muito)?\s+(?:de|do|da|dos|das)\s+([^.!?]+)",
        texto,
        flags=re.IGNORECASE
    )

    for item in frases_preferencia:
        item = item.strip(" ,;:")
        if item:
            dados.setdefault("preferencias", []).append(item)

    aprendendo = re.findall(
        r"(?:estou|tô|to)\s+aprendendo\s+([^.!?]+)",
        texto,
        flags=re.IGNORECASE
    )

    for item in aprendendo:
        item = item.strip(" ,;:")
        if item:
            dados.setdefault("memorias", []).append(
                "O usuário está aprendendo " + item + "."
            )

    # --------------------------------------------------------
    # Preferências
    # --------------------------------------------------------

    novas_preferencias = dados.get("preferencias", [])

    if isinstance(novas_preferencias, dict):
        novas_preferencias = list(novas_preferencias.keys())

    if isinstance(novas_preferencias, list):
        for preferencia in novas_preferencias:
            if not isinstance(preferencia, str):
                continue

            preferencia = preferencia.strip(" ,;:.")
            if not preferencia:
                continue

            # Remove prefixos acidentais.
            preferencia = re.sub(
                r"^(?:eu\s+)?gosto(?:\s+muito)?\s+(?:de|do|da|dos|das)\s+",
                "",
                preferencia,
                flags=re.IGNORECASE
            ).strip()

            if preferencia and preferencia.lower() not in {
                str(chave).lower() for chave in preferencias.keys()
            }:
                preferencias[preferencia] = True

    # --------------------------------------------------------
    # Projetos
    # --------------------------------------------------------

    novos_projetos = dados.get("projetos", [])

    if isinstance(novos_projetos, list):
        for projeto in novos_projetos:
            if not isinstance(projeto, str):
                continue

            projeto = projeto.strip()
            if not projeto:
                continue

            if not any(
                str(x).strip().lower() == projeto.lower()
                for x in projetos
            ):
                projetos.append(projeto)

    # --------------------------------------------------------
    # Memórias
    # --------------------------------------------------------

    novas_memorias = dados.get("memorias", [])

    if isinstance(novas_memorias, list):
        for lembranca in novas_memorias:
            if not isinstance(lembranca, str):
                continue

            lembranca = lembranca.strip()
            if not lembranca:
                continue

            if not any(
                str(x).strip().lower() == lembranca.lower()
                for x in memorias
            ):
                memorias.append(lembranca)

    # --------------------------------------------------------
    # Salvar
    # --------------------------------------------------------

    try:
        memoria = organizar_memoria(memoria)
    except Exception:
        pass

    salvar_memoria(memoria)

    return memoria


'@

$codeNovo = $code.Substring(0, $inicio) + $novaFuncao + $code.Substring($proximo)

# Troca qualquer uso restante de auto por auto:fast.
$codeNovo = $codeNovo.Replace('model="auto"', 'model="auto:fast"')

Set-Content $main $codeNovo -Encoding UTF8

python -m py_compile $main

Write-Host ""
Write-Host "OK - memória corrigida."
Write-Host "Backup criado:"
Write-Host $backup
Write-Host ""
Write-Host "Agora execute:"
Write-Host "python main.py"
