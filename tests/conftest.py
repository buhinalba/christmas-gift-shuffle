import pytest
from christmas_gift_schuffle.domain.entities import GiftExchange, Participant, Theme


@pytest.fixture
def participants():
    return tuple(Participant(f"Person {i}", f"person{i}@example.com") for i in range(1, 9))


@pytest.fixture
def themes():
    return tuple(Theme(f"Theme {i}") for i in range(1, 8))


@pytest.fixture
def draft_exchange(participants, themes):
    return GiftExchange("Family Christmas", participants, themes)
