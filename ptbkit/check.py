"""Checks that a bot's translations are complete, for its tests and CI.

    from ptbkit.check import assert_complete
    def test_translations():
        assert_complete(STRINGS, code="bot")

or from a shell: `python -m ptbkit.check bot/res/strings bot`

Finds: keys a language lacks or has too many, texts whose placeholders differ from English, texts
that are not valid format strings, keys the code uses that en.json doesn't have, and (optionally)
keys nothing uses.
"""

from __future__ import annotations

import re
import string
import sys
from pathlib import Path
from typing import Iterable

from ptbkit.strings import Strings

# `t(lang, "key")`, `strings(lang, "key")`, `strings.get(lang, "key")`, `STRINGS.get(...)`, `tr(...)`, `_(...)`
DEFAULT_CALL = re.compile(
    r"""\b(?:t|tr|_|strings|STRINGS|texts|TEXTS)(?:\.get)?\(\s*[^,()]+?,\s*(?P<q>["'])(?P<key>[A-Za-z0-9_.\-]+)(?P=q)"""
)


def placeholders(text: str) -> set[str]:
    """Names of the `{name}` fields in a text; raises ValueError on broken braces."""
    return {field.split(".")[0].split("[")[0] for _, field, _, _ in string.Formatter().parse(text) if field}


def _sources(code: str | Path | Iterable[str | Path]) -> list[Path]:
    roots = [code] if isinstance(code, (str, Path)) else list(code)
    files: list[Path] = []
    for root in map(Path, roots):
        files += [root] if root.is_file() else sorted(p for p in root.rglob("*.py") if "site-packages" not in p.parts)
    return files


def problems(
    strings: Strings,
    code: str | Path | Iterable[str | Path] = (),
    *,
    call: re.Pattern[str] = DEFAULT_CALL,
    unused: bool = True,
    dynamic: Iterable[str] = ("command.", "label."),
) -> list[str]:
    """Everything wrong with the translations, as readable lines; empty when all is well.
    `dynamic` lists key prefixes the code builds at runtime (f"command.{name}"), so they don't count
    as unused."""
    found: list[str] = []
    default = strings.table[strings.default]
    for lang, keys in strings.missing().items():
        found += [f"{lang}.json lacks {key!r}" for key in keys]
    for lang, keys in strings.unknown().items():
        found += [f"{lang}.json has {key!r}, which {strings.default}.json doesn't" for key in keys]
    for lang, table in strings.table.items():
        for key, text in table.items():
            if not isinstance(text, str):
                found.append(f"{lang}.json {key!r} is not a string")
                continue
            try:
                names = placeholders(text)
            except ValueError as error:
                found.append(f"{lang}.json {key!r} is not a valid format string: {error}")
                continue
            if lang != strings.default and key in default and isinstance(default[key], str):
                try:
                    expected = placeholders(default[key])
                except ValueError:
                    continue
                if names != expected:
                    found.append(f"{lang}.json {key!r} has placeholders {sorted(names)}, {strings.default}.json {sorted(expected)}")
    files = _sources(code)
    if files:
        source = "\n".join(path.read_text(encoding="utf-8", errors="replace") for path in files)
        used = {match.group("key") for match in call.finditer(source)}
        found += [f"the code uses {key!r}, which {strings.default}.json doesn't have" for key in sorted(used - set(default))]
        if unused:
            prefixes = tuple(dynamic)
            for key in sorted(default):
                if key not in used and not key.startswith(prefixes) and f'"{key}"' not in source and f"'{key}'" not in source:
                    found.append(f"{key!r} is not used anywhere in the code")
    return found


def assert_complete(strings: Strings, code: str | Path | Iterable[str | Path] = (), **options) -> None:
    """Fails with every problem listed (for pytest)."""
    found = problems(strings, code, **options)
    assert not found, "Translation problems:\n- " + "\n- ".join(found)


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    if not args:
        print("usage: python -m ptbkit.check <res/strings dir> [code dir or file ...]")
        return 2
    found = problems(Strings(args[0]), args[1:])
    for line in found:
        print(line)
    print("translations complete" if not found else f"{len(found)} problem(s)")
    return 1 if found else 0


if __name__ == "__main__":
    raise SystemExit(main())
