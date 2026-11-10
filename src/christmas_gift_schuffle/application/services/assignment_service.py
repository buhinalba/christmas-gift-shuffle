from ...domain.entities import GiftExchange
from ...domain.strategies import AssignmentStrategy


class AssignmentService:
    def __init__(self, strategy: AssignmentStrategy):
        self._strategy = strategy

    def generate(self, exchange: GiftExchange) -> GiftExchange:
        if exchange.assignments:
            raise ValueError("Assignments have already been generated.")
        assignments = self._strategy.generate(exchange.participants, exchange.themes)
        return exchange.with_assignments(assignments)
