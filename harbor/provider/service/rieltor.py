import re
from enum import Enum
from typing import List, Tuple
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup, Tag

from harbor.provider.base import PropertyProvider, PropertyItem


Locations = {
    104: "Герое Днепра (М)",

    "Герое Днепра (М)": 104,
}

PriceRange = Tuple[int, int]
SquareRange = Tuple[int, int]


class Currency(Enum):
    UAH = 1
    USD = 2


class Soring(Enum):
    ByDate = 'bydate'


class QueryBuilder:
    def __init__(self):
        self._currency: Currency = Currency.USD
        self._locations: List[int] = []
        self._price: PriceRange = (0, 0)
        self._rooms: List[int] = []
        self._kitchen: SquareRange = (0, 0)
        self._square: SquareRange = (0, 0)
        self._useful_square: SquareRange = (0, 0)
        self._sort: Soring = Soring.ByDate
        self._page = 1

    def currency(self, c: Currency) -> 'QueryBuilder':
        self._currency = c
        return self

    def locations(self, l: List[int]) -> 'QueryBuilder':
        self._locations = l
        return self

    def price(self, minimum: int = 0, maximum: int = 0) -> 'QueryBuilder':
        self._price = (minimum, maximum)
        return self

    def rooms(self, r: List[int]) -> 'QueryBuilder':
        self._rooms = r
        return self

    def kitchen_square(self, minimum: int = 0, maximum: int = 0) -> 'QueryBuilder':
        self._kitchen = (minimum, maximum)
        return self

    def square(self, minimum: int = 0, maximum: int = 0) -> 'QueryBuilder':
        self._square = (minimum, maximum)
        return self

    def useful_square(self, minimum: int = 0, maximum: int = 0) -> 'QueryBuilder':
        self._useful_square = (minimum, maximum)
        return self

    def sorting(self, s: Soring) -> 'QueryBuilder':
        self._sort = s
        return self

    def page(self, p: int) -> 'QueryBuilder':
        self._page = p
        return self

    def build(self) -> dict:
        query = {
            'currency': self._currency.value,
            **{f'orient[{i}]': c for i, c in enumerate(self._locations)},
            **{f'room_cnt[{i}]': r for i, r in enumerate(self._rooms)},
            'sort': self._sort.value,
        }

        if self._price[0]:
            query['price_min'] = self._price[0]
        if self._price[1]:
            query['price_max'] = self._price[1]

        if self._kitchen[0]:
            query['kitchen_area_min'] = self._kitchen[0]
        if self._kitchen[1]:
            query['kitchen_area_max'] = self._kitchen[1]

        if self._square[0]:
            query['common_area_min'] = self._square[0]
        if self._square[1]:
            query['common_area_max'] = self._square[1]

        if self._useful_square[0]:
            query['useful_area_min'] = self._useful_square[0]
        if self._useful_square[1]:
            query['useful_area_max'] = self._useful_square[1]

        if self._page > 1:
            query['page'] = self._page

        return query


class RieltorService(PropertyProvider):
    class Meta:
        name = 'rieltor'

    def __init__(self):
        super(RieltorService, self).__init__('https://rieltor.ua/flats-sale/')
        self.max_items = 25
        self.max_images = 5

    def load(self) -> List[PropertyItem]:
        items = []

        links = self._load_links()
        if not links:
            return items

        for l in links:
            items.append(self._load_info(l))

        return items

    def _load_links(self) -> List[str]:
        links = []
        query = self.query

        page = 1
        while True:
            self.handle_on_request_start()
            html = requests.get(self._host, params=query.page(page).build()).text
            html_parser = BeautifulSoup(html, features='html.parser')
            html_items = html_parser.find_all('div', class_='catalog-item')
            if not html_items:
                break

            for hi in html_items:
                link = hi.find('div', class_='catalog-item__img').a['href']
                links.append(link)
                if len(links) >= self.max_items:
                    break

            page += 1

        return links

    def _load_info(self, rel_link) -> PropertyItem:
        item = PropertyItem(self.Meta.name, rel_link)
        path = urljoin(self._host, rel_link)

        html = requests.get(path).text
        html_parser = BeautifulSoup(html, features='html.parser')
        html_panel = html_parser.find('div', class_='ov-params-col')
        address = html_panel.find('h1', class_='catalog-view-header__title ov-title').a.string
        price = html_panel.find('div', class_='ov-price').contents[0]
        price = int(''.join(price.split()))

        html_params = html_panel.find('dl', class_='ov-params-list')
        dt = None
        for html_p in html_params.children:
            if isinstance(html_p, Tag) and html_p.name == 'dt':
                dt = html_p.text.strip()
            elif isinstance(html_p, Tag) and html_p.name == 'dd':
                if dt is None:
                    continue
                if dt == 'Площа':
                    square, useful_square, kitchen = re.findall(r'(\d+)', html_p.text.strip())
                    item.square = int(square)
                    item.useful_square = int(useful_square)
                    item.kitchen = int(kitchen)
                elif dt == 'Кімнати':
                    rooms = re.findall(r'(\d+)', html_p.text.strip())[0]
                    item.rooms = int(rooms)
                elif dt == 'Поверховість':
                    floor, max_floor = re.findall(r'(\d+)', html_p.text.strip())
                    item.floor = int(floor)
                    item.max_floor = int(max_floor)

        secondary_params = html_panel.find('dl', class_='ov-params-list_secondary').find_all('dd')
        external_id = secondary_params[4].text

        desc = html_parser.find('div', class_='description-container').find('dd', class_='description-text').text

        html_images = html_parser.find('div', {'id': 'carousel-offer-generic'})
        for html_img in html_images.find_all('img', class_='fancybox')[:self.max_images]:
            img_src = html_img['src']
            item.photos.append(img_src)

        item.external_id = external_id
        item.address = address
        item.price = price
        item.description = desc

        return item

    @property
    def query(self) -> QueryBuilder:
        return QueryBuilder(
        ).locations(
            [Locations['Герое Днепра (М)']]
        ).price(
            minimum=50_000
        ).rooms(
            [2]
        ).square(
            minimum=50
        )
