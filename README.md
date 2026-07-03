# zk-gchat MCP-server

MCP-server waarmee je vanuit Claude Code in Google Chat kunt **lezen** en **sturen**. Elke Zwarte Kraai collega draait deze lokaal met een eigen Google-account (per-gebruiker OAuth). Berichten die je verstuurt komen dus vanuit jouw eigen account.

Niet-technische installatiehandleiding: zie `HANDLEIDING.md`.

## Mapstructuur

```
GoogleChatMCP/
  install.ps1                       # Installer Windows
  install.sh                        # Installer macOS/Linux
  README.md                         # Dit bestand
  HANDLEIDING.md                    # Non-technische uitleg voor collega's
  .gitignore
  pyproject.toml                    # Package-definitie (door dev-agent)
  src/
    zk_gchat_mcp/
      client_secret.json            # Gedeelde OAuth desktop-client (niet-geheim)
      ...                           # Python-code (door dev-agent)
```

## Vereisten

- Python 3.10 of hoger
- Claude Code met de `claude` CLI in je PATH
- Een `@zwartekraai.nl` Google-account

## Installeren (handmatig)

De installer doet dit automatisch. Wil je het zelf stap voor stap doen, dan vanuit de tool-dir:

```bash
# 1. Package installeren
pip install -e .

# 2. Eenmalig inloggen (browser opent)
python -m zk_gchat_mcp setup

# 3. Registreren bij Claude Code
claude mcp add zk-gchat -- python -m zk_gchat_mcp
```

Op macOS/Linux gebruik je `python3` in plaats van `python`.

De server draait via stdio en wordt door Claude Code zelf gestart met `python -m zk_gchat_mcp`. Je hoeft de server niet handmatig te starten.

## OAuth-scopes

De server vraagt de volgende vier scopes:

| Scope | Waarvoor |
|-------|----------|
| `chat.spaces.readonly` | Lezen welke spaces/kanalen er zijn waar jij in zit |
| `chat.messages.readonly` | Berichten in die spaces lezen |
| `chat.messages.create` | Berichten versturen namens jou |
| `directory.readonly` | Namen van collega's opzoeken zodat afzenders leesbaar zijn in plaats van interne ID's |

## Token-locatie

Na het inloggen wordt je token lokaal opgeslagen:

- Windows: `%APPDATA%\zk-gchat\token.json`
- macOS/Linux: `~/.config/zk-gchat/token.json`

Dit token blijft op jouw machine. **Tokens komen nooit in git** (zie `.gitignore`). Deel je `token.json` met niemand: het geeft toegang tot jouw Google Chat.

## Opnieuw inloggen / updaten

Token verlopen of een nieuwe scope nodig? Draai gewoon opnieuw:

```bash
python -m zk_gchat_mcp setup
```

Dit overschrijft het bestaande token met een vers token. Na een code-update volstaat meestal `git pull` plus opnieuw `pip install -e .`.

## Bekende beperking

Berichten die via `send_message` worden verstuurd krijgen automatisch een `🤖`-prefix. Zo is voor iedereen in de chat zichtbaar dat het bericht via de tool (Claude) is verstuurd en niet handmatig getypt.
