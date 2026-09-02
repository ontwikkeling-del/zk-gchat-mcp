#!/usr/bin/env bash
# install.sh - Installatie zk-gchat MCP-server (macOS/Linux)
# Idempotent: herhaald draaien is veilig.

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

fail() {
    echo ""
    echo "[FOUT] $1"
    echo "Installatie gestopt."
    exit 1
}

echo "=== zk-gchat MCP installatie ==="
echo ""

# Stap 1: python3 aanwezig?
echo "[1/4] Python controleren..."
if ! command -v python3 >/dev/null 2>&1; then
    fail "Python3 is niet gevonden. Installeer Python 3.10+ (bijv. via https://www.python.org/downloads/ of je package manager)."
fi
PY_VERSION="$(python3 --version 2>&1)"
echo "      Gevonden: $PY_VERSION"

# Stap 2: package installeren in een eigen virtuele omgeving
#
# Waarom een venv en niet gewoon `python3 -m pip install`: Python's die via
# Homebrew of een Linux-package-manager binnenkomen zijn "externally managed"
# (PEP 668) en weigeren elke pip-installatie buiten een venv. Dat leverde een
# foutmelding op die de verkeerde kant op wees ("controleer je internetverbinding").
# Een venv werkt op elk systeem en houdt de installatie los van je systeem-Python.
echo ""
echo "[2/4] Package installeren in een virtuele omgeving..."
VENV_DIR="$SCRIPT_DIR/venv"
VENV_PY="$VENV_DIR/bin/python3"

if [ ! -x "$VENV_PY" ]; then
    if ! python3 -m venv "$VENV_DIR"; then
        fail "Aanmaken van de virtuele omgeving is mislukt. Op Debian/Ubuntu moet je mogelijk eerst 'python3-venv' installeren."
    fi
fi

"$VENV_PY" -m pip install --quiet --upgrade pip >/dev/null 2>&1 || true

if ! "$VENV_PY" -m pip install -e "$SCRIPT_DIR"; then
    fail "pip install is mislukt. Controleer je internetverbinding en Python-installatie."
fi
echo "      Package geinstalleerd in $VENV_DIR"

# Stap 3: OAuth login
echo ""
echo "[3/4] Inloggen bij Google (browser opent)..."
echo "      Log in met je @zwartekraai.nl account en geef toestemming."
echo "      LET OP: laat het browsertabblad open tot je ziet dat het gelukt is."
if ! "$VENV_PY" -m zk_gchat_mcp setup; then
    fail "Inloggen is mislukt of afgebroken. Draai het script opnieuw om nogmaals in te loggen."
fi
echo "      Ingelogd, token opgeslagen."

# Stap 4: MCP registreren bij Claude Code
echo ""
echo "[4/4] Registreren bij Claude Code..."
if ! command -v claude >/dev/null 2>&1; then
    fail "De 'claude' CLI is niet gevonden. Installeer Claude Code en draai dit script opnieuw."
fi

# Idempotent: bestaande registratie eerst verwijderen (mag falen)
claude mcp remove zk-gchat >/dev/null 2>&1 || true

# Het volledige pad naar de venv-python, want een kale `python3` vindt het
# package niet: het staat in de venv en niet in de systeem-Python.
if ! claude mcp add zk-gchat -- "$VENV_PY" -m zk_gchat_mcp; then
    fail "Registreren bij Claude Code is mislukt."
fi
echo "      Geregistreerd als 'zk-gchat'."

echo ""
echo "=== Klaar! ==="
echo "Herstart Claude Code en vraag bijvoorbeeld: 'wat speelt er in #tech?'"
