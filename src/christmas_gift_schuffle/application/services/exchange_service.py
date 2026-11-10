from ...application.interfaces import GiftExchangeRepository
from ...domain.entities import GiftExchange, Participant, Theme


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
