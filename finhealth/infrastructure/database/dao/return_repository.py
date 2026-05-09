from abc import ABC, abstractmethod
from datetime import date

from finhealth.domain.entities.return_ import ReturnEntity


class ReturnRepository(ABC):
    @abstractmethod
    async def find_by_date_range(
        self, from_date: date, to_date: date
    ) -> list[ReturnEntity]: ...
