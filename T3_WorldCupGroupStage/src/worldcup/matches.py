"""Match loading and visual standings (not scenario logic)."""

from __future__ import annotations

import csv
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from src.logic.predicate.engine import Fixture, Outcome, PartialState, PlayedMatch
from src.worldcup.config import RESULTS_CSV, display_name, flag_emoji, groups, normalize_team

GROUP_IDS = list("abcdefghijkl")


@dataclass(frozen=True)
class Match:
    """One group-stage match in schedule order."""

    index: int
    group: str
    matchday: int
    home: str
    away: str
    home_goals: int
    away_goals: int
    kickoff: datetime | None = None

    def fixture(self) -> Fixture:
        return Fixture(self.home, self.away)

    def as_played(self) -> PlayedMatch:
        return PlayedMatch(self.home, self.away, self.home_goals, self.away_goals)

    def outcome(self) -> Outcome:
        return self.as_played().outcome

    def scoreline(self) -> str:
        return (
            f"{flag_emoji(self.home)} {display_name(self.home)} "
            f"{self.home_goals}-{self.away_goals} "
            f"{flag_emoji(self.away)} {display_name(self.away)}"
        )


@dataclass(frozen=True)
class StandingRow:
    team: str
    played: int
    wins: int
    draws: int
    losses: int
    gf: int
    ga: int
    gd: int
    pts: int


def load_matches(csv_path: Path | str | None = None) -> list[Match]:
    """Load all matches in CSV order (= chronological kickoff order)."""
    path = Path(csv_path) if csv_path else RESULTS_CSV
    matches: list[Match] = []
    with path.open(encoding="utf-8") as f:
        for i, row in enumerate(csv.DictReader(f)):
            ko_raw = (row.get("kickoff") or "").strip()
            kickoff = datetime.fromisoformat(ko_raw) if ko_raw else None
            matches.append(
                Match(
                    index=i,
                    group=row["grupo"].strip().lower(),
                    matchday=int(row["jornada"]),
                    home=normalize_team(row["local"]),
                    away=normalize_team(row["visitante"]),
                    home_goals=int(row["goles_local"]),
                    away_goals=int(row["goles_visitante"]),
                    kickoff=kickoff,
                )
            )
    return matches


def state_for(
    schedule: list[Match],
    played: list[Match],
    group: str,
) -> PartialState:
    """Partial state for one group: known scorelines + still-pending fixtures."""
    group = group.lower()
    teams = tuple(groups()[group])
    group_schedule = [m for m in schedule if m.group == group]
    played_keys = {(m.home, m.away) for m in played if m.group == group}

    known: list[PlayedMatch] = []
    pending: list[Fixture] = []
    for m in group_schedule:
        if (m.home, m.away) in played_keys:
            known.append(m.as_played())
        else:
            pending.append(m.fixture())
    return PartialState(teams=teams, known=frozenset(known), pending=tuple(pending))


def standings_from_matches(played: list[Match], group: str) -> list[StandingRow]:
    """Visual table for one group from matches played so far."""
    group = group.lower()
    stats = {
        t: {"pj": 0, "w": 0, "d": 0, "l": 0, "gf": 0, "ga": 0}
        for t in groups()[group]
    }
    for m in played:
        if m.group != group:
            continue
        for team, gf, ga in (
            (m.home, m.home_goals, m.away_goals),
            (m.away, m.away_goals, m.home_goals),
        ):
            s = stats[team]
            s["pj"] += 1
            s["gf"] += gf
            s["ga"] += ga
            if gf > ga:
                s["w"] += 1
            elif gf == ga:
                s["d"] += 1
            else:
                s["l"] += 1

    rows = [
        StandingRow(
            team=team,
            played=s["pj"],
            wins=s["w"],
            draws=s["d"],
            losses=s["l"],
            gf=s["gf"],
            ga=s["ga"],
            gd=s["gf"] - s["ga"],
            pts=3 * s["w"] + s["d"],
        )
        for team, s in stats.items()
    ]
    rows.sort(key=lambda r: (-r.pts, -r.gd, -r.gf, r.team))
    return rows


def best_third_teams(played: list[Match]) -> set[str]:
    """
    Top 8 third-place teams once every group has finished (all PJ == 3).
    Pure Python visual ranking — not part of the scenario logic.
    """
    thirds: list[StandingRow] = []
    for g in GROUP_IDS:
        rows = standings_from_matches(played, g)
        if len(rows) != 4 or any(r.played != 3 for r in rows):
            return set()
        thirds.append(rows[2])
    thirds.sort(key=lambda r: (-r.pts, -r.gd, -r.gf, r.team))
    return {r.team for r in thirds[:8]}
