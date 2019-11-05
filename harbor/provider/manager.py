from typing import TYPE_CHECKING, List, ClassVar

from harbor import conf
from harbor.provider.service.rieltor import RieltorService

if TYPE_CHECKING:
    from harbor.provider.base import PropertyProvider, PropertyItem


class ProviderManager:
    def __init__(self):
        self.services: List['PropertyProvider'] = []

    def register_service(self, s: ClassVar['PropertyProvider']):
        provider_config = conf.get_provider(s.Meta.name)
        self.services.append(s(provider_config))

    def load(self) -> List['PropertyItem']:
        items = []

        for s in self.services:
            items.extend(s.load())

        return items


all_providers = [RieltorService]
active_provider_keys = [p['name'] for p in conf.PROVIDERS]
provider_manager = ProviderManager()
for provider_cls in [cls for cls in all_providers if cls.Meta.name in active_provider_keys]:
    provider_manager.register_service(provider_cls)
