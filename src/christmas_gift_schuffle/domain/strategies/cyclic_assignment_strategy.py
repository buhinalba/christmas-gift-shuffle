from random import Random
from ..entities import Participant, Theme, GiftAssignment
from .assignment_strategy import AssignmentStrategy


class CyclicAssignmentStrategy(AssignmentStrategy):
    """Randomized cyclic strategy; every buyer meets every other participant once."""

    def __init__(self, seed: int | None = None):
        self._random = Random(seed)

    def generate(self, participants, themes):
        n = len(participants)
        if n < 2:
            raise ValueError("At least two participants are required.")
        if len(themes) != n - 1:
            raise ValueError("There must be exactly N-1 themes.")

        people, shuffled_themes = list(participants), list(themes)
        self._random.shuffle(people)
        self._random.shuffle(shuffled_themes)
        shifts = list(range(1, n))
        self._random.shuffle(shifts)

        return tuple(
            GiftAssignment(
                buyer_id=people[i].id,
                recipient_id=people[(i + shift) % n].id,
                theme_id=theme.id,
            )
            for theme, shift in zip(shuffled_themes, shifts)
            for i in range(n)
        )
