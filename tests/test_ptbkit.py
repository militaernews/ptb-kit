import logging
from pathlib import Path
from types import SimpleNamespace

import pytest

from ptbkit import ErrorReporter, Strings, admin_ids, setup_logging
from ptbkit.errors import format_error

STRINGS = Strings(Path(__file__).parent / "res" / "strings")


def test_strings_pick_language_and_fall_back():
    assert STRINGS.languages == ("de", "en")
    assert STRINGS.lang("de-AT") == "de" and STRINGS.lang("fr") == "en" and STRINGS.lang(None) == "en"
    assert STRINGS.lang_of(SimpleNamespace(language_code="de")) == "de"
    assert STRINGS("de", "hello", name="Ana") == "Hallo Ana"
    assert STRINGS.get("de", "bye") == "Bye"
    with pytest.raises(KeyError):
        STRINGS.get("en", "nope")
    assert STRINGS.missing() == {"de": ["bye"]}
    assert STRINGS.unknown() == {"de": ["typo"]}


def test_missing_default_language(tmp_path):
    with pytest.raises(FileNotFoundError):
        Strings(tmp_path)


async def test_apply_commands():
    calls = []

    class Bot:
        async def set_my_commands(self, commands, scope=None, language_code=None):
            calls.append((language_code, [(c.command, c.description) for c in commands]))

    pytest.importorskip("telegram")
    await STRINGS.apply_commands(Bot(), ["start"])
    assert calls == [("de", [("start", "Starten")]), (None, [("start", "Start")])]


def test_admin_ids():
    assert admin_ids("1, 2;3") == {1, 2, 3}
    assert admin_ids("") == frozenset() and admin_ids(None) == frozenset()


def test_logging_quiets_httpx(tmp_path):
    setup_logging(file=tmp_path / "logs" / "bot.log")
    assert logging.getLogger("httpx").level == logging.WARNING
    assert (tmp_path / "logs" / "bot.log").exists()


def test_format_error_escapes():
    try:
        raise ValueError("<b>bad</b>")
    except ValueError as error:
        text = format_error("bot <x>", error, "ctx & more")
    assert "&lt;b&gt;bad&lt;/b&gt;" in text and "bot &lt;x&gt;" in text and "ctx &amp; more" in text
    assert text.count("<pre>") == 1


async def test_reporter_posts_and_never_raises():
    sent = []

    class Bot:
        async def send_message(self, **kwargs):
            sent.append(kwargs)

    class Broken:
        async def send_message(self, **kwargs):
            raise RuntimeError("down")

    reporter = ErrorReporter("test", chat_id=-100, thread_id=7)
    assert await reporter.report(Bot(), ValueError("x"), "ctx")
    assert sent[0]["message_thread_id"] == 7 and sent[0]["parse_mode"] == "HTML"
    assert not await reporter.report(Broken(), ValueError("x"))
    assert not await ErrorReporter("quiet").report(Bot(), ValueError("x"))

    update = SimpleNamespace(effective_chat=SimpleNamespace(id=5))
    await reporter.handler()(update, SimpleNamespace(bot=Bot(), error=ValueError("y")))
    assert "SimpleNamespace in chat 5" in sent[-1]["text"]


def test_check_finds_every_kind_of_problem(tmp_path):
    from ptbkit.check import main, problems

    strings_dir = tmp_path / "strings"
    strings_dir.mkdir()
    (strings_dir / "en.json").write_text('{"hello": "Hi {name}", "bye": "Bye", "old": "x", "command.start": "Start"}')
    (strings_dir / "de.json").write_text('{"hello": "Hallo {nam}", "bye": "Tschüss {", "old": "x", "command.start": "Los", "extra": "y"}')
    code = tmp_path / "bot.py"
    code.write_text('t(lang, "hello")\nstrings.get(lang, "bye")\nt(lang, "nope")\n')
    found = problems(Strings(strings_dir), code)
    text = "\n".join(found)
    assert "de.json has 'extra'" in text
    assert "placeholders ['nam']" in text
    assert "'bye' is not a valid format string" in text
    assert "the code uses 'nope'" in text
    assert "'old' is not used" in text
    assert "command.start" not in text  # built at runtime
    assert main([str(strings_dir), str(code)]) == 1


def test_check_passes_for_complete_translations():
    from ptbkit.check import assert_complete, problems

    strings = Strings(Path(__file__).parent / "res" / "strings")
    code = Path(__file__).parent / "code"
    found = problems(strings, code)
    assert "de.json lacks 'bye'" in found and any("typo" in line for line in found)
    with pytest.raises(AssertionError, match="Translation problems"):
        assert_complete(strings, code)


def test_check_clean():
    from ptbkit.check import assert_complete

    assert_complete(Strings(Path(__file__).parent / "complete"), Path(__file__).parent / "code")


def test_chat_id_and_scope():
    from ptbkit import chat_id

    assert chat_id("1234567890") == -1001234567890 and chat_id(-100123) == -100123 and chat_id(None) is None
    assert ErrorReporter("x", "1234567890", 0).chat_id == -1001234567890
    assert ErrorReporter("x", "1234567890", 0).thread_id is None


async def test_apply_commands_scope():
    pytest.importorskip("telegram")
    from telegram import BotCommandScopeChat

    scopes = []

    class Bot:
        async def set_my_commands(self, commands, scope=None, language_code=None):
            scopes.append((language_code, scope))

    await STRINGS.apply_commands(Bot(), ["start"], scope=BotCommandScopeChat(5))
    assert all(scope.chat_id == 5 for _, scope in scopes)
