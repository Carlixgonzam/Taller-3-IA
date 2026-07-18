"""
Automated tests for World Cup scenario rules.

Run with: pytest tests/test_predicates.py -v
"""

from __future__ import annotations

from src.logic.predicate.engine import (
    Fixture,
    PartialState,
    PlayedMatch,
    ScenarioEngine,
    World,
)
from src.worldcup.rules import (
    definitely_eliminated,
    definitely_qualified,
    goal_difference,
    points,
    teams_above,
    teams_below,
)


def _world(matches: list[PlayedMatch], teams: tuple[str, ...]) -> World:
    return World(teams, frozenset(matches))


def _state(
    teams: tuple[str, ...],
    known: list[PlayedMatch],
    pending: list[Fixture],
) -> PartialState:
    return PartialState(teams=teams, known=frozenset(known), pending=tuple(pending))


class TestPointsAndGD:
    def test_win_draw_loss_points_and_gd(self):
        world = _world(
            [
                PlayedMatch("A", "B", 2, 0),
                PlayedMatch("A", "C", 1, 1),
                PlayedMatch("A", "D", 0, 1),
                PlayedMatch("B", "C", 0, 0),
                PlayedMatch("B", "D", 0, 0),
                PlayedMatch("C", "D", 0, 0),
            ],
            ("A", "B", "C", "D"),
        )
        assert points(world, "A") == 4
        assert goal_difference(world, "A") == 1

    def test_three_wins(self):
        world = _world(
            [
                PlayedMatch("A", "B", 1, 0),
                PlayedMatch("A", "C", 1, 0),
                PlayedMatch("A", "D", 1, 0),
                PlayedMatch("B", "C", 0, 0),
                PlayedMatch("B", "D", 0, 0),
                PlayedMatch("C", "D", 0, 0),
            ],
            ("A", "B", "C", "D"),
        )
        assert points(world, "A") == 9
        assert goal_difference(world, "A") == 3


class TestTeamsBelowAbove:
    def test_same_points_better_gd_ranks_higher(self):
        """Equal points: better GD ranks strictly above."""
        matches = [
            PlayedMatch("A", "C", 2, 0),
            PlayedMatch("B", "D", 1, 0),
            PlayedMatch("A", "D", 0, 0),
            PlayedMatch("B", "C", 0, 0),
            PlayedMatch("A", "B", 0, 0),
            PlayedMatch("C", "D", 0, 0),
        ]
        world = _world(matches, ("A", "B", "C", "D"))
        assert points(world, "A") == points(world, "B")
        assert goal_difference(world, "A") > goal_difference(world, "B")
        assert teams_below(world, "A") > teams_below(world, "B")
        assert teams_above(world, "B") > teams_above(world, "A")

    def test_clear_leader(self):
        world = _world(
            [
                PlayedMatch("A", "B", 3, 0),
                PlayedMatch("A", "C", 2, 0),
                PlayedMatch("A", "D", 1, 0),
                PlayedMatch("B", "C", 0, 0),
                PlayedMatch("B", "D", 0, 0),
                PlayedMatch("C", "D", 0, 0),
            ],
            ("A", "B", "C", "D"),
        )
        assert teams_below(world, "A") == 3
        assert teams_above(world, "A") == 0
        assert teams_above(world, "D") >= 1


class TestDefinitelyQualified:
    def test_mexico_style_clinch(self):
        teams = ("MEX", "RSA", "KOR", "CZE")
        known = [
            PlayedMatch("MEX", "RSA", 2, 0),
            PlayedMatch("KOR", "CZE", 1, 1),
            PlayedMatch("MEX", "KOR", 1, 0),
            PlayedMatch("RSA", "CZE", 1, 0),
        ]
        pending = [Fixture("MEX", "CZE"), Fixture("RSA", "KOR")]
        state = _state(teams, known, pending)
        engine = ScenarioEngine()

        assert definitely_qualified(engine, state, "MEX") is True
        assert definitely_qualified(engine, state, "RSA") is False

    def test_finished_group_gd_tiebreak_qualifies(self):
        """A and B on 4 pts; A better GD → A has ≥2 below; C/D worse."""
        teams = ("A", "B", "C", "D")
        known = [
            PlayedMatch("A", "C", 2, 0),
            PlayedMatch("B", "D", 1, 0),
            PlayedMatch("A", "D", 0, 0),
            PlayedMatch("B", "C", 0, 0),
            PlayedMatch("A", "B", 0, 0),
            PlayedMatch("C", "D", 0, 0),
        ]
        # A5(+2), B5(+1), C1, D1 — both A and B qualify.
        state = _state(teams, known, [])
        engine = ScenarioEngine()
        assert definitely_qualified(engine, state, "A") is True
        assert definitely_qualified(engine, state, "B") is True
        assert definitely_eliminated(engine, state, "C") is True


class TestDefinitelyEliminated:
    def test_last_place_eliminated_with_pending(self):
        teams = ("A", "B", "C", "D")
        known = [
            PlayedMatch("A", "D", 1, 0),
            PlayedMatch("B", "D", 1, 0),
            PlayedMatch("C", "D", 1, 0),
            PlayedMatch("A", "B", 0, 0),
            PlayedMatch("A", "C", 0, 0),
        ]
        pending = [Fixture("B", "C")]
        state = _state(teams, known, pending)
        engine = ScenarioEngine()
        assert definitely_eliminated(engine, state, "D") is True
        assert definitely_qualified(engine, state, "D") is False
