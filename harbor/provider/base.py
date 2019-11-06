from typing import Optional, List


class PropertyProvider:
    def __init__(self, base_url: str, **kwargs):
        """
        Create instance
        :param host: service base host
        :param kwargs:
            * max_items_to_load (default 25) - maximum items to load
            * max_images_to_load (default 5) - maximum item's images to load
            * price_min - lowest price (default 0) in USD
            * price_max - higher price (default 0) in USD
            * rooms - list of rooms number, ex. [2, 3]
            * square - minimum square
        """
        self._base_url = base_url

        self._max_items = kwargs.get('max_items_to_load', 25)
        self._max_images = kwargs.get('max_images_to_load', 5)
        self._price_min = kwargs.get('price_min', 0)
        self._price_max = kwargs.get('price_max', 0),
        self._rooms = kwargs.get('rooms', [])
        self._min_square = kwargs.get('min_square', 0)

    def load(self) -> List['PropertyItem']:
        raise NotImplemented()


class PropertyItem:
    def __init__(self, provider: str = None, rel_url: str = None):
        self.provider = provider
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
