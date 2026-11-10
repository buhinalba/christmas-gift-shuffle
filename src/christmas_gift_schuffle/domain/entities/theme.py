from dataclasses import dataclass
from uuid import uuid4
from ..exceptions import ConfigurationError


@dataclass(frozen=True, slots=True)
class Theme:
    name: str
    description: str = ""
    id: str = ""

    def __post_init__(self):
        name = self.name.strip()
        if not name:
            raise ConfigurationError("Theme name cannot be empty.")
        object.__setattr__(self, "name", name)
        object.__setattr__(self, "description", self.description.strip())
        if not self.id:
            object.__setattr__(self, "id", str(uuid4()))
