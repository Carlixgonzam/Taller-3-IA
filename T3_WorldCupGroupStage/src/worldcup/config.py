"""Load World Cup static configuration from assets/world_cup_2026.yaml."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

_ASSETS = Path(__file__).resolve().parents[2] / "assets"
RESULTS_CSV = _ASSETS / "group_stage_results.csv"


@lru_cache(maxsize=1)
def _config() -> dict[str, Any]:
    with (_ASSETS / "world_cup_2026.yaml").open(encoding="utf-8") as f:
        return yaml.safe_load(f)


def groups() -> dict[str, list[str]]:
    return _config()["groups"]


def display_name(team: str) -> str:
    return _config()["display_names"][team]


def flag_emoji(team: str) -> str:
    """Flag emoji for a team slug (🇲🇽, 🏴󠁧󠁢󠁥󠁮󠁧󠁿, …)."""
    return _config()["flag_emojis"][team]


def normalize_team(name: str) -> str:
    """Expect a canonical slug; reject unknown team names."""
    slug = name.strip()
    if slug not in {t for teams in groups().values() for t in teams}:
        raise ValueError(
            f"Unknown team {name!r}. Use a slug from world_cup_2026.yaml "
            f"(e.g. MEX, BIH)."
        )
    return slug
