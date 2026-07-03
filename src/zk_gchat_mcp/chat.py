"""Google Chat API-laag: spaces lijsten, berichten lezen, bericht sturen.

Werkt namens de ingelogde gebruiker (user-OAuth). Afzendernamen worden geresolved
via NameResolver. Berichten van deze tool krijgen een robot-prefix.
"""
from __future__ import annotations

from datetime import datetime, timezone, timedelta

from googleapiclient.discovery import build

from .auth import load_credentials
from .names import NameResolver

ROBOT_PREFIX = "\U0001F916 "  # 🤖


def _services():
    creds = load_credentials(interactive=False)
    chat = build("chat", "v1", credentials=creds, cache_discovery=False)
    return chat, NameResolver(creds, chat_service=chat)


def _space_label(space: dict) -> str:
    if space.get("displayName"):
        return space["displayName"]
    if space.get("spaceType") == "DIRECT_MESSAGE":
        return "DM"
    return space.get("name", "?")


def _fmt_time(iso: str | None) -> str:
    if not iso:
        return "?"
    try:
        dt = datetime.fromisoformat(iso.replace("Z", "+00:00")).astimezone()
        return dt.strftime("%d-%m-%Y %H:%M")
    except Exception:  # noqa: BLE001
        return iso


def _all_spaces(chat) -> list[dict]:
    spaces, token = [], None
    while True:
        resp = chat.spaces().list(pageSize=100, pageToken=token).execute()
        spaces.extend(resp.get("spaces", []))
        token = resp.get("nextPageToken")
        if not token:
            break
    return spaces


def _messages(chat, space_name: str, limit: int, since: datetime | None) -> list[dict]:
    msgs, token = [], None
    while len(msgs) < limit:
        resp = chat.spaces().messages().list(
            parent=space_name,
            pageSize=min(100, limit),
            orderBy="createTime DESC",
            pageToken=token,
        ).execute()
        for m in resp.get("messages", []):
            ct = m.get("createTime")
            if since and ct:
                dt = datetime.fromisoformat(ct.replace("Z", "+00:00"))
                if dt < since:
                    return msgs
            msgs.append(m)
            if len(msgs) >= limit:
                break
        token = resp.get("nextPageToken")
        if not token:
            break
    return msgs


def _normalize_space(space_id: str) -> str:
    return space_id if space_id.startswith("spaces/") else f"spaces/{space_id}"


# ---- publieke functies (gebruikt door de MCP-tools) ----

def list_spaces() -> str:
    chat, _ = _services()
    spaces = _all_spaces(chat)
    lines = [f"{len(spaces)} spaces waar je lid van bent:"]
    rows = []
    for sp in spaces:
        last = _messages(chat, sp["name"], limit=1, since=None)
        raw = last[0].get("createTime") if last else ""
        when = _fmt_time(raw) if last else "-"
        sid = sp["name"].replace("spaces/", "")
        rows.append((raw or "", _space_label(sp), when, sid))
    rows.sort(key=lambda r: r[0], reverse=True)  # sorteer op echte ISO-tijd
    for _raw, label, when, sid in rows:
        lines.append(f"  {label:<35} laatste: {when:<18} id={sid}")
    return "\n".join(lines)


def read_messages(space_id: str, limit: int = 30, hours: int | None = None) -> str:
    chat, resolver = _services()
    name = _normalize_space(space_id)
    space = chat.spaces().get(name=name).execute()
    since = None
    if hours:
        since = datetime.now(timezone.utc) - timedelta(hours=hours)
    msgs = _messages(chat, name, limit=limit, since=since)
    head = f"=== {_space_label(space)}  ({name}) ==="
    if not msgs:
        return head + "\n  (geen berichten)"
    resolver.prime_space(name)  # cache id->naam via members.list (best effort)
    lines = [head]
    for m in reversed(msgs):  # oudste eerst -> leest als gesprek
        who = resolver.resolve(m.get("sender"))
        when = _fmt_time(m.get("createTime"))
        text = (m.get("text") or m.get("formattedText") or "").replace("\n", " ").strip()
        if not text:
            text = "[geen tekst / card of bijlage]"
        lines.append(f"  [{when}] {who}: {text}")
    return "\n".join(lines)


def create_space(display_name: str, member_emails: list[str] | None = None,
                 description: str | None = None) -> str:
    chat, _ = _services()
    body: dict = {
        "space": {
            "displayName": display_name,
            "spaceType": "SPACE",
        }
    }
    if description:
        body["space"]["spaceDetails"] = {"description": description}
    if member_emails:
        body["memberships"] = [
            {"member": {"name": f"users/{email}", "type": "HUMAN"}}
            for email in member_emails
        ]
    result = chat.spaces().setup(body=body).execute()
    name = result.get("name", "?")
    return (f"Space '{display_name}' aangemaakt: {name} "
            f"(id={name.replace('spaces/', '')}), "
            f"{len(member_emails or [])} leden uitgenodigd naast jezelf.")


def add_members(space_id: str, member_emails: list[str]) -> str:
    chat, _ = _services()
    name = _normalize_space(space_id)
    results = []
    for email in member_emails:
        try:
            chat.spaces().members().create(
                parent=name,
                body={"member": {"name": f"users/{email}", "type": "HUMAN"}},
            ).execute()
            results.append(f"  OK: {email}")
        except Exception as e:  # noqa: BLE001
            results.append(f"  FOUT: {email}: {e}")
    return f"Leden toevoegen aan {name}:\n" + "\n".join(results)


def send_message(space_id: str, text: str, thread_key: str | None = None) -> str:
    chat, _ = _services()
    name = _normalize_space(space_id)
    body = {"text": f"{ROBOT_PREFIX}{text}"}
    kwargs = {"parent": name, "body": body}
    if thread_key:
        kwargs["threadKey"] = thread_key
        kwargs["messageReplyOption"] = "REPLY_MESSAGE_FALLBACK_TO_NEW_THREAD"
    result = chat.spaces().messages().create(**kwargs).execute()
    return f"Verzonden naar {name}. Message ID: {result.get('name', 'onbekend')}"
