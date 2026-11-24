"""Translations as JSON files: `res/strings/en.json` holds every key, other languages
(`res/strings/de.json`, …) may leave keys out and fall back to English."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterable


class Strings:
    def __init__(self, directory: str | Path, default: str = "en") -> None:
        self.directory = Path(directory)
        self.default = default
        self.table: dict[str, dict[str, str]] = {
            path.stem: json.loads(path.read_text(encoding="utf-8")) for path in sorted(self.directory.glob("*.json"))
        }
        if default not in self.table:
            raise FileNotFoundError(f"{self.directory / (default + '.json')} is missing")

    @property
    def languages(self) -> tuple[str, ...]:
        return tuple(self.table)

    def lang(self, code: str | None) -> str:
        """`de-AT` → `de` when there is a de.json, otherwise the default language."""
        base = (code or "").lower().replace("_", "-").split("-")[0]
        return base if base in self.table else self.default

    def lang_of(self, user: Any) -> str:
        """The language of a Telegram user (anything with `language_code`, or None)."""
        return self.lang(getattr(user, "language_code", None))

    def has(self, key: str, lang: str | None = None) -> bool:
        return key in self.table.get(lang or self.default, {})

    def get(self, lang: str | None, key: str, **values: Any) -> str:
        """The text for `key` in `lang`, falling back to the default language; `{name}` placeholders
        are filled from `values`. A key missing everywhere raises KeyError."""
        text = self.table.get(lang or self.default, {}).get(key) or self.table[self.default][key]
        return text.format(**values) if values else text

    __call__ = get

    def missing(self) -> dict[str, list[str]]:
        """Keys of the default language that each other language lacks, for tests and CI."""
        keys = set(self.table[self.default])
        return {lang: sorted(keys - set(table)) for lang, table in self.table.items() if lang != self.default}

    def unknown(self) -> dict[str, list[str]]:
        """Keys a translation has that the default language doesn't (typos, removed texts)."""
        keys = set(self.table[self.default])
        return {lang: sorted(set(table) - keys) for lang, table in self.table.items() if lang != self.default}

    async def apply_commands(self, bot: Any, names: Iterable[str], prefix: str = "command.") -> None:
        """Sets the command menu in every language from `command.<name>` keys (setMyCommands)."""
        from telegram import BotCommand

        names = list(names)
        for lang in self.table:
            commands = [BotCommand(name, self.get(lang, prefix + name)) for name in names]
            await bot.set_my_commands(commands, language_code=None if lang == self.default else lang)
