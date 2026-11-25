"""Domain entity for tournament matches."""

from dataclasses import dataclass, replace
from datetime import date
from enum import Enum

from server.core.entities.names import optional_text


class MatchStatus(Enum):
    PENDING = "pending"
    COMPLETED = "completed"


class MatchResult(Enum):
    FIRST_WIN = "first_win"
    DRAW = "draw"
    SECOND_WIN = "second_win"


@dataclass(frozen=True, kw_only=True)
class Match:
    id: str
    tournament_id: str
    round_number: int
    first_team_id: str | None
    second_team_id: str | None
    bracket_position: int | None = None
    status: MatchStatus = MatchStatus.PENDING
    result: MatchResult | None = None
    first_score: int | None = None
    second_score: int | None = None
    first_team_stats: dict[str, int] | None = None
    second_team_stats: dict[str, int] | None = None
    scheduled_date: date | None = None
    location: str | None = None

    @property
    def has_teams(self) -> bool:
        return (
            self.first_team_id is not None and self.second_team_id is not None
        )

    def schedule(
        self,
        *,
        scheduled_date: date | None,
        location: str | None,
    ) -> "Match":
        """Return the match with an optional date and location.

        Scheduling is independent from the result: it neither requires nor
        changes it. A blank location is treated as absent.
        """
        return replace(
            self,
            scheduled_date=scheduled_date,
            location=optional_text(location),
        )

    def record_result(
        self,
        *,
        result: MatchResult,
        first_score: int | None,
        second_score: int | None,
        first_team_stats: dict[str, int] | None,
        second_team_stats: dict[str, int] | None,
    ) -> "Match":
        if self.first_team_id is None or self.second_team_id is None:
            raise ValueError("partida aguardando equipes")
        if (first_score is None) != (second_score is None):
            raise ValueError("placar completo")
        if first_score is not None and second_score is not None:
            inferred = (
                MatchResult.FIRST_WIN
                if first_score > second_score
                else MatchResult.SECOND_WIN
                if second_score > first_score
                else MatchResult.DRAW
            )
            if inferred is not result:
                raise ValueError("placar não corresponde ao resultado")
        return replace(
            self,
            status=MatchStatus.COMPLETED,
            result=result,
            first_score=first_score,
            second_score=second_score,
            first_team_stats=dict(first_team_stats or {}),
            second_team_stats=dict(second_team_stats or {}),
        )
