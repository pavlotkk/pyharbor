import re
from enum import Enum
from typing import List, Tuple
from urllib.parse import urljoin

from bs4 import BeautifulSoup, Tag

from harbor.provider.balancer import requester
from harbor.provider.base import PropertyProvider, PropertyItem

Locations = {
    76: "Оболонський",
    104: "Героїв Дніпра (M)",
    105: "Мінська (M)",
    106: "Оболонь (M)",
    107: "Петрівка (M)",
    108: "Мінський масив",
    109: "Вишгородський масив",
    110: "Пріорка",
    111: "Куренівка",
    1349: "Пуща-Водиця",
    1376: "Оболонь",
    78: "Подільський",
    102: "Виноградар",
    103: "Вітряні Гори",
    112: "Мостицький масив",
    113: "Тараса Шевченко (M)",
    114: "Контрактова площа (M)",
    115: "Поштова площа (M)",
    913: "Поділ",
    79: "Шевченківський",
    94: "Нивки (M)",
    97: "Берестейська (M)",
    98: "Шулявська (M)",
    99: "Сирець (M)",
    100: "Дорогожичі (M)",
    101: "Лук&#039;янівська (M)",
    116: "Майдан Незалежності (M)",
    117: "Театральна (M)",
    118: "Площа Льва Толстого (M)",
    190: "Універсітет (M)",
    191: "Золоті Ворота (M)",
    243: "Нивки",
    257: "Кудрявець",
    258: "Татарка",
    911: "Солдатська слобідка",
    912: "Вовчий яр",
    914: "Лук&#039;янівка",
    1278: "Політехнічний інститут",
    1279: "Площа Перемоги",
    80: "Соломянський",
    188: "Вокзальна (M)",
    189: "Політехнічний інститут (M)",
    204: "Солом&#039;янка",
    205: "Чоколівка",
    206: "Караваєві дачі",
    207: "Відрадний",
    224: "Першотравневий",
    255: "Турецьке Містечко",
    256: "Аеропорт Жуляни",
    896: "Новокараваєві дачі",
    897: "Кадетський Гай",
    898: "Байкова гора",
    899: "Монтажник",
    900: "Протасів яр",
    901: "Совки",
    902: "Олександрівська слобідка",
    905: "Залізничний масив",
    81: "Голосіївський",
    120: "Олімпійська (M)",
    140: "Глушкова Академіка",
    195: "Либідська (M)",
    225: "Батиєва Гора",
    226: "Деміївка",
    227: "Саперна слобідка",
    228: "Добрий шлях",
    229: "Голосіїв",
    230: "Теремки-2",
    231: "Теремки-1",
    232: "Експоцентр України",
    233: "Іподром",
    234: "Голосіївський парк",
    235: "Мишоловка",
    236: "Пирогів",
    237: "Корчувате",
    238: "Чапаєвка",
    239: "Селище Водників",
    254: "Новосілки",
    340: "Деміївська (M)",
    341: "Голосіївська (M)",
    342: "Васильківська (M)",
    895: "Феофанія",
    1262: "Виставковий центр (M)",
    1264: "Видубичі (M)",
    82: "Печерський",
    10: "Хрещатик (M)",
    119: "Палац Спорту (M)",
    121: "Дніпро (M)",
    122: "Арсенальна (M)",
    192: "Кловська (M)",
    193: "Печерська (M)",
    196: "Палац Україна (M)",
    259: "Липки",
    906: "Бессарабка",
    907: "Чорна гора",
    908: "Видубичі",
    909: "Звіринець",
    910: "Печерськ",
    1263: "Дружби народів (M)",
    83: "Деснянський",
    127: "Лісова (M)",
    138: "Троєщина",
    139: "Лісовий масив",
    1415: "Чернігівська  (M)",
    84: "Дніпровський",
    123: "Гідропарк (M)",
    124: "Лівоборежна (M)",
    125: "Дарниця (M)",
    126: "Чернігівскька (M)",
    128: "Русанівка",
    129: "Березняки",
    130: "ДВРЗ",
    131: "Стара Дарниця",
    132: "Соцмісто",
    141: "Русанівські сади",
    241: "Воскресеньский масив",
    242: "Комсомольський масив",
    85: "Дарницький",
    133: "Корольок",
    134: "Позняки",
    135: "Харківський масив",
    136: "Рембаза",
    137: "Нова Дарниця",
    202: "Вирлиця (M)",
    203: "Бориспільська (M)",
    240: "Бортничі",
    246: "Осокорки",
    247: "Славутич (M)",
    248: "Осокорки (M)",
    249: "Позняки (M)",
    250: "Харківська (M)",
    893: "Нижні сади",
    894: "Червоний хутір",
    1265: "Червоний хутір (M)",
    86: "Святошинський",
    88: "Академмістечко (M)",
    89: "Біличі",
    90: "Новобіличі",
    91: "Житомирська (M)",
    92: "Авіамістечко",
    93: "Святошин (M)",
    95: "Коцюбинське",
    96: "Берковець",
    208: "Микільська Борщагівка",
    209: "Південна Борщагівка",
    210: "Галагани",
    211: "Софіївська Борщагівка",
    212: "Петропавлівська Борщагівка",
    245: "Жовтневе",
    903: "Михайлівська Борщагівка",
    904: "Братська Борщагівка",

    "Оболонський": 76,
    "Героїв Дніпра (M)": 104,
    "Мінська (M)": 105,
    "Оболонь (M)": 106,
    "Петрівка (M)": 107,
    "Мінський масив": 108,
    "Вишгородський масив": 109,
    "Пріорка": 110,
    "Куренівка": 111,
    "Пуща-Водиця": 1349,
    "Оболонь": 1376,
    "Подільський": 78,
    "Виноградар": 102,
    "Вітряні Гори": 103,
    "Мостицький масив": 112,
    "Тараса Шевченко (M)": 113,
    "Контрактова площа (M)": 114,
    "Поштова площа (M)": 115,
    "Поділ": 913,
    "Шевченківський": 79,
    "Нивки (M)": 94,
    "Берестейська (M)": 97,
    "Шулявська (M)": 98,
    "Сирець (M)": 99,
    "Дорогожичі (M)": 100,
    "Лук&#039;янівська (M)": 101,
    "Майдан Незалежності (M)": 116,
    "Театральна (M)": 117,
    "Площа Льва Толстого (M)": 118,
    "Універсітет (M)": 190,
    "Золоті Ворота (M)": 191,
    "Нивки": 243,
    "Кудрявець": 257,
    "Татарка": 258,
    "Солдатська слобідка": 911,
    "Вовчий яр": 912,
    "Лук&#039;янівка": 914,
    "Політехнічний інститут": 1278,
    "Площа Перемоги": 1279,
    "Соломянський": 80,
    "Вокзальна (M)": 188,
    "Політехнічний інститут (M)": 189,
    "Солом&#039;янка": 204,
    "Чоколівка": 205,
    "Караваєві дачі": 206,
    "Відрадний": 207,
    "Першотравневий": 224,
    "Турецьке Містечко": 255,
    "Аеропорт Жуляни": 256,
    "Новокараваєві дачі": 896,
    "Кадетський Гай": 897,
    "Байкова гора": 898,
    "Монтажник": 899,
    "Протасів яр": 900,
    "Совки": 901,
    "Олександрівська слобідка": 902,
    "Залізничний масив": 905,
    "Голосіївський": 81,
    "Олімпійська (M)": 120,
    "Глушкова Академіка": 140,
    "Либідська (M)": 195,
    "Батиєва Гора": 225,
    "Деміївка": 226,
    "Саперна слобідка": 227,
    "Добрий шлях": 228,
    "Голосіїв": 229,
    "Теремки-2": 230,
    "Теремки-1": 231,
    "Експоцентр України": 232,
    "Іподром": 233,
    "Голосіївський парк": 234,
    "Мишоловка": 235,
    "Пирогів": 236,
    "Корчувате": 237,
    "Чапаєвка": 238,
    "Селище Водників": 239,
    "Новосілки": 254,
    "Деміївська (M)": 340,
    "Голосіївська (M)": 341,
    "Васильківська (M)": 342,
    "Феофанія": 895,
    "Виставковий центр (M)": 1262,
    "Видубичі (M)": 1264,
    "Печерський": 82,
    "Хрещатик (M)": 10,
    "Палац Спорту (M)": 119,
    "Дніпро (M)": 121,
    "Арсенальна (M)": 122,
    "Кловська (M)": 192,
    "Печерська (M)": 193,
    "Палац Україна (M)": 196,
    "Липки": 259,
    "Бессарабка": 906,
    "Чорна гора": 907,
    "Видубичі": 908,
    "Звіринець": 909,
    "Печерськ": 910,
    "Дружби народів (M)": 1263,
    "Деснянський": 83,
    "Лісова (M)": 127,
    "Троєщина": 138,
    "Лісовий масив": 139,
    "Чернігівська  (M)": 1415,
    "Дніпровський": 84,
    "Гідропарк (M)": 123,
    "Лівоборежна (M)": 124,
    "Дарниця (M)": 125,
    "Чернігівскька (M)": 126,
    "Русанівка": 128,
    "Березняки": 129,
    "ДВРЗ": 130,
    "Стара Дарниця": 131,
    "Соцмісто": 132,
    "Русанівські сади": 141,
    "Воскресеньский масив": 241,
    "Комсомольський масив": 242,
    "Дарницький": 85,
    "Корольок": 133,
    "Позняки": 134,
    "Харківський масив": 135,
    "Рембаза": 136,
    "Нова Дарниця": 137,
    "Вирлиця (M)": 202,
    "Бориспільська (M)": 203,
    "Бортничі": 240,
    "Осокорки": 246,
    "Славутич (M)": 247,
    "Осокорки (M)": 248,
    "Позняки (M)": 249,
    "Харківська (M)": 250,
    "Нижні сади": 893,
    "Червоний хутір": 894,
    "Червоний хутір (M)": 1265,
    "Святошинський": 86,
    "Академмістечко (M)": 88,
    "Біличі": 89,
    "Новобіличі": 90,
    "Житомирська (M)": 91,
    "Авіамістечко": 92,
    "Святошин (M)": 93,
    "Коцюбинське": 95,
    "Берковець": 96,
    "Микільська Борщагівка": 208,
    "Південна Борщагівка": 209,
    "Галагани": 210,
    "Софіївська Борщагівка": 211,
    "Петропавлівська Борщагівка": 212,
    "Жовтневе": 245,
    "Михайлівська Борщагівка": 903,
    "Братська Борщагівка": 904,
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

    def __init__(self, config: dict):
        super(RieltorService, self).__init__(config)
        self._max_items = self._config.get('max_items_to_load', 25)
        self._max_images = self._config.get('max_images_to_load', 5)

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
            html = requester.get(self._host, params=query.page(page).build()).text
            html_parser = BeautifulSoup(html, features='html.parser')
            html_items = html_parser.find_all('div', class_='catalog-item')
            if not html_items:
                break

            for hi in html_items:
                link = hi.find('div', class_='catalog-item__img').a['href']
                links.append(link)
                if len(links) >= self._max_items:
                    break

            page += 1

        return links

    def _load_info(self, rel_link) -> PropertyItem:
        item = PropertyItem(self.Meta.name, rel_link)
        item.rel_url = rel_link
        path = urljoin(self._host, rel_link)

        html = requester.get(path).text
        html_parser = BeautifulSoup(html, features='html.parser')
        html_panel = html_parser.find('div', class_='ov-params-col')
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
                    square, useful_square, kitchen = re.findall(r'([0-9]+\.*[0-9]*)',
                                                                html_p.text.strip())
                    item.square = int(float(square))
                    item.useful_square = int(float(useful_square))
                    item.kitchen = int(float(kitchen))
                elif dt == 'Кімнати':
                    rooms = re.findall(r'(\d+)', html_p.text.strip())[0]
                    item.rooms = int(rooms)
                elif dt == 'Поверховість':
                    floor, max_floor = re.findall(r'(\d+)', html_p.text.strip())
                    item.floor = int(floor)
                    item.max_floor = int(max_floor)

        secondary_params = html_panel.find('dl', class_='ov-params-list_secondary').find_all('dd')
        external_id = secondary_params[4].text.strip()

        html_desc_container = html_parser.find('div', class_='description-container')
        desc = html_desc_container.find('dd', class_='description-text').text.strip()
        address = html_desc_container.find_all('dd', class_='description-text')[-1].text.strip().rsplit(',', maxsplit=1)[0]

        html_images = html_parser.find('div', {'id': 'carousel-offer-generic'})
        for html_img in html_images.find_all('img', class_='fancybox')[:self._max_images]:
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
            [Locations[l] for l in self._config.get('locations', [])]
        ).price(
            minimum=self._config.get('price', {}).get('min', 0),
            maximum=self._config.get('price', {}).get('max', 0),
        ).rooms(
            self._config.get('rooms', [])
        ).square(
            minimum=self._config.get('square', 0)
        )
