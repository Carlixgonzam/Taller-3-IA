"""
World Cup group-stage rules.

Implement the predicates below. Qualification/elimination uses scenario 
entailment: a claim holds only if it is true in EVERY possible world.

Ranking uses points first, then goal difference (GD) as the only tie-break.
Pending fixtures are completed with canonical scores 1-0 / 0-0 / 0-1.

Hint: Use `world.matches_involving`, `PlayedMatch` fields, and `Outcome`.
"""

from __future__ import annotations

from src.logic.predicate.engine import Outcome, PartialState, ScenarioEngine, World


def points(world: World, team: str) -> int:
    """
    Points for `team` in this completed scenario.

    Win = 3, draw = 1, loss = 0.
    """
    # === YOUR CODE HERE ===
    # === END YOUR CODE ===
    raise NotImplementedError("Implement points()")


def goal_difference(world: World, team: str) -> int:
    """
    Goal difference (GF - GA) for `team` in this completed scenario.
    """
    # === YOUR CODE HERE ===
    # === END YOUR CODE ===
    raise NotImplementedError("Implement goal_difference()")


def teams_below(world: World, team: str) -> int:
    """
    How many group rivals finish strictly below `team` on (points, then GD).
    """
    # === YOUR CODE HERE ===
    # === END YOUR CODE ===
    raise NotImplementedError("Implement teams_below()")


def teams_above(world: World, team: str) -> int:
    """
    How many group rivals finish strictly above `team` on (points, then GD).
    """
    # === YOUR CODE HERE ===
    # === END YOUR CODE ===
    raise NotImplementedError("Implement teams_above()")


def definitely_qualified(
    engine: ScenarioEngine,
    state: PartialState,
    team: str,
) -> bool:
    """
    True iff `team` has clinched top-2:
    in EVERY scenario, at least 2 rivals finish strictly below on (pts, GD).

    Hint: `engine.holds_in_all(pred, state)` where pred(world) -> bool.
    """
    # === YOUR CODE HERE ===
    # === END YOUR CODE ===
    raise NotImplementedError("Implement definitely_qualified()")


def definitely_eliminated(
    engine: ScenarioEngine,
    state: PartialState,
    team: str,
) -> bool:
    """
    True iff `team` cannot finish top-2:
    in EVERY scenario, at least 2 rivals finish strictly above on (pts, GD).
    """
    # === YOUR CODE HERE ===
    # === END YOUR CODE ===
    raise NotImplementedError("Implement definitely_eliminated()")


def register_rules(engine: ScenarioEngine) -> None:
    """Wire student predicates into the engine (given — do not change)."""
    engine.define("points", points)
    engine.define("goal_difference", goal_difference)
    engine.define(
        "definitely_qualified",
        lambda state, team: definitely_qualified(engine, state, team),
    )
    engine.define(
        "definitely_eliminated",
        lambda state, team: definitely_eliminated(engine, state, team),
    )
