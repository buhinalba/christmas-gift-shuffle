from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class GiftLine:
    recipient: str
    theme: str


@dataclass(frozen=True)
class RenderedEmail:
    subject: str
    text: str
    html: str


class AssignmentEmailRenderer(Protocol):
    def render(self, exchange_name: str, buyer_name: str,
               gifts: list[GiftLine]) -> RenderedEmail: ...


class EmailSender(Protocol):
    def send(self, to: str, subject: str, text: str, html: str | None = None) -> None: ...