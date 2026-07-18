"""Generic scenario engine: partial results → all possible completions."""

from __future__ import annotations

from collections.abc import Callable, Iterator
from dataclasses import dataclass
from enum import Enum
from itertools import product
from typing import Any


class Outcome(Enum):
    """Result of a fixture from the home team's perspective."""

    HOME_WIN = "home_win"
    DRAW = "draw"
    AWAY_WIN = "away_win"


@dataclass(frozen=True)
class Fixture:
    """Scheduled match identified by home/away pair (no matchday)."""

    home: str
    away: str


@dataclass(frozen=True)
class PlayedMatch:
    """A fixture with a concrete scoreline (known or hypothesized)."""

    home: str
    away: str
    home_goals: int
    away_goals: int

    @property
    def fixture(self) -> Fixture:
        return Fixture(self.home, self.away)

    @property
    def outcome(self) -> Outcome:
        if self.home_goals > self.away_goals:
            return Outcome.HOME_WIN
        if self.home_goals < self.away_goals:
            return Outcome.AWAY_WIN
        return Outcome.DRAW

    @staticmethod
    def from_outcome(fixture: Fixture, outcome: Outcome) -> PlayedMatch:
        """Canonical pending scorelines: win 1-0 / draw 0-0 / away win 0-1."""
        if outcome is Outcome.HOME_WIN:
            return PlayedMatch(fixture.home, fixture.away, 1, 0)
        if outcome is Outcome.AWAY_WIN:
            return PlayedMatch(fixture.home, fixture.away, 0, 1)
        return PlayedMatch(fixture.home, fixture.away, 0, 0)


@dataclass(frozen=True)
class PartialState:
    """Known scorelines plus pending fixtures for one closed set of teams."""

    teams: tuple[str, ...]
    known: frozenset[PlayedMatch]
    pending: tuple[Fixture, ...]


@dataclass(frozen=True)
class World:
    """One complete assignment of scorelines to every fixture."""

    teams: tuple[str, ...]
    results: frozenset[PlayedMatch]

    def played(self, home: str, away: str) -> PlayedMatch:
        for match in self.results:
            if match.home == home and match.away == away:
                return match
        raise KeyError(f"No result for {home} vs {away}")

    def outcome(self, home: str, away: str) -> Outcome:
        return self.played(home, away).outcome

    def matches_involving(self, team: str) -> list[PlayedMatch]:
        return [m for m in self.results if m.home == team or m.away == team]

    def group_rivals(self, team: str) -> list[str]:
        return [t for t in self.teams if t != team]


class ScenarioEngine:
    """Enumerate possible worlds and test whether a property holds in all of them."""

    def __init__(self) -> None:
        self._predicates: dict[str, Callable[..., Any]] = {}

    def define(self, name: str, fn: Callable[..., Any]) -> None:
        """Register a named predicate / helper for later entailment queries."""
        self._predicates[name] = fn

    def scenarios(self, state: PartialState) -> Iterator[World]:
        """Yield every completion of pending fixtures (3**k worlds)."""
        known = list(state.known)
        if not state.pending:
            yield World(state.teams, frozenset(known))
            return
        for assignment in product(Outcome, repeat=len(state.pending)):
            completed = known + [
                PlayedMatch.from_outcome(fixture, outcome)
                for fixture, outcome in zip(state.pending, assignment, strict=True)
            ]
            yield World(state.teams, frozenset(completed))

    def holds_in_all(
        self,
        pred: Callable[[World], bool],
        state: PartialState,
    ) -> bool:
        """True iff pred(world) is true for every scenario (KB ⊨ property)."""
        return all(pred(world) for world in self.scenarios(state))

    def counterexample(
        self,
        pred: Callable[[World], bool],
        state: PartialState,
    ) -> World | None:
        """Return a world where pred fails, or None if it holds everywhere."""
        for world in self.scenarios(state):
            if not pred(world):
                return world
        return None

    def entails(self, name: str, *args: Any, **kwargs: Any) -> Any:
        """Call a registered predicate by name."""
        if name not in self._predicates:
            raise KeyError(f"Unknown predicate {name!r}")
        return self._predicates[name](*args, **kwargs)
