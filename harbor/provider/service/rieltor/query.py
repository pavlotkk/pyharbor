from enum import Enum
from typing import List, Tuple


class Currency(Enum):
    UAH = 1
    USD = 2


class Soring(Enum):
    ByDate = 'bydate'


PriceRange = Tuple[int, int]
SquareRange = Tuple[int, int]


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
