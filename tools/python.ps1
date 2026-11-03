# Trova l'ambiente Python del progetto usabile da questo utente Windows (incluso da avvia.ps1 e build.ps1).
# Un ambiente creato da un altro utente punta al suo Python, che da qui non si puo' avviare:
# in quel caso se ne crea uno per l'utente corrente, .venv-<utente>, accanto agli altri.

function Test-Python([string]$exe) {
    if (-not (Test-Path $exe)) { return $false }
    try { & $exe -c "import sys" 2>$null; return $LASTEXITCODE -eq 0 } catch { return $false }
}

function Find-BasePython {
    # "python" puo' essere il collegamento al Microsoft Store, che non esegue nulla: si prova davvero
    $py = Get-Command py -ErrorAction SilentlyContinue
    if ($py) {
        $exe = & $py.Source -3 -c "import sys; print(sys.executable)" 2>$null
        if ($LASTEXITCODE -eq 0 -and $exe) { return $exe.Trim() }
    }
    $candidates = @((Get-Command python -ErrorAction SilentlyContinue).Source) +
        @(Get-ChildItem "$env:LOCALAPPDATA\Programs\Python\Python3*\python.exe" -ErrorAction SilentlyContinue |
          Sort-Object FullName -Descending | ForEach-Object FullName)
    foreach ($exe in $candidates) {
        if ($exe -and (Test-Python $exe)) { return $exe }
    }
    throw "Python 3 non trovato: installalo da https://www.python.org (o con: winget install Python.Python.3.14 --scope user)."
}

function Get-ProjectPython {
    $dirs = @(".venv") + @(Get-ChildItem -Directory -Filter ".venv-*" | Sort-Object Name | ForEach-Object Name)
    foreach ($dir in $dirs) {
        $exe = Join-Path $dir "Scripts\python.exe"
        if (Test-Python $exe) { return (Resolve-Path $exe).Path }
    }
    $dir = ".venv-" + ($env:USERNAME -replace '[^\w.-]', '_')
    Write-Host "Creo l'ambiente Python $dir (solo la prima volta)..."
    & (Find-BasePython) -m venv $dir
    $exe = (Resolve-Path (Join-Path $dir "Scripts\python.exe")).Path
    & $exe -m pip install -q -r requirements.txt
    if ($LASTEXITCODE -ne 0) { throw "Installazione delle librerie non riuscita" }
    return $exe
}
