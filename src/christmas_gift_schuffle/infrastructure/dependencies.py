import os
from ..application.interfaces import GiftExchangeRepository
from .persistence.sqlite import SQLiteGiftExchangeRepository


def create_repository() -> GiftExchangeRepository:
    """Composition root: select persistence adapter from configuration."""
    backend = os.getenv("DATABASE_BACKEND", "sqlite").strip().lower()
    if backend == "sqlite":
        repo = SQLiteGiftExchangeRepository(
            os.getenv("SQLITE_DATABASE_PATH", "data/christmas_gift_schuffle.db")
        )
        repo.initialize()
        return repo
    if backend == "snowflake":
        raise NotImplementedError("Snowflake adapter is a future implementation.")
    raise ValueError(f"Unsupported DATABASE_BACKEND: {backend}")
