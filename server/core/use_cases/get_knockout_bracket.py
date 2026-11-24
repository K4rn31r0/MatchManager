"""Read a saved knockout bracket for display."""

from server.core.entities.match import MatchResult, MatchStatus
from server.core.entities.tournament import TournamentFormat, TournamentStatus
from server.core.errors import InvalidTournamentError
from server.core.interfaces.match_repository import MatchRepository
from server.core.interfaces.tournament_repository import TournamentRepository
from server.core.entities.knockout_bracket import (
    KnockoutBracket,
    KnockoutRound,
    bracket_size,
)
from server.core.entities.match import Match
from server.core.use_cases.get_tournament import GetTournament


class GetKnockoutBracket:
    def __init__(
        self,
        tournaments: TournamentRepository,
        matches: MatchRepository,
    ) -> None:
        self._get_tournament = GetTournament(tournaments)
        self._matches = matches

    def execute(self, tournament_id: str) -> KnockoutBracket | None:
        tournament = self._get_tournament.execute(tournament_id)
        if tournament.tournament_format is not TournamentFormat.KNOCKOUT:
            raise InvalidTournamentError(
                "O chaveamento exige o formato mata-mata."
            )
        config = tournament.knockout
        if config is None:
            return None

        match_groups: dict[int, list[Match]] = {}
        matches = self._matches.list_for_tournament(tournament_id)
        for match in matches:
            match_groups.setdefault(match.round_number, []).append(match)
        round_count = bracket_size(len(config.initial_order)).bit_length() - 1
        champion_team_id = None
        final_matches = match_groups.get(round_count, [])
        if (
            tournament.status is TournamentStatus.FINISHED
            and len(final_matches) == 1
        ):
            final = final_matches[0]
            if (
                final.status is MatchStatus.COMPLETED
                and final.result is MatchResult.FIRST_WIN
            ):
                champion_team_id = final.first_team_id
            elif (
                final.status is MatchStatus.COMPLETED
                and final.result is MatchResult.SECOND_WIN
            ):
                champion_team_id = final.second_team_id
        return KnockoutBracket(
            rounds=tuple(
                KnockoutRound(
                    number=number,
                    matches=tuple(sorted(
                        match_groups.get(number, []),
                        key=lambda match: match.bracket_position or 0,
                    )),
                    bye_team_ids=(
                        config.bye_team_ids if number == 1 else ()
                    ),
                )
                for number in range(1, round_count + 1)
            ),
            champion_team_id=champion_team_id,
        )
