import re
from typing import List

from bs4 import BeautifulSoup, Tag

from harbor.provider.base import PropertyItem


def parse_page_items_links(html: str) -> List[str]:
    html_parser = BeautifulSoup(html, features='html.parser')
    html_items = html_parser.find_all('div', class_='catalog-item')
    if not html_items:
        return []

    return [hi.find('div', class_='catalog-item__img').a['href'] for hi in html_items]


def parse_item(html: str, max_images: int = None) -> PropertyItem:
    item = PropertyItem()

    html_parser = BeautifulSoup(html, features='html.parser')
    html_panel = html_parser.find('div', class_='ov-params-col')
    html_price = html_panel.find('div', class_='ov-price')
    currency = html_price.find('span', class_='ov-price-currency').contents[0].string.strip()
    price = 0
    if currency != '$':
        html_currency_table = html_panel.find('table', class_='ov-price-box__other-curr-table')
        for html_tr in html_currency_table.find_all('tr'):
            other_currency = html_tr.find('span', class_='ov-price-box__other-curr').contents[0].string.strip()
            if other_currency == '$':
                price = html_tr.find('span', class_='ov-price-box__other-curr-val').contents[0].string.strip()
                price = int(''.join(price.split()))
    else:
        price = html_price.contents[0].string.strip()
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
                square, useful_square, kitchen = re.findall(r'([0-9]+\.*[0-9]*)', html_p.text.strip())
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
    for html_img in html_images.find_all('img', class_='fancybox')[:max_images]:
        img_src = html_img['src']
        item.photos.append(img_src)

    item.external_id = external_id
    item.address = address
    item.price = price
    item.description = desc

    return item
