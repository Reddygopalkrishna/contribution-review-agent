"""Read-only GitHub REST helpers reserved for the optional triage command."""

from __future__ import annotations

import json
from urllib.request import Request, urlopen


def get_json(url: str, token: str | None = None) -> object:
    """Fetch public GitHub JSON with an optional read-only bearer token."""
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "contribution-review-agent"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    with urlopen(Request(url, headers=headers), timeout=20) as response:  # nosec B310: GitHub API URL is caller-controlled only by CLI repo parsing.
        return json.load(response)
