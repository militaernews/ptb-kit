"""Settings helpers."""

from __future__ import annotations


def admin_ids(value: str | None) -> frozenset[int]:
    """`"1, 2,3"` → {1, 2, 3}; empty or missing → no admins. Invalid entries raise ValueError."""
    return frozenset(int(part) for part in (value or "").replace(";", ",").split(",") if part.strip())
