"""Formats tournament matches for display in the HTML templates."""

from dataclasses import dataclass
from datetime import date

from server.core.entities.match import Match, MatchResult, MatchStatus
from server.core.entities.tournament import TournamentFormat

TO_BE_DEFINED = "A definir"

MATCH_STATUS_LABELS: dict[MatchStatus, str] = {
    MatchStatus.PENDING: "Pendente",
    MatchStatus.COMPLETED: "Concluída",
}


@dataclass(frozen=True)
class MatchViewModel:
    id: str
    first_name: str
    second_name: str
    has_teams: bool
    status: str
    status_label: str
    outcome: str
    schedule_label: str
    result: str
    first_score: int | None
    second_score: int | None
    first_team_stats: dict[str, int]
    second_team_stats: dict[str, int]
    scheduled_date: str
    location: str


@dataclass(frozen=True)
class RoundViewModel:
    number: int
    label: str
    matches: tuple[MatchViewModel, ...]
    bye_names: tuple[str, ...] = ()


def round_label(
    tournament_format: TournamentFormat,
    number: int,
    round_count: int,
) -> str:
    """Name a round: "Rodada 2" (round-robin) or "Fase 2 · Final"."""
    if tournament_format is TournamentFormat.ROUND_ROBIN:
        return f"Rodada {number}"
    suffix = {0: " · Final", 1: " · Semifinal"}.get(round_count - number, "")
    return f"Fase {number}{suffix}"


def present_rounds(
    matches: tuple[Match, ...],
    *,
    tournament_format: TournamentFormat,
    round_count: int,
    team_names: dict[str, str],
    first_round_byes: tuple[str, ...] = (),
) -> list[RoundViewModel]:
    """Group matches (already ordered) by round for display."""
    grouped: dict[int, list[MatchViewModel]] = {}
    for match in matches:
        grouped.setdefault(match.round_number, []).append(
            present_match(match, team_names)
        )
    return [
        RoundViewModel(
            number=number,
            label=round_label(tournament_format, number, round_count),
            matches=tuple(items),
            bye_names=(
                tuple(
                    team_names.get(team_id, team_id)
                    for team_id in first_round_byes
                )
                if number == 1
                else ()
            ),
        )
        for number, items in grouped.items()
    ]


def present_match(match: Match, team_names: dict[str, str]) -> MatchViewModel:
    first_name = _team_name(match.first_team_id, team_names)
    second_name = _team_name(match.second_team_id, team_names)
    return MatchViewModel(
        id=match.id,
        first_name=first_name,
        second_name=second_name,
        has_teams=match.has_teams,
        status=match.status.value,
        status_label=MATCH_STATUS_LABELS[match.status],
        outcome=_outcome(match, first_name, second_name),
        schedule_label=_schedule_label(match.scheduled_date, match.location),
        result=match.result.value if match.result else "",
        first_score=match.first_score,
        second_score=match.second_score,
        first_team_stats=dict(match.first_team_stats or {}),
        second_team_stats=dict(match.second_team_stats or {}),
        scheduled_date=(
            match.scheduled_date.isoformat() if match.scheduled_date else ""
        ),
        location=match.location or "",
    )


def _team_name(team_id: str | None, team_names: dict[str, str]) -> str:
    if team_id is None:
        return TO_BE_DEFINED
    return team_names.get(team_id, TO_BE_DEFINED)


def _outcome(match: Match, first_name: str, second_name: str) -> str:
    if match.status is not MatchStatus.COMPLETED or match.result is None:
        return ""
    if match.result is MatchResult.DRAW:
        verdict = "Empate"
    elif match.result is MatchResult.FIRST_WIN:
        verdict = f"Vencedor: {first_name}"
    else:
        verdict = f"Vencedor: {second_name}"
    if match.first_score is None or match.second_score is None:
        return verdict
    return f"{match.first_score} × {match.second_score} · {verdict}"


def _schedule_label(scheduled_date: date | None, location: str | None) -> str:
    parts = []
    if scheduled_date is not None:
        parts.append(scheduled_date.strftime("%d/%m/%Y"))
    if location:
        parts.append(location)
    return " · ".join(parts)
