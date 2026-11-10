from abc import ABC, abstractmethod
from ..entities import Participant, Theme, GiftAssignment


class AssignmentStrategy(ABC):
    @abstractmethod
    def generate(self, participants: tuple[Participant, ...],
                 themes: tuple[Theme, ...]) -> tuple[GiftAssignment, ...]:
        raise NotImplementedError
