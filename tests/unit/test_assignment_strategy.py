import pytest
from christmas_gift_shuffle.application.services import AssignmentService
from christmas_gift_shuffle.domain.entities import GiftExchange, Participant, Theme
from christmas_gift_shuffle.domain.strategies import CyclicAssignmentStrategy


@pytest.mark.parametrize("n", range(2, 31))
def test_generic_group_sizes(n):
    people = tuple(Participant(f"Person {i}", f"p{i}@example.com") for i in range(n))
    themes = tuple(Theme(f"Theme {i}") for i in range(n - 1))
    exchange = GiftExchange("Generic", people, themes)
    generated = AssignmentService(CyclicAssignmentStrategy(seed=123)).generate(exchange)
    assert len(generated.assignments) == n * (n - 1)
    generated.validate_assignments()


@pytest.mark.parametrize("seed", range(100))
def test_many_seeds(draft_exchange, seed):
    result = AssignmentService(CyclicAssignmentStrategy(seed)).generate(draft_exchange)
    result.validate_assignments()


def test_seed_reproducible(participants, themes):
    exchange = GiftExchange("Seeded", participants, themes)
    a = AssignmentService(CyclicAssignmentStrategy(42)).generate(exchange)
    b = AssignmentService(CyclicAssignmentStrategy(42)).generate(exchange)
    assert {(x.buyer_id, x.recipient_id, x.theme_id) for x in a.assignments} == {
        (x.buyer_id, x.recipient_id, x.theme_id) for x in b.assignments
    }


def test_buyer_gets_every_other_person_once(draft_exchange):
    result = AssignmentService(CyclicAssignmentStrategy(17)).generate(draft_exchange)
    people = {p.id for p in result.participants}
    for buyer in people:
        recipients = {a.recipient_id for a in result.assignments if a.buyer_id == buyer}
        assert recipients == people - {buyer}


def test_recipient_gets_each_theme_once(draft_exchange):
    result = AssignmentService(CyclicAssignmentStrategy(17)).generate(draft_exchange)
    themes = {t.id for t in result.themes}
    for recipient in (p.id for p in result.participants):
        received = {a.theme_id for a in result.assignments if a.recipient_id == recipient}
        assert received == themes


def test_cannot_generate_twice(draft_exchange):
    service = AssignmentService(CyclicAssignmentStrategy(1))
    generated = service.generate(draft_exchange)
    with pytest.raises(ValueError, match="already been generated"):
        service.generate(generated)
