import pytest
from christmas_gift_schuffle.domain.entities import GiftExchange, Participant, Theme
from christmas_gift_schuffle.domain.exceptions import ConfigurationError


def test_requires_n_minus_one_themes(participants):
    with pytest.raises(ConfigurationError, match="exactly 7 themes"):
        GiftExchange("Invalid", participants, (Theme("Only one"),))


def test_requires_two_people():
    with pytest.raises(ConfigurationError, match="at least 2"):
        GiftExchange("Solo", (Participant("Only", "only@example.com"),), ())


def test_email_is_normalized():
    p = Participant(" Alex ", " ALEX@Example.COM ")
    assert p.name == "Alex"
    assert p.email == "alex@example.com"


def test_duplicate_emails_rejected(participants, themes):
    duplicate = Participant("Other", participants[0].email)
    with pytest.raises(ConfigurationError, match="email"):
        GiftExchange("Duplicate", participants[:-1] + (duplicate,), themes)
