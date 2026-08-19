#!/usr/bin/env python3
"""
Fetch OpenAI's official ChatGPT Voice IP list and convert it to a Mihomo
ipcidr text rule-provider.

Official source:
    https://openai.com/chatgpt-voice.json

Safety properties:
- Requires the response to be valid JSON.
- Extracts only syntactically valid IP addresses / CIDR networks.
- Writes atomically.
- If download or parsing fails, the existing last-known-good rule file is kept.
"""

from __future__ import annotations

import ipaddress
import json
import os
import re
import sys
import tempfile
import urllib.request
from pathlib import Path
from typing import Any, Iterable

SOURCE_URL = "https://openai.com/chatgpt-voice.json"
ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "rules" / "chatgpt-voice.txt"

# Broad token pattern; ipaddress does the final validation.
TOKEN_RE = re.compile(
    r"(?<![0-9A-Fa-f:.])"
    r"(?:"
    r"(?:\d{1,3}\.){3}\d{1,3}(?:/\d{1,2})?"
    r"|"
    r"[0-9A-Fa-f:]{2,}(?:/\d{1,3})?"
    r")"
    r"(?![0-9A-Fa-f:.])"
)


def walk_strings(value: Any) -> Iterable[str]:
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for k, v in value.items():
            yield from walk_strings(k)
            yield from walk_strings(v)
    elif isinstance(value, (list, tuple)):
        for item in value:
            yield from walk_strings(item)


def normalize_network(token: str) -> str | None:
    token = token.strip().strip("[](){}<>,;\"'")
    try:
        if "/" in token:
            network = ipaddress.ip_network(token, strict=False)
        else:
            address = ipaddress.ip_address(token)
            network = ipaddress.ip_network(
                f"{address}/{32 if address.version == 4 else 128}",
                strict=False,
            )
        return str(network)
    except ValueError:
        return None


def fetch_json() -> Any:
    request = urllib.request.Request(
        SOURCE_URL,
        headers={
            "User-Agent": "chatgpt-network-rules/1.0 (+GitHub Actions)",
            "Accept": "application/json, */*",
        },
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        raw = response.read()
    if not raw:
        raise RuntimeError("OpenAI returned an empty response")
    return json.loads(raw.decode("utf-8-sig"))


def extract_networks(data: Any) -> list[str]:
    found: set[str] = set()
    for text in walk_strings(data):
        for match in TOKEN_RE.finditer(text):
            normalized = normalize_network(match.group(0))
            if normalized:
                found.add(normalized)

    if not found:
        raise RuntimeError("Valid JSON contained no IP addresses or CIDR ranges")

    def sort_key(s: str):
        net = ipaddress.ip_network(s)
        return (net.version, int(net.network_address), net.prefixlen)

    return sorted(found, key=sort_key)


def render(networks: list[str]) -> str:
    return (
        "# AUTO-GENERATED. DO NOT EDIT BY HAND.\n"
        "# Official source: https://openai.com/chatgpt-voice.json\n"
        f"# Networks: {len(networks)}\n"
        + "\n".join(networks)
        + "\n"
    )


def atomic_write(path: Path, content: str) -> bool:
    path.parent.mkdir(parents=True, exist_ok=True)
    old = path.read_text(encoding="utf-8") if path.exists() else None
    if old == content:
        print("No rule changes.")
        return False

    fd, tmp_name = tempfile.mkstemp(prefix=path.name + ".", dir=str(path.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as f:
            f.write(content)
        os.replace(tmp_name, path)
    finally:
        if os.path.exists(tmp_name):
            os.unlink(tmp_name)

    print(f"Updated {path.relative_to(ROOT)}")
    return True


def main() -> int:
    try:
        data = fetch_json()
        networks = extract_networks(data)
        print(f"Fetched {len(networks)} network(s) from OpenAI.")
        atomic_write(OUTPUT, render(networks))
        return 0
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        print(
            "Existing last-known-good rules were left untouched.",
            file=sys.stderr,
        )
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
