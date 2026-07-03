# install.ps1 - Installatie zk-gchat MCP-server (Windows)
# Idempotent: herhaald draaien is veilig.

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

function Fail($msg) {
    Write-Host ""
    Write-Host "[FOUT] $msg" -ForegroundColor Red
    Write-Host "Installatie gestopt." -ForegroundColor Red
    exit 1
}

Write-Host "=== zk-gchat MCP installatie ===" -ForegroundColor Cyan
Write-Host ""

# Stap 1: python aanwezig?
Write-Host "[1/4] Python controleren..." -ForegroundColor Cyan
$python = $null
foreach ($cmd in @("python", "python3", "py")) {
    if (Get-Command $cmd -ErrorAction SilentlyContinue) {
        $python = $cmd
        break
    }
}
if (-not $python) {
    Fail "Python is niet gevonden. Installeer Python 3.10+ via https://www.python.org/downloads/ en zorg dat het in je PATH staat."
}
$pyVersion = & $python --version 2>&1
Write-Host "      Gevonden: $pyVersion ($python)" -ForegroundColor Green

# Stap 2: package installeren
Write-Host ""
Write-Host "[2/4] Package installeren (pip install -e .)..." -ForegroundColor Cyan
& $python -m pip install -e $ScriptDir
if ($LASTEXITCODE -ne 0) {
    Fail "pip install is mislukt. Controleer je internetverbinding en Python-installatie."
}
Write-Host "      Package geinstalleerd." -ForegroundColor Green

# Stap 3: OAuth login
Write-Host ""
Write-Host "[3/4] Inloggen bij Google (browser opent)..." -ForegroundColor Cyan
Write-Host "      Log in met je @zwartekraai.nl account en geef toestemming." -ForegroundColor Yellow
& $python -m zk_gchat_mcp setup
if ($LASTEXITCODE -ne 0) {
    Fail "Inloggen is mislukt of afgebroken. Draai het script opnieuw om nogmaals in te loggen."
}
Write-Host "      Ingelogd, token opgeslagen." -ForegroundColor Green

# Stap 4: MCP registreren bij Claude Code
Write-Host ""
Write-Host "[4/4] Registreren bij Claude Code..." -ForegroundColor Cyan
if (-not (Get-Command "claude" -ErrorAction SilentlyContinue)) {
    Fail "De 'claude' CLI is niet gevonden. Installeer Claude Code en draai dit script opnieuw."
}

# Idempotent: bestaande registratie eerst verwijderen (mag falen)
& claude mcp remove zk-gchat 2>$null | Out-Null

& claude mcp add zk-gchat -- $python -m zk_gchat_mcp
if ($LASTEXITCODE -ne 0) {
    Fail "Registreren bij Claude Code is mislukt."
}
Write-Host "      Geregistreerd als 'zk-gchat'." -ForegroundColor Green

Write-Host ""
Write-Host "=== Klaar! ===" -ForegroundColor Green
Write-Host "Herstart Claude Code en vraag bijvoorbeeld: 'wat speelt er in #tech?'" -ForegroundColor Green
