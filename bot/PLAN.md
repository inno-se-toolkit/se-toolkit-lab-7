This lab will be implemented as a small client application that keeps the core
business logic separate from Telegram. The main architectural choice is a
testable handler layer: every command and natural-language request is processed
by Python functions that return plain text. Telegram becomes only a transport
adapter. That gives us one execution path for local `--test` checks, future
unit tests, and the real bot runtime.

Task 1 focuses on the scaffold. The `bot/` directory contains an entry point,
configuration loading, handler modules, and service clients. Configuration is
loaded from environment variables, with support for `.env.bot.secret` in the
repository root. The entry point supports `uv run bot.py --test "/start"` so
the autochecker can run the bot without Telegram access.

Task 2 adds backend integration. A dedicated API client will wrap the LMS
backend endpoints behind descriptive methods such as `get_items()` and
`get_pass_rates(lab)`. Command handlers will call this client and format
friendly responses for `/health`, `/labs`, and `/scores <lab>`. Errors will be
converted into user-facing messages that still preserve the actual failure
reason, for example connection refused or HTTP 502.

Task 3 adds natural-language routing powered by an OpenAI-compatible LLM. The
bot will expose all nine backend endpoints as tool schemas. The router will
send the user message, system instructions, and tool definitions to the LLM,
execute returned tool calls, feed the results back into the conversation, and
request the final answer. This enables both single-step and multi-step queries
without hardcoded keyword routing. Telegram keyboard buttons will be added for
discoverability, while the same plain-text router stays usable in `--test`
mode.

Task 4 finishes deployment. The bot gets its own `Dockerfile`, a `bot` service
is added to `docker-compose.yml`, and the README is updated with configuration,
local usage, and VM deployment instructions. Inside Docker the bot will talk to
the backend via `http://backend:8000`, while the LLM API will be reached via
`host.docker.internal` so the separate Qwen proxy remains accessible from the
container. Final verification includes local `uv run` checks, Docker compose
startup, and VM validation against the real backend and LLM.
