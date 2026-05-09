from abc import ABC, abstractmethod
from datetime import date

from finhealth.domain.entities.order import OrderEntity


class OrderRepository(ABC):
    @abstractmethod
    async def find_by_date_range(
        self, from_date: date, to_date: date
    ) -> list[OrderEntity]: ...
