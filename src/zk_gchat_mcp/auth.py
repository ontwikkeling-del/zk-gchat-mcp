"""OAuth per gebruiker. Token lokaal opgeslagen, gedeelde desktop-client meegeleverd.

Token-locatie:
  Windows : %APPDATA%\\zk-gchat\\token.json
  mac/lin : ~/.config/zk-gchat/token.json

De gedeelde OAuth desktop-client ligt naast deze module als client_secret.json
(een desktop/installed-app client; de secret daarvan is geen echt geheim).
"""
from __future__ import annotations

import os
import sys
import json
from pathlib import Path

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# Gesplitste scopes: lezen != sturen. Namen via members.list (chat.memberships.readonly,
# geen extra API-enable nodig) met People API (directory.readonly) als fallback.
SCOPES = [
    "https://www.googleapis.com/auth/chat.spaces.readonly",
    "https://www.googleapis.com/auth/chat.spaces.create",
    "https://www.googleapis.com/auth/chat.messages.readonly",
    "https://www.googleapis.com/auth/chat.messages.create",
    "https://www.googleapis.com/auth/chat.memberships",
    "https://www.googleapis.com/auth/directory.readonly",
    # Nodig voor bijlagen uploaden naar Chat (media.upload); alleen files die
    # deze app zelf aanmaakt/upload - geen toegang tot bestaande Drive-bestanden.
    "https://www.googleapis.com/auth/drive.file",
    # "Alles gelezen" in de Chat-UI zelf (spaceReadState PATCH). PAS ACTIVEREN
    # (uncomment) direct vóór een re-auth door Dennis (dennis@zwartekraai.nl!):
    # een scope in deze lijst die NIET in het huidige token zit, laat de
    # token-refresh falen met invalid_scope en breekt ALLE chat-calls.
    # "https://www.googleapis.com/auth/chat.users.readstate",
]

_PKG_DIR = Path(__file__).resolve().parent
CLIENT_SECRET_PATH = Path(
    os.getenv("ZK_GCHAT_CLIENT_SECRET", str(_PKG_DIR / "client_secret.json"))
)


def _config_dir() -> Path:
    if sys.platform.startswith("win"):
        base = Path(os.getenv("APPDATA", str(Path.home() / "AppData" / "Roaming")))
    else:
        base = Path(os.getenv("XDG_CONFIG_HOME", str(Path.home() / ".config")))
    d = base / "zk-gchat"
    d.mkdir(parents=True, exist_ok=True)
    return d


def token_path() -> Path:
    return Path(os.getenv("ZK_GCHAT_TOKEN", str(_config_dir() / "token.json")))


def names_cache_path() -> Path:
    return _config_dir() / "names_cache.json"


def load_credentials(interactive: bool = False) -> Credentials:
    """Laad token, refresh waar nodig. interactive=True triggert browser-login
    als er geen (geldig) token is. interactive=False gooit een nette fout."""
    tp = token_path()
    creds: Credentials | None = None

    if tp.exists():
        creds = Credentials.from_authorized_user_file(str(tp), SCOPES)

    if creds and creds.valid:
        return creds

    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
        tp.write_text(creds.to_json(), encoding="utf-8")
        return creds

    if not interactive:
        raise RuntimeError(
            "Geen geldig Google Chat token. Run eerst:  python -m zk_gchat_mcp setup"
        )

    if not CLIENT_SECRET_PATH.exists():
        raise RuntimeError(
            f"client_secret.json niet gevonden op {CLIENT_SECRET_PATH}. "
            "Zet de gedeelde desktop-client daar neer of via env ZK_GCHAT_CLIENT_SECRET."
        )

    flow = InstalledAppFlow.from_client_secrets_file(str(CLIENT_SECRET_PATH), SCOPES)
    creds = flow.run_local_server(port=0)
    tp.write_text(creds.to_json(), encoding="utf-8")
    return creds


def run_setup() -> int:
    """Eenmalige browser-login. Returnt exit code."""
    try:
        creds = load_credentials(interactive=True)
    except Exception as e:  # noqa: BLE001
        print(f"Login mislukt: {e}", file=sys.stderr)
        return 1
    acct = ""
    try:
        acct = json.loads(creds.to_json()).get("account", "")
    except Exception:  # noqa: BLE001
        pass
    print(f"Ingelogd en token opgeslagen op {token_path()}"
          + (f" (account: {acct})" if acct else ""))
    return 0
