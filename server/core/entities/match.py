"""Domain entity for tournament matches."""

from dataclasses import dataclass
from enum import Enum


class MatchStatus(Enum):
    PENDING = "pending"
    COMPLETED = "completed"


@dataclass(frozen=True, kw_only=True)
class Match:
    id: str
    tournament_id: str
    round_number: int
    first_team_id: str
    second_team_id: str
    status: MatchStatus = MatchStatus.PENDING
