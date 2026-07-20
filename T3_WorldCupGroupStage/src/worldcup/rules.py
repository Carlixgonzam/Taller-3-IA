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
    pts = 0

    for match in world.matches_involving(team):

        if match.home == team:

            if match.home_goals > match.away_goals:
                pts += 3

            elif match.home_goals == match.away_goals:
                pts += 1

        else:

            if match.away_goals > match.home_goals:
                pts += 3

            elif match.home_goals == match.away_goals:
                pts += 1
                
    return pts
    # === END YOUR CODE ===


def goal_difference(world: World, team: str) -> int:
    """
    Goal difference (GF - GA) for `team` in this completed scenario.
    """
    # === YOUR CODE HERE ===
    gf = 0
    ga = 0

    for match in world.matches_involving(team):

        if match.home == team:

            gf += match.home_goals
            ga += match.away_goals

        else:

            gf += match.away_goals
            ga += match.home_goals

    return gf - ga
    # === END YOUR CODE ===


def teams_below(world: World, team: str) -> int:
    """
    How many group rivals finish strictly below `team` on (points, then GD).
    """
    # === YOUR CODE HERE ===
    below = 0

    my_points = points(world, team)
    my_gd = goal_difference(world, team)

    for rival in world.group_rivals(team):

        rival_points = points(world, rival)
        rival_gd = goal_difference(world, rival)

        if my_points > rival_points:

            below += 1

        elif my_points == rival_points and my_gd > rival_gd:

            below += 1

    return below
    # === END YOUR CODE ===


def teams_above(world: World, team: str) -> int:
    """
    How many group rivals finish strictly above `team` on (points, then GD).
    """
    # === YOUR CODE HERE ===
    above = 0

    my_points = points(world, team)
    my_gd = goal_difference(world, team)

    for rival in world.group_rivals(team):

        rival_points = points(world, rival)
        rival_gd = goal_difference(world, rival)

        if rival_points > my_points:

            above += 1

        elif rival_points == my_points and rival_gd > my_gd:

            above += 1

    return above
    # === END YOUR CODE ===


def clasifica(world, team):
    return teams_below(world, team) >= 2

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
    def clasifica(world):
        return teams_below(world, team) >= 2

    return engine.holds_in_all(clasifica, state)
    # === END YOUR CODE ===


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
    def eliminado(world):
        return teams_above(world, team) >= 2

    return engine.holds_in_all(eliminado, state)
    # === END YOUR CODE ===


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
