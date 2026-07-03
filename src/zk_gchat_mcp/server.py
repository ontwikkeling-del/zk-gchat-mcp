"""FastMCP stdio-server: stelt 5 Google Chat tools beschikbaar in Claude Code.

Start/stopt met de Claude Code-sessie (stdio). Geen permanente achtergronddienst.
"""
from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from . import chat

mcp = FastMCP("zk-gchat")


@mcp.tool()
def list_spaces() -> str:
    """Lijst alle Google Chat spaces/DM's waar je lid van bent, met de tijd van het
    laatste bericht. Gebruik dit om space-id's te vinden voor read_messages/send_message."""
    return chat.list_spaces()


@mcp.tool()
def read_messages(space_id: str, limit: int = 30, hours: int | None = None) -> str:
    """Lees recente berichten uit een Google Chat space.

    space_id: het id of de volledige resource name (bv. 'AAQA0TONJco' of 'spaces/AAQA0TONJco').
    limit: max aantal berichten (default 30).
    hours: optioneel - alleen berichten van de laatste N uur.
    Toont per bericht tijd, afzendernaam en tekst (oudste eerst)."""
    return chat.read_messages(space_id, limit=limit, hours=hours)


@mcp.tool()
def create_space(display_name: str, member_emails: list[str] | None = None,
                 description: str | None = None) -> str:
    """Maak een nieuwe Google Chat space aan (type SPACE) met jou als eigenaar.

    display_name: naam van de space. member_emails: optionele lijst e-mailadressen
    om direct als lid uit te nodigen. description: optionele beschrijving.
    Gebruik dit alleen na bevestiging van de gebruiker over naam en leden."""
    return chat.create_space(display_name, member_emails=member_emails,
                             description=description)


@mcp.tool()
def add_members(space_id: str, member_emails: list[str]) -> str:
    """Voeg leden toe aan een bestaande Google Chat space op basis van e-mailadres.

    space_id: id of resource name van de space. member_emails: lijst e-mailadressen.
    Gebruik dit alleen na bevestiging van de gebruiker."""
    return chat.add_members(space_id, member_emails)


@mcp.tool()
def send_message(space_id: str, text: str, thread_key: str | None = None) -> str:
    """Stuur een bericht naar een Google Chat space namens jezelf.

    Het bericht krijgt automatisch een robot-prefix zodat duidelijk is dat het via de tool
    is gestuurd. space_id: id of resource name. thread_key: optioneel om in een thread te
    antwoorden. Gebruik dit alleen na bevestiging van de gebruiker over inhoud en doel-space."""
    return chat.send_message(space_id, text, thread_key=thread_key)


def run() -> None:
    mcp.run()  # stdio transport
