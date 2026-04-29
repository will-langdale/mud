"""Compatibility facade for the pre-refactor engine module.

New code should import from :mod:`mud.engine`. This module intentionally holds
no game logic; it delegates attribute access to ``mud.engine.runtime`` so older
tests and scripts can keep using ``mud.legacy`` during the transition.
"""

from __future__ import annotations

from mud.engine import runtime as _runtime

_runtime.reset_state()


def __getattr__(name: str) -> object:
    """Delegate legacy attribute access to the runtime module."""
    return getattr(_runtime, name)


def __dir__() -> list[str]:
    """Return runtime attributes for interactive legacy users."""
    return sorted(set(globals()) | set(dir(_runtime)))
