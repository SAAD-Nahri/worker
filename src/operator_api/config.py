from __future__ import annotations

from dataclasses import dataclass
import json
import os
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
CONFIG_DIR = REPO_ROOT / "config"
DEFAULT_OPERATOR_API_CONFIG_PATH = CONFIG_DIR / "operator_api.local.json"


@dataclass(frozen=True)
class OperatorApiConfig:
    bind_host: str
    bind_port: int
    shared_secret: str
    enable_docs: bool = False

    @property
    def base_url(self) -> str:
        return f"http://{self.bind_host}:{self.bind_port}"


def load_operator_api_config(path: Path | None = None) -> OperatorApiConfig:
    config_path = path or DEFAULT_OPERATOR_API_CONFIG_PATH
    payload = _load_payload(config_path)

    bind_host = str(
        payload.get("bind_host")
        or os.environ.get("CONTENT_OPS_OPERATOR_API_HOST")
        or "127.0.0.1"
    ).strip()
    bind_port_value = payload.get("bind_port") or os.environ.get("CONTENT_OPS_OPERATOR_API_PORT") or 8765
    shared_secret = str(
        payload.get("shared_secret")
        or os.environ.get("CONTENT_OPS_OPERATOR_API_SHARED_SECRET")
        or ""
    ).strip()
    enable_docs = _coerce_bool(
        payload.get("enable_docs"),
        default=bool(_coerce_bool(os.environ.get("CONTENT_OPS_OPERATOR_API_ENABLE_DOCS"), default=False)),
    )

    if not shared_secret:
        raise ValueError(
            "Operator API requires a shared secret via config/operator_api.local.json or CONTENT_OPS_OPERATOR_API_SHARED_SECRET."
        )

    try:
        bind_port = int(bind_port_value)
    except (TypeError, ValueError) as exc:
        raise ValueError("Operator API bind_port must be an integer.") from exc

    return OperatorApiConfig(
        bind_host=bind_host,
        bind_port=bind_port,
        shared_secret=shared_secret,
        enable_docs=enable_docs,
    )


def _load_payload(path: Path) -> dict[str, object]:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON in operator API config: {path}") from exc
    if not isinstance(payload, dict):
        raise ValueError("Operator API config root must be a JSON object.")
    return payload


def _coerce_bool(value: object, default: bool = False) -> bool:
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    normalized = str(value).strip().lower()
    if normalized in {"1", "true", "yes", "on"}:
        return True
    if normalized in {"0", "false", "no", "off"}:
        return False
    return default
