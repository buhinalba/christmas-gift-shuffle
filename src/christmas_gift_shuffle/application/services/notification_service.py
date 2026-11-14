from dataclasses import dataclass, field

from christmas_gift_shuffle.domain.entities import GiftExchange
from collections import defaultdict

from christmas_gift_shuffle.application.interfaces.interfaces import (
    AssignmentEmailRenderer, EmailSender, GiftLine,
)


@dataclass
class SendReport:
    sent: list[str] = field(default_factory=list)
    failed: dict[str, str] = field(default_factory=dict)

class AssignmentNotificationService:
    def __init__(self, sender: EmailSender, renderer: AssignmentEmailRenderer):
        self._sender = sender
        self._renderer = renderer

    def send_assignments(self, exchange, only: set[str] | None = None) -> SendReport:
        if exchange.status.value == "draft":
            raise ValueError("Generate and lock the assignments first")

        people = {p.id: p for p in exchange.participants}
        themes = {t.id: t.name for t in exchange.themes}

        by_buyer = defaultdict(list)
        for a in exchange.assignments:
            by_buyer[a.buyer_id].append(a)

        report = SendReport()
        for buyer_id, items in by_buyer.items():
            buyer = people[buyer_id]
            if only is not None and buyer.email not in only:
                continue
            gifts = [GiftLine(people[a.recipient_id].name, themes[a.theme_id])
                     for a in sorted(items, key=lambda a: people[a.recipient_id].name)]
            mail = self._renderer.render(exchange.name, buyer.name, gifts)
            try:
                self._sender.send(buyer.email, mail.subject, mail.text, mail.html)
                report.sent.append(buyer.email)
            except Exception as exc:
                report.failed[buyer.email] = f"{type(exc).__name__}: {exc}"
        return report