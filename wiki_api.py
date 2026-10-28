import re
from urllib.parse import quote

import requests

API_URL = "https://pt.wikipedia.org/api/rest_v1/page/summary/{title}"
HEADERS = {
    "User-Agent": "Letrario/1.0 (jogo de palavras escolar; Flask)",
    "Accept": "application/json",
}
TIMEOUT = 4
MAX_CHARS = 320

_cache = {}


def _shorten(text, limit=MAX_CHARS):
    text = re.sub(r"\s+", " ", text or "").strip()
    if len(text) <= limit:
        return text
    cut = text[:limit]
    last_dot = cut.rfind(". ")
    if last_dot >= 80:
        return cut[: last_dot + 1]
    return cut.rsplit(" ", 1)[0] + "…"


def fetch_summary(display_word):
    title = display_word.strip().capitalize()
    if title in _cache:
        return _cache[title]

    result = None
    try:
        resp = requests.get(
            API_URL.format(title=quote(title, safe="")),
            headers=HEADERS,
            params={"redirect": "true"},
            timeout=TIMEOUT,
        )
        if resp.status_code == 200:
            data = resp.json()
            extract = data.get("extract")
            if data.get("type") == "standard" and extract:
                page_url = data.get("content_urls", {}).get("desktop", {}).get("page")
                result = {
                    "title": data.get("title", title),
                    "extract": _shorten(extract),
                    "url": page_url,
                }
        _cache[title] = result
    except (requests.RequestException, ValueError):
        return None

    return result
