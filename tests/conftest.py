"""Shared fixtures for the test suite."""

import pytest

from tests.fakes import InMemoryTeamRepository, InMemoryTournamentRepository


@pytest.fixture
def tournament_repository() -> InMemoryTournamentRepository:
    return InMemoryTournamentRepository()


@pytest.fixture
def team_repository() -> InMemoryTeamRepository:
    return InMemoryTeamRepository()
