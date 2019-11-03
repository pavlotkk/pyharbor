from typing import Optional, List


class RequestHandler:
    def handle_on_request_start(self):
        pass


class PropertyProvider(RequestHandler):
    def __init__(self, host: str):
        self._host = host

    def load(self) -> List['PropertyItem']:
        raise NotImplemented()


class PropertyItem:
    def __init__(self, source: str, rel_url: str):
        self.source = source
        self.rel_url = rel_url
        self.address: Optional[str] = None
        self.rooms: int = 0
        self.floor: int = 0
        self.max_floor: int = 0
        self.square: int = 0
        self.useful_square: int = 0
        self.kitchen: int = 0
        self.price: int = 0
        self.external_id: Optional[str] = None
        self.description: Optional[str] = None
        self.photos: List[str] = []

    @property
    def short_description(self) -> str:
        if not self.description:
            return ''

        max_words = 30
        words = self.description.split(maxsplit=max_words + 1)
        total_words = len(words)
        if total_words < max_words:
            max_words = total_words
        return ' '.join(words[:max_words - 1]) + '...'

    def __repr__(self):
        return f'<Flat external_id={self.external_id} ' \
               f'address="{self.address}" ' \
               f'rooms={self.rooms} ' \
               f'floor={self.floor}/{self.max_floor} ' \
               f'square={self.square}/{self.useful_square}/{self.kitchen} ' \
               f'price={self.price}>'
