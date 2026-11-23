"""Formats tournaments for display in the HTML templates."""

from dataclasses import dataclass
from datetime import date

from server.core.entities.tournament import (
    Tournament,
    TournamentFormat,
    TournamentStatus,
)

FORMAT_LABELS: dict[TournamentFormat, str] = {
    TournamentFormat.ROUND_ROBIN: "Pontos corridos",
    TournamentFormat.KNOCKOUT: "Mata-mata",
}

STATUS_LABELS: dict[TournamentStatus, str] = {
    TournamentStatus.DRAFT: "Rascunho",
    TournamentStatus.IN_PROGRESS: "Em andamento",
    TournamentStatus.FINISHED: "Encerrado",
}


@dataclass(frozen=True)
class TournamentViewModel:
    """Display-ready representation of a tournament."""

    id: str
    name: str
    format_label: str
    status: str
    status_label: str
    modality: str
    period: str
    participant_count: int


def present_tournament(
    tournament: Tournament, participant_count: int = 0,
) -> TournamentViewModel:
    return TournamentViewModel(
        id=tournament.id,
        participant_count=participant_count,
        name=tournament.name,
        format_label=FORMAT_LABELS[tournament.tournament_format],
        status=tournament.status.value,
        status_label=STATUS_LABELS[tournament.status],
        modality=tournament.modality or "Modalidade não informada",
        period=_format_period(tournament.start_date, tournament.end_date),
    )


def present_tournaments(
    tournaments: list[Tournament], counts: dict[str, int],
) -> list[TournamentViewModel]:
    return [
        present_tournament(tournament, counts.get(tournament.id, 0))
        for tournament in tournaments
    ]


def _format_period(start: date | None, end: date | None) -> str:
    if start and end:
        return f"{_format_date(start)} a {_format_date(end)}"
    if start:
        return f"A partir de {_format_date(start)}"
    if end:
        return f"Até {_format_date(end)}"
    return "Datas não definidas"


def _format_date(value: date) -> str:
    return value.strftime("%d/%m/%Y")
