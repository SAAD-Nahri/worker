from __future__ import annotations

import uvicorn

from operator_api.app import build_app
from operator_api.config import load_operator_api_config


def main() -> int:
    config = load_operator_api_config()
    app = build_app(config=config)
    uvicorn.run(app, host=config.bind_host, port=config.bind_port)
    return 0
