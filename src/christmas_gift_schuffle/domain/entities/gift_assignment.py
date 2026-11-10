from dataclasses import dataclass
from uuid import uuid4
from ..exceptions import AssignmentError


@dataclass(frozen=True, slots=True)
class GiftAssignment:
    buyer_id: str
    recipient_id: str
    theme_id: str
    id: str = ""

    def __post_init__(self):
        if not all((self.buyer_id, self.recipient_id, self.theme_id)):
            raise AssignmentError("Assignment references cannot be empty.")
        if self.buyer_id == self.recipient_id:
            raise AssignmentError("A participant cannot buy a gift for themselves.")
        if not self.id:
            object.__setattr__(self, "id", str(uuid4()))
