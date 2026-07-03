"""E2E verificatie van de zk-gchat MCP-server (draai na `python -m zk_gchat_mcp setup`).

Bewijst: list_spaces, read_messages met echte namen, send_message naar een opgegeven
test-space + teruglezen. Gebruik:

    python verify_e2e.py --send-space AAQAhQ3M6Mw
"""
import argparse

from zk_gchat_mcp import chat
from zk_gchat_mcp.auth import token_path, SCOPES


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--send-space", help="space-id voor de send-test (optioneel)")
    p.add_argument("--read-space", default="AAQA0TONJco", help="space-id om te lezen")
    args = p.parse_args()

    print(f"Token: {token_path()}")
    print(f"Scopes ({len(SCOPES)}): " + ", ".join(s.split('/')[-1] for s in SCOPES))
    print("\n[1] list_spaces (top 6)")
    print("\n".join(chat.list_spaces().splitlines()[:7]))

    print(f"\n[2] read_messages op {args.read_space} (laatste 5, MET namen)")
    print(chat.read_messages(args.read_space, limit=5))

    if args.send_space:
        print(f"\n[3] send_message naar {args.send_space}")
        print(chat.send_message(
            args.send_space,
            "E2E verificatie zk-gchat MCP-server. Negeer dit testbericht.",
        ))
        print("\n[4] teruglezen (laatste 2)")
        print(chat.read_messages(args.send_space, limit=2))
    else:
        print("\n[3/4] send-test overgeslagen (geen --send-space)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
