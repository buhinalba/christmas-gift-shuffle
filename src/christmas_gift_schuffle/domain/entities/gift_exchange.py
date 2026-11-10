from dataclasses import dataclass
from enum import StrEnum
from uuid import uuid4
from ..exceptions import AssignmentError, ConfigurationError
from .participant import Participant
from .theme import Theme
from .gift_assignment import GiftAssignment


class ExchangeStatus(StrEnum):
    DRAFT = "draft"
    GENERATED = "generated"
    CLOSED = "closed"


@dataclass(frozen=True, slots=True)
class GiftExchange:
    name: str
    participants: tuple[Participant, ...]
    themes: tuple[Theme, ...]
    assignments: tuple[GiftAssignment, ...] = ()
    status: ExchangeStatus = ExchangeStatus.DRAFT
    id: str = ""

    def __post_init__(self):
        name = self.name.strip()
        if not name:
            raise ConfigurationError("Exchange name cannot be empty.")
        object.__setattr__(self, "name", name)
        object.__setattr__(self, "participants", tuple(self.participants))
        object.__setattr__(self, "themes", tuple(self.themes))
        object.__setattr__(self, "assignments", tuple(self.assignments))
        if not self.id:
            object.__setattr__(self, "id", str(uuid4()))
        self._validate_configuration()
        if self.status == ExchangeStatus.DRAFT and self.assignments:
            raise ConfigurationError("A draft exchange cannot contain assignments.")
        if self.status in (ExchangeStatus.GENERATED, ExchangeStatus.CLOSED):
            if not self.assignments:
                raise ConfigurationError("A generated or closed exchange needs assignments.")
            self.validate_assignments()

    def _validate_configuration(self):
        n = len(self.participants)
        if n < 2:
            raise ConfigurationError("An exchange needs at least 2 participants.")
        if len(self.themes) != n - 1:
            raise ConfigurationError(
                f"An exchange with {n} participants must have exactly {n - 1} themes."
            )
        participant_ids = [p.id for p in self.participants]
        emails = [p.email for p in self.participants]
        theme_ids = [t.id for t in self.themes]
        theme_names = [t.name.casefold() for t in self.themes]
        if len(set(participant_ids)) != n:
            raise ConfigurationError("Participant IDs must be unique.")
        if len(set(emails)) != n:
            raise ConfigurationError("Participant email addresses must be unique.")
        if len(set(theme_ids)) != len(self.themes):
            raise ConfigurationError("Theme IDs must be unique.")
        if len(set(theme_names)) != len(self.themes):
            raise ConfigurationError("Theme names must be unique.")

    def validate_assignments(self):
        n, theme_ids = len(self.participants), {t.id for t in self.themes}
        people = {p.id for p in self.participants}
        expected = n * (n - 1)
        if len(self.assignments) != expected:
            raise AssignmentError(f"Expected {expected} assignments; got {len(self.assignments)}.")
        if len({a.id for a in self.assignments}) != len(self.assignments):
            raise AssignmentError("Assignment IDs must be unique.")
        for a in self.assignments:
            if a.buyer_id not in people or a.recipient_id not in people:
                raise AssignmentError("Assignment contains an unknown participant.")
            if a.theme_id not in theme_ids:
                raise AssignmentError("Assignment contains an unknown theme.")
            if a.buyer_id == a.recipient_id:
                raise AssignmentError("Self-gifting is not allowed.")
        for buyer in people:
            rows = [a for a in self.assignments if a.buyer_id == buyer]
            if len(rows) != n - 1 or {a.theme_id for a in rows} != theme_ids:
                raise AssignmentError("Each buyer must use every theme exactly once.")
            if {a.recipient_id for a in rows} != people - {buyer}:
                raise AssignmentError("Each buyer must buy for every other participant once.")
        for recipient in people:
            rows = [a for a in self.assignments if a.recipient_id == recipient]
            if len(rows) != n - 1 or {a.theme_id for a in rows} != theme_ids:
                raise AssignmentError("Each recipient must receive every theme exactly once.")

    def with_assignments(self, assignments):
        return GiftExchange(
            name=self.name, participants=self.participants, themes=self.themes,
            assignments=tuple(assignments), status=ExchangeStatus.GENERATED, id=self.id
        )
