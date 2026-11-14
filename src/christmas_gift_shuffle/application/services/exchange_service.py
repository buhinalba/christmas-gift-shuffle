from christmas_gift_shuffle.application.interfaces import GiftExchangeRepository
from christmas_gift_shuffle.domain.entities import GiftExchange, Participant, Theme
from dataclasses import replace



class GiftExchangeService:
    """Application use cases for creating and retrieving exchanges."""

    def __init__(self, repository: GiftExchangeRepository):
        self._repository = repository

    def create_draft(self, name: str, participants: list[Participant], themes: list[Theme]) -> GiftExchange:
        exchange = GiftExchange(name, tuple(participants), tuple(themes))
        self._repository.save(exchange)
        return exchange

    def get(self, exchange_id: str) -> GiftExchange | None:
        return self._repository.get_by_id(exchange_id)

    def list_all(self) -> list[GiftExchange]:
        return self._repository.list_exchanges()

    def list_for_participant(self, email: str) -> list[GiftExchange]:
        return self._repository.get_by_participant_email(email)

    def delete_draft(self, exchange_id: str) -> None:
        self._repository.delete_draft(exchange_id)

    def update_draft(self, exchange_id: str, name: str,
                     participants: list[Participant], themes: list[Theme]) -> GiftExchange:
        exchange = self._repository.get_by_id(exchange_id)
        if exchange is None:
            raise ValueError("Exchange not found")
        if exchange.status.value != "draft":
            raise ValueError("Only drafts can be edited")
        updated = replace(exchange, name=name,
                          participants=tuple(participants), themes=tuple(themes))
        self._repository.delete_draft(exchange_id)
        self._repository.save(updated)
        return updated