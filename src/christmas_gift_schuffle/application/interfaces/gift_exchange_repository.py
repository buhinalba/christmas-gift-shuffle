from abc import ABC, abstractmethod
from ...domain.entities import GiftExchange


class GiftExchangeRepository(ABC):
    """Persistence port; adapters implement this interface."""

    @abstractmethod
    def initialize(self) -> None: ...

    @abstractmethod
    def save(self, exchange: GiftExchange) -> None: ...

    @abstractmethod
    def save_generated_exchange(self, exchange: GiftExchange) -> None: ...

    @abstractmethod
    def get_by_id(self, exchange_id: str) -> GiftExchange | None: ...

    @abstractmethod
    def list_exchanges(self) -> list[GiftExchange]: ...

    @abstractmethod
    def get_by_participant_email(self, email: str) -> list[GiftExchange]: ...

    @abstractmethod
    def delete_draft(self, exchange_id: str) -> None: ...
