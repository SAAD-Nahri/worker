# Config Examples

This folder holds safe example config files for live operator setup.

## Rule

Copy example files into `.local.json` files and keep the real values local.

Recommended filenames:

1. `config/wordpress_rest_config.local.json`
2. `config/facebook_graph_config.local.json`
3. `config/openai_provider_config.local.json`
4. `config/operator_api.local.json`

Those filenames are already ignored by git.

## Example Files

1. [wordpress_rest_config.example.json](C:/Users/Administrator/OneDrive/Documents/co_ma/config/wordpress_rest_config.example.json)
2. [facebook_graph_config.example.json](C:/Users/Administrator/OneDrive/Documents/co_ma/config/facebook_graph_config.example.json)
3. [openai_provider_config.example.json](C:/Users/Administrator/OneDrive/Documents/co_ma/config/openai_provider_config.example.json)
4. [operator_api_config.example.json](C:/Users/Administrator/OneDrive/Documents/co_ma/config/operator_api_config.example.json)

## OpenAI Notes

The OpenAI quality layer prefers:

1. `OPENAI_API_KEY`

The ignored file:

1. `config/openai_provider_config.local.json`

is still supported as a fallback and may also carry:

1. `model`
2. `timeout_seconds`

Precedence rules:

1. `OPENAI_API_KEY` overrides file `api_key`,
2. file `model` and `timeout_seconds` still apply when present,
3. defaults are `gpt-5.4-mini` and `30`.

The OpenAI path is optional. If it is missing or invalid, the draft micro-skill CLI falls back to the heuristic provider and the social refinement CLI reports a safe fallback reason without changing the selected package.

## Operator API Notes

The internal operator API reads `config/operator_api.local.json` by default.

Use [operator_api_config.example.json](C:/Users/Administrator/OneDrive/Documents/co_ma/config/operator_api_config.example.json) as the safe template, then copy it to the `.local.json` filename and set:

1. `bind_host`
2. `bind_port`
3. `shared_secret`
4. `enable_docs`

Important:

1. `127.0.0.1` is correct for local same-host validation,
2. if WordPress is hosted elsewhere, the plugin must use a reachable HTTPS operator-API URL instead of worker localhost,
3. example reverse-proxy baselines live in [deploy/nginx/content-ops-operator-api.nginx.example](C:/Users/Administrator/OneDrive/Documents/co_ma/deploy/nginx/content-ops-operator-api.nginx.example) and [deploy/caddy/content-ops-operator-api.Caddyfile.example](C:/Users/Administrator/OneDrive/Documents/co_ma/deploy/caddy/content-ops-operator-api.Caddyfile.example).

## Do Not Do

1. do not commit live credentials,
2. do not rename live config files to the example filenames,
3. do not paste secrets into docs or terminal transcripts.
