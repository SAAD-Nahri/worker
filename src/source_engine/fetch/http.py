from __future__ import annotations

import gzip
import re
from urllib.parse import urlparse
from urllib.request import Request


USER_AGENT = "content-ops-source-engine/0.1 (+https://local.project)"
MAX_RESPONSE_BYTES = 750_000
CHARSET_RE = re.compile(r"charset=([^\s;]+)", re.IGNORECASE)


def build_request(url: str) -> Request:
    return Request(
        url,
        headers={
            "User-Agent": USER_AGENT,
            "Accept-Encoding": "gzip",
        },
    )


def read_response_payload(response, max_bytes: int = MAX_RESPONSE_BYTES) -> bytes:
    payload = response.read(max_bytes + 1)
    if len(payload) > max_bytes:
        raise ValueError(f"Response exceeded max size limit of {max_bytes} bytes.")

    content_encoding = (response.getheader("Content-Encoding") or "").lower()
    if content_encoding == "gzip" or payload.startswith(b"\x1f\x8b"):
        return gzip.decompress(payload)
    return payload


def decode_response_text(payload: bytes, content_type: str | None) -> str:
    charset = response_charset(content_type) or "utf-8"
    try:
        return payload.decode(charset, errors="replace")
    except LookupError:
        return payload.decode("utf-8", errors="replace")


def response_charset(content_type: str | None) -> str | None:
    if not content_type:
        return None
    match = CHARSET_RE.search(content_type)
    if match is None:
        return None
    return match.group(1).strip("\"' ")


def url_matches_domain(url: str, domain: str) -> bool:
    hostname = (urlparse(url).hostname or "").lower()
    normalized_domain = domain.lower().lstrip(".")
    return bool(hostname) and (
        hostname == normalized_domain or hostname.endswith(f".{normalized_domain}")
    )
