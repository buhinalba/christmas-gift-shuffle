from dataclasses import dataclass
from uuid import uuid4
from ..exceptions import ConfigurationError


@dataclass(frozen=True, slots=True)
class Participant:
    name: str
    email: str
    id: str

    def __init__(self, name: str, email: str, id: str | None = None):
        name, email = name.strip(), email.strip().casefold()
        if not name:
            raise ConfigurationError("Participant name cannot be empty.")
        if not email or "@" not in email:
            raise ConfigurationError("Participant must have a valid email address.")
        object.__setattr__(self, "name", name)
        object.__setattr__(self, "email", email)
        object.__setattr__(self, "id", id or str(uuid4()))
