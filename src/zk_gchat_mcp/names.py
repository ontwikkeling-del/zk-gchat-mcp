"""Resolve Chat user-ids (users/<id>) naar echte namen.

Twee bronnen, in deze volgorde:
  1. Per-space members.list (scope chat.memberships.readonly) - geen extra API-enable nodig.
     Bij read_messages weten we de space, dus we cachen daar de id->naam map.
  2. People API people.get (scope directory.readonly) - fallback per onbekende id;
     vereist dat de People API aanstaat in het project.
  3. Lukt beide niet, val terug op het ruwe id.

Cache (id -> naam) staat in geheugen en op disk.
"""
from __future__ import annotations

import json

from googleapiclient.discovery import build

from .auth import names_cache_path


class NameResolver:
    def __init__(self, creds, chat_service=None):
        self._creds = creds
        self._chat = chat_service  # hergebruik de chat-service voor members.list
        self._people = None  # lazy
        self._primed_spaces: set[str] = set()
        self._cache: dict[str, str] = {}
        self._path = names_cache_path()
        if self._path.exists():
            try:
                self._cache = json.loads(self._path.read_text(encoding="utf-8"))
            except Exception:  # noqa: BLE001
                self._cache = {}

    def _save(self) -> None:
        try:
            self._path.write_text(
                json.dumps(self._cache, ensure_ascii=False), encoding="utf-8"
            )
        except Exception:  # noqa: BLE001
            pass

    def prime_space(self, space_name: str) -> None:
        """Haal de members van een space op en cache hun id->naam. Stil falen mag."""
        if not self._chat or space_name in self._primed_spaces:
            return
        self._primed_spaces.add(space_name)
        token = None
        try:
            while True:
                resp = self._chat.spaces().members().list(
                    parent=space_name, pageSize=100, pageToken=token
                ).execute()
                for m in resp.get("memberships", []):
                    u = m.get("member", {})
                    name = u.get("name")
                    disp = u.get("displayName")
                    if name and disp:
                        self._cache.setdefault(name, disp)
                token = resp.get("nextPageToken")
                if not token:
                    break
            self._save()
        except Exception:  # noqa: BLE001
            pass  # geen memberships-scope of geen toegang -> fallback regelt het

    def _people_lookup(self, resource: str) -> str | None:
        uid = resource.split("/", 1)[-1]
        try:
            if self._people is None:
                self._people = build(
                    "people", "v1", credentials=self._creds, cache_discovery=False
                )
            person = self._people.people().get(
                resourceName=f"people/{uid}", personFields="names"
            ).execute()
            names = person.get("names") or []
            if names:
                return names[0].get("displayName")
        except Exception:  # noqa: BLE001
            return None
        return None

    def resolve(self, sender: dict | None) -> str:
        if not sender:
            return "onbekend"
        if sender.get("displayName"):
            return sender["displayName"]
        res = sender.get("name", "")  # users/123...
        if not res:
            return "onbekend"
        if res in self._cache:
            return self._cache[res]
        label = self._people_lookup(res) or res
        self._cache[res] = label
        self._save()
        return label
