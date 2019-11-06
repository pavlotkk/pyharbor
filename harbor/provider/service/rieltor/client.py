from typing import List
from urllib.parse import urljoin

from harbor.provider.balancer import requester
from harbor.provider.base import PropertyProvider, PropertyItem
from harbor.provider.service.rieltor.locations import Locations
from harbor.provider.service.rieltor.parser import parse_page_items_links, parse_item
from harbor.provider.service.rieltor.query import QueryBuilder


class RieltorService(PropertyProvider):
    class Meta:
        name = 'rieltor'

    def __init__(self, base_url: str, **kwargs):
        """
        Create instance
        :param host: service base host
        :param kwargs:
            * max_items_to_load (default 25) - maximum items to load
            * max_images_to_load (default 5) - maximum item's images to load
            * locations - list of addresses (see harbor.provider.service.rieltor.locations.Locations)
            * price_min - lowest price (default 0) in USD
            * price_max - higher price (default 0) in USD
            * rooms - list of rooms number, ex. [2, 3]
            * square - minimum square
        """
        super(RieltorService, self).__init__(base_url, **kwargs)
        self._locations = [Locations[l] for l in kwargs.get('locations', []) if l in Locations]

    @classmethod
    def get_default(cls) -> 'RieltorService':
        from harbor import conf
        provider = conf.get_provider(cls.Meta.name)
        return cls(
            provider['base_url'],
            **provider
        )

    def load(self) -> List[PropertyItem]:
        items = []

        links = self._load_item_links()
        if not links:
            return items

        for l in links:
            items.append(self.load_item(l))

        return items

    def _load_item_links(self) -> List[str]:
        links = []
        query = self.query

        page = 1
        while True:
            html = requester.get(self._base_url, params=query.page(page).build()).text
            links_on_page = parse_page_items_links(html)

            # items not found
            if not links_on_page:
                break

            links.extend(links_on_page)
            if len(links) >= self._max_items:
                links = links[:self._max_items]
                break

            page += 1

        return links

    def load_item(self, rel_link) -> PropertyItem:
        path = urljoin(self._base_url, rel_link)
        html = requester.get(path).text

        item = parse_item(html, self._max_images)

        item.provider = self.Meta.name
        item.rel_url = rel_link

        return item

    @property
    def query(self) -> QueryBuilder:
        return QueryBuilder(
        ).locations(
            self._locations
        ).price(
            minimum=self._price_min,
            maximum=self._price_max,
        ).rooms(
            self._rooms
        ).square(
            minimum=self._min_square
        )
