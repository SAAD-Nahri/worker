from __future__ import annotations

from dataclasses import dataclass
import json
import os
from pathlib import Path
from typing import Any, Callable, Mapping

from source_engine.cleaner import clean_text


REPO_ROOT = Path(__file__).resolve().parents[2]
CONFIG_DIR = REPO_ROOT / "config"
DEFAULT_OPENAI_PROVIDER_CONFIG_PATH = CONFIG_DIR / "openai_provider_config.local.json"
DEFAULT_OPENAI_MODEL = "gpt-5.4-mini"
DEFAULT_OPENAI_TIMEOUT_SECONDS = 30


@dataclass(frozen=True)
class OpenAiProviderConfig:
    api_key: str
    model: str = DEFAULT_OPENAI_MODEL
    timeout_seconds: int = DEFAULT_OPENAI_TIMEOUT_SECONDS

    def __post_init__(self) -> None:
        api_key = clean_text(self.api_key)
        model = clean_text(self.model) or DEFAULT_OPENAI_MODEL
        if not api_key:
            raise ValueError(
                "OpenAI provider requires OPENAI_API_KEY or config/openai_provider_config.local.json with api_key."
            )
        if self.timeout_seconds <= 0:
            raise ValueError("OpenAI provider timeout_seconds must be greater than zero.")
        object.__setattr__(self, "api_key", api_key)
        object.__setattr__(self, "model", model)


@dataclass(frozen=True)
class OpenAiPromptRequest:
    task_name: str
    instructions: str
    input_text: str
    max_output_tokens: int


OpenAiResponseCreator = Callable[[OpenAiPromptRequest, OpenAiProviderConfig], str]


def load_openai_provider_config(
    path: Path | None = None,
    environ: Mapping[str, str] | None = None,
) -> OpenAiProviderConfig:
    env = environ or os.environ
    config_path = path or DEFAULT_OPENAI_PROVIDER_CONFIG_PATH
    payload = _load_payload(config_path)

    api_key = clean_text(env.get("OPENAI_API_KEY", "")) or clean_text(str(payload.get("api_key", "")))
    model = clean_text(str(payload.get("model", DEFAULT_OPENAI_MODEL))) or DEFAULT_OPENAI_MODEL
    timeout_value = payload.get("timeout_seconds", DEFAULT_OPENAI_TIMEOUT_SECONDS)
    try:
        timeout_seconds = int(timeout_value)
    except (TypeError, ValueError) as exc:
        raise ValueError("OpenAI provider timeout_seconds must be an integer.") from exc

    return OpenAiProviderConfig(
        api_key=api_key,
        model=model,
        timeout_seconds=timeout_seconds,
    )


def request_openai_output(
    request: OpenAiPromptRequest,
    config: OpenAiProviderConfig,
    response_creator: OpenAiResponseCreator | None = None,
) -> str:
    creator = response_creator or _default_response_creator
    output_text = clean_text(creator(request, config))
    if not output_text:
        raise RuntimeError(f"OpenAI returned no text for task {request.task_name}.")
    return output_text


def _load_payload(path: Path) -> dict[str, object]:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"OpenAI provider config is not valid JSON: {path}") from exc
    if not isinstance(payload, dict):
        raise ValueError("OpenAI provider config must contain a JSON object.")
    return payload


def _default_response_creator(
    request: OpenAiPromptRequest,
    config: OpenAiProviderConfig,
) -> str:
    try:
        from openai import OpenAI
    except ImportError as exc:
        raise RuntimeError(
            "OpenAI SDK is not installed. Install the optional openai dependency to enable provider-backed quality."
        ) from exc

    client = OpenAI(
        api_key=config.api_key,
        timeout=float(config.timeout_seconds),
    )
    response = client.responses.create(
        model=config.model,
        instructions=request.instructions,
        input=request.input_text,
        max_output_tokens=request.max_output_tokens,
    )
    output_text = _extract_response_text(response)
    if not output_text:
        raise RuntimeError(f"OpenAI response did not include text for task {request.task_name}.")
    return output_text


def _extract_response_text(response: Any) -> str:
    direct = clean_text(str(getattr(response, "output_text", "") or ""))
    if direct:
        return direct
    if isinstance(response, dict):
        return _extract_response_text_from_mapping(response)

    output_items = getattr(response, "output", None)
    if output_items:
        collected: list[str] = []
        for item in output_items:
            content_items = getattr(item, "content", None) or []
            for content_item in content_items:
                text_value = clean_text(str(getattr(content_item, "text", "") or ""))
                if text_value:
                    collected.append(text_value)
        if collected:
            return "\n".join(collected)
    return ""


def _extract_response_text_from_mapping(response: Mapping[str, Any]) -> str:
    direct = clean_text(str(response.get("output_text", "") or ""))
    if direct:
        return direct
    output_items = response.get("output")
    if not isinstance(output_items, list):
        return ""
    collected: list[str] = []
    for item in output_items:
        if not isinstance(item, Mapping):
            continue
        content_items = item.get("content")
        if not isinstance(content_items, list):
            continue
        for content_item in content_items:
            if not isinstance(content_item, Mapping):
                continue
            text_value = clean_text(str(content_item.get("text", "") or ""))
            if text_value:
                collected.append(text_value)
    return "\n".join(collected)
