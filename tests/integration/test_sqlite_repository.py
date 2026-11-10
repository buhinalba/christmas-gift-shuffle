import pytest
from christmas_gift_schuffle.application.services import AssignmentService
from christmas_gift_schuffle.domain.entities import GiftExchange, Participant, Theme
from christmas_gift_schuffle.domain.strategies import CyclicAssignmentStrategy
from christmas_gift_schuffle.infrastructure.persistence.sqlite import SQLiteGiftExchangeRepository
from christmas_gift_schuffle.domain.exceptions import ConfigurationError


def make_exchange(n=5):
    people = tuple(Participant(f"Person {i}", f"person{i}@example.com") for i in range(n))
    themes = tuple(Theme(f"Theme {i}") for i in range(n - 1))
    return GiftExchange("Test exchange", people, themes)


def test_save_and_load_draft(tmp_path):
    repo = SQLiteGiftExchangeRepository(tmp_path / "test.db")
    repo.initialize()
    exchange = make_exchange()
    repo.save(exchange)
    assert repo.get_by_id(exchange.id) == exchange


def test_generate_and_load_assignments(tmp_path):
    repo = SQLiteGiftExchangeRepository(tmp_path / "test.db")
    repo.initialize()
    draft = make_exchange()
    repo.save(draft)
    generated = AssignmentService(CyclicAssignmentStrategy(seed=5)).generate(draft)
    repo.save_generated_exchange(generated)
    loaded = repo.get_by_id(draft.id)
    assert loaded == generated
    loaded.validate_assignments()


def test_participant_lookup_returns_only_generated_exchanges(tmp_path):
    repo = SQLiteGiftExchangeRepository(tmp_path / "test.db")
    repo.initialize()
    draft = make_exchange()
    repo.save(draft)
    assert repo.get_by_participant_email(draft.participants[0].email) == []
    generated = AssignmentService(CyclicAssignmentStrategy(seed=5)).generate(draft)
    repo.save_generated_exchange(generated)
    assert [e.id for e in repo.get_by_participant_email(draft.participants[0].email)] == [draft.id]


def test_generated_exchange_cannot_be_deleted(tmp_path):
    repo = SQLiteGiftExchangeRepository(tmp_path / "test.db")
    repo.initialize()
    draft = make_exchange()
    repo.save(draft)
    generated = AssignmentService(CyclicAssignmentStrategy(seed=5)).generate(draft)
    repo.save_generated_exchange(generated)
    with pytest.raises(ConfigurationError):
        repo.delete_draft(draft.id)


def test_duplicate_email_is_rejected_by_database(tmp_path):
    repo = SQLiteGiftExchangeRepository(tmp_path / "test.db")
    repo.initialize()
    people = (Participant("A", "same@example.com"), Participant("B", "same@example.com"))
    with pytest.raises(Exception):
        repo.save(GiftExchange("Invalid", people, (Theme("Only theme"),)))
