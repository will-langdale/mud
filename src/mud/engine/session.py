"""Session wrapper around Mud's runtime engine."""

from __future__ import annotations

import asyncio
import traceback
from collections.abc import Awaitable, Callable, Iterable
from contextlib import suppress

from mud.engine import runtime
from mud.events import Artifacts, EngineEvent

InputProvider = Callable[[], str | Awaitable[str]]
OutputHandler = Callable[[EngineEvent], None]
QuitHandler = Callable[[], None]


class InputExhausted(Exception):
    """Raised by scripted sessions when no more input is available."""


class GameSession:
    """Run a Mud traversal without multiprocessing."""

    def __init__(
        self,
        input_provider: InputProvider,
        output_handler: OutputHandler,
        quit_handler: QuitHandler | None = None,
    ) -> None:
        """Create a session with UI or scripted input/output callbacks."""
        self.input_provider = input_provider
        self.output_handler = output_handler
        self.quit_handler = quit_handler
        self.deaths = 0
        self.artifacts = [False, False, False]
        self.error_count = 0
        self._engine = runtime
        self._engine.reset_state()
        self._configure_engine()

    async def run(self) -> None:
        """Run until the user quits, the final ending exits, or input stops."""
        while True:
            try:
                await self._engine.start(self.deaths, False, False, self.artifacts)
            except self._engine.DeathError as why:
                self.output_handler(str(why.value))
                self.artifacts = list(why.art)
                self.output_handler(Artifacts(self.artifacts))
                self.deaths += 1
                self._reset_engine()
            except InputExhausted:
                raise
            except (SystemExit, KeyboardInterrupt):
                return
            except Exception:  # noqa: BLE001
                self.output_handler(
                    "[[Error]]. Your input has been recorded for debugging. "
                    "Your current traverse has restarted."
                )
                self.output_handler(traceback.format_exc())
                self.error_count += 1
                self._reset_engine()

    async def run_script(self, inputs: Iterable[str]) -> list[EngineEvent]:
        """Run with scripted inputs and return all emitted events."""
        events: list[EngineEvent] = []
        iterator = iter(inputs)

        def next_input() -> str:
            try:
                return next(iterator)
            except StopIteration as exc:
                raise InputExhausted from exc

        scripted = type(self)(next_input, events.append, self.quit_handler)
        with suppress(InputExhausted):
            await scripted.run()
        return events

    def _configure_engine(self) -> None:
        self._engine.configure_io(
            self.input_provider,
            self.output_handler,
            self.quit_handler,
        )

    def _reset_engine(self) -> None:
        self._engine.reset_state()
        self._configure_engine()


async def run_script_async(inputs: Iterable[str]) -> list[EngineEvent]:
    """Run a fresh scripted session and return emitted events."""
    events: list[EngineEvent] = []
    iterator = iter(inputs)

    def next_input() -> str:
        try:
            return next(iterator)
        except StopIteration as exc:
            raise InputExhausted from exc

    session = GameSession(next_input, events.append)
    with suppress(InputExhausted):
        await session.run()
    return events


def run_script(inputs: Iterable[str]) -> list[EngineEvent]:
    """Run a fresh scripted session and return emitted events."""
    return asyncio.run(run_script_async(inputs))
