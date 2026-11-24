"""Unhandled errors to a log group topic, shared by several bots (one topic per bot)."""

from __future__ import annotations

import html
import logging
import traceback
from typing import Any

logger = logging.getLogger(__name__)

MAX_MESSAGE = 4000


def format_error(name: str, error: BaseException, context: str | None = None, lines: int = 8) -> str:
    """The error as Telegram HTML; everything is escaped, the traceback trimmed to its last lines."""
    trace = "".join(traceback.format_exception(type(error), error, error.__traceback__)).strip().splitlines()[-lines:]
    parts = [f"🚨 <b>{html.escape(name)}</b>"]
    if context:
        parts.append(f"<b>Context:</b> {html.escape(context[:600])}")
    parts.append(f"<b>{html.escape(type(error).__name__)}:</b> <code>{html.escape(str(error)[:600])}</code>")
    parts.append(f"<pre>{html.escape(chr(10).join(trace))}</pre>")
    text = "\n\n".join(parts)
    return text if len(text) <= MAX_MESSAGE else text[: MAX_MESSAGE - 7] + "…</pre>"


def chat_id(value: int | str | None) -> int | None:
    """A group id as Telegram wants it: `1234567890` (as copied from some clients) → `-1001234567890`."""
    if value in (None, "", 0, "0"):
        return None
    number = int(value)
    return int(f"-100{number}") if number > 0 else number


normalize_chat_id = chat_id


class ErrorReporter:
    """Posts errors to `chat_id` (and topic `thread_id`); without a chat it only logs them."""

    def __init__(self, name: str, chat_id: int | str | None = None, thread_id: int | None = None) -> None:
        self.name = name
        self.chat_id = normalize_chat_id(chat_id)
        self.thread_id = thread_id or None

    async def report(self, bot: Any, error: BaseException, context: str | None = None) -> bool:
        logger.error("%s: %s", context or "Unhandled error", error, exc_info=error)
        if not self.chat_id:
            return False
        try:
            await bot.send_message(
                chat_id=self.chat_id,
                message_thread_id=self.thread_id,
                text=format_error(self.name, error, context),
                parse_mode="HTML",
            )
            return True
        except Exception as failure:  # reporting must never raise
            logger.error("Could not post the error to the log group: %s", failure)
            return False

    def handler(self):
        """An error handler for `Application.add_error_handler`. The context names the update type
        and chat id only, so no message contents end up in the log group."""

        async def on_error(update: object, context: Any) -> None:
            where = None
            chat = getattr(update, "effective_chat", None)
            if update is not None:
                where = type(update).__name__ + (f" in chat {chat.id}" if chat else "")
            await self.report(context.bot, context.error, where)

        return on_error
