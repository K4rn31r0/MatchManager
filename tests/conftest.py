"""Shared fixtures for the test suite."""

import pytest

from tests.fakes import InMemoryTournamentRepository


@pytest.fixture
def tournament_repository() -> InMemoryTournamentRepository:
    return InMemoryTournamentRepository()
