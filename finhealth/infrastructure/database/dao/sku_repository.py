from abc import ABC, abstractmethod

from finhealth.domain.entities.sku import SKUEntity


class SKURepository(ABC):
    @abstractmethod
    async def find_all(self) -> list[SKUEntity]: ...
