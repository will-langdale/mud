"""Session wrapper around Mud's engine."""

from __future__ import annotations

import asyncio
import random
import traceback
from collections.abc import Awaitable, Callable, Iterable
from contextlib import suppress

from mud.engine.engine import EngineOutcome, GameEngine
from mud.engine.exceptions import InputExhausted
from mud.events import Artifacts, EngineEvent

InputProvider = Callable[[], str | Awaitable[str]]
OutputHandler = Callable[[EngineEvent], None]
QuitHandler = Callable[[], None]


class GameSession:
    """Run a Mud traversal without multiprocessing."""

    def __init__(
        self,
        input_provider: InputProvider,
        output_handler: OutputHandler,
        quit_handler: QuitHandler | None = None,
        *,
        seed: int | None = None,
    ) -> None:
        """Create a session with UI or scripted input/output callbacks."""
        self.input_provider = input_provider
        self.output_handler = output_handler
        self.quit_handler = quit_handler
        self.seed = seed
        self.rng = random.Random(seed)
        self.deaths = 0
        self.artifacts = [False, False, False]
        self.error_count = 0
        self._engine = self._new_engine()

    async def run(self) -> None:
        """Run until the user quits, the final ending exits, or input stops."""
        while True:
            try:
                result = await self._engine.run(self.deaths, self.artifacts)
            except InputExhausted:
                raise
            except KeyboardInterrupt:
                return
            except Exception:  # noqa: BLE001
                self.output_handler(
                    "[[Error]]. Your input has been recorded for debugging. "
                    "Your current traverse has restarted."
                )
                self.output_handler(traceback.format_exc())
                self.error_count += 1
                self._reset_engine()
                continue

            if result.outcome is EngineOutcome.DEATH:
                self.output_handler(result.death_text)
                self.artifacts = list(result.artifacts or self.artifacts)
                self.output_handler(Artifacts(self.artifacts))
                self.deaths += 1
                self._reset_engine()
            elif result.outcome is EngineOutcome.QUIT:
                if self.quit_handler is not None:
                    self.quit_handler()
                return
            elif result.outcome is EngineOutcome.FINAL_ENDING:
                return

    async def run_script(self, inputs: Iterable[str]) -> list[EngineEvent]:
        """Run with scripted inputs and return all emitted events."""
        events: list[EngineEvent] = []
        iterator = iter(inputs)

        def next_input() -> str:
            try:
                return next(iterator)
            except StopIteration as exc:
                raise InputExhausted from exc

        scripted = type(self)(
            next_input,
            events.append,
            self.quit_handler,
            seed=self.seed,
        )
        with suppress(InputExhausted):
            await scripted.run()
        return events

    def _new_engine(self) -> GameEngine:
        """Create an engine bound to this session's callbacks and RNG."""
        return GameEngine(
            self.input_provider,
            self.output_handler,
            rng=self.rng,
        )

    def _reset_engine(self) -> None:
        self._engine.reset_traversal()


async def run_script_async(
    inputs: Iterable[str],
    *,
    seed: int | None = None,
) -> list[EngineEvent]:
    """Run a fresh scripted session and return emitted events."""
    events: list[EngineEvent] = []
    iterator = iter(inputs)

    def next_input() -> str:
        try:
            return next(iterator)
        except StopIteration as exc:
            raise InputExhausted from exc

    session = GameSession(next_input, events.append, seed=seed)
    with suppress(InputExhausted):
        await session.run()
    return events


def run_script(inputs: Iterable[str], *, seed: int | None = None) -> list[EngineEvent]:
    """Run a fresh scripted session and return emitted events."""
    return asyncio.run(run_script_async(inputs, seed=seed))
