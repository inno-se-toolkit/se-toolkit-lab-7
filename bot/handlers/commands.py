"""Command handlers that can be used without Telegram."""

from dataclasses import dataclass

from services.api_client import BackendClient, BackendClientError
from services.intent_router import IntentRouter


@dataclass(slots=True)
class CommandHandlers:
    """Application handlers shared by CLI mode and Telegram."""

    backend: BackendClient
    intent_router: IntentRouter

    async def handle_text(self, text: str) -> str:
        """Dispatch a Telegram command or natural-language message."""

        cleaned = text.strip()
        if not cleaned:
            return "Send a command like /help or ask a question about the LMS."

        if cleaned.startswith("/"):
            return await self.handle_command(cleaned)

        return await self.intent_router.route(cleaned)

    async def handle_command(self, text: str) -> str:
        """Dispatch slash commands without any Telegram dependency."""

        parts = text.split()
        command = parts[0].lower()
        args = parts[1:]

        if command == "/start":
            return self.start()
        if command == "/help":
            return self.help()
        if command == "/health":
            return await self.health()
        if command == "/labs":
            return await self.labs()
        if command == "/scores":
            return await self.scores(args)

        return "Unknown command. Use /help to see the supported commands."

    def start(self) -> str:
        """Return the welcome message."""

        return (
            "Welcome to LMS Insight Bot.\n"
            "I can check backend health, list labs, show pass rates, and answer "
            "plain-language questions about LMS data."
        )

    def help(self) -> str:
        """Return the help text."""

        return "\n".join(
            [
                "Available commands:",
                "/start - Show a welcome message",
                "/help - List commands and examples",
                "/health - Check whether the LMS backend is healthy",
                "/labs - List available labs from the LMS backend",
                "/scores <lab> - Show per-task pass rates for a lab",
                "",
                "You can also ask plain-language questions, for example:",
                '"what labs are available?"',
                '"which lab has the lowest pass rate?"',
            ]
        )

    async def health(self) -> str:
        """Check the backend health via /items."""

        try:
            items = await self.backend.get_items()
        except BackendClientError as exc:
            return f"Backend error: {exc}"

        return f"Backend is healthy. {len(items)} items available."

    async def labs(self) -> str:
        """Return the list of labs."""

        try:
            labs = await self.backend.list_labs()
        except BackendClientError as exc:
            return f"Backend error: {exc}"

        if not labs:
            return "No labs were found in the LMS backend yet."

        lines = ["Available labs:"]
        for lab in labs:
            lines.append(f"- {lab['id']} - {lab['title']}")
        return "\n".join(lines)

    async def scores(self, args: list[str]) -> str:
        """Return pass rates for a lab."""

        if not args:
            return "Usage: /scores <lab>. Example: /scores lab-04"

        lab = args[0]
        try:
            rows = await self.backend.get_pass_rates(lab)
        except BackendClientError as exc:
            return f"Backend error: {exc}"

        if not rows:
            return f"No pass-rate data found for {lab}."

        lines = [f"Pass rates for {lab}:"]
        for row in rows:
            lines.append(
                f"- {row['task']}: {row['avg_score']:.1f}% ({row['attempts']} attempts)"
            )
        return "\n".join(lines)
