from typing import TYPE_CHECKING, List, ClassVar

from harbor.provider.service.rieltor import RieltorService

if TYPE_CHECKING:
    from harbor.provider.base import PropertyProvider, PropertyItem


class ProviderManager:
    def __init__(self):
        self.services: List['PropertyProvider'] = []

    def register_service(self, s: ClassVar['PropertyProvider']):
        self.services.append(s())

    def load(self) -> List['PropertyItem']:
        items = []

        for s in self.services:
            items.extend(s.load())

        return items


provider_manager = ProviderManager()
provider_manager.register_service(RieltorService)
