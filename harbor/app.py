import logging
from typing import TYPE_CHECKING, Tuple, Optional

from harbor.db.base import create_session
from harbor.db.models import DbApartment, DbApartmentPhoto
from harbor.provider.manager import provider_manager

if TYPE_CHECKING:
    from harbor.provider.base import PropertyItem

logger = logging.getLogger(__name__)


class App:
    def __init__(self):
        self.db = create_session()

    def load(self):
        logger.info("Start loading data")
        loaded_items = provider_manager.load()

        for item in loaded_items:
            db_apartment = self._create_or_none(item)

            if db_apartment:
                self.db.add(db_apartment)
                self.db.flush()

                logger.info(f'New property item:\n{item}')

        self.db.commit()
        logger.info("Finish loading data")

    def _create_or_none(self, data: 'PropertyItem') -> Optional[DbApartment]:
        exists = self.db.query(
            self.db.query(
                DbApartment
            ).filter(
                DbApartment.external_id == data.external_id,
                DbApartment.provider == data.provider
            ).exists()
        ).scalar()

        if exists:
            return None

        db_apartment = DbApartment()
        db_apartment.external_id = data.external_id
        db_apartment.provider = data.provider
        db_apartment.rel_url = data.rel_url
        db_apartment.address = data.address
        db_apartment.rooms = data.rooms
        db_apartment.floor = data.floor
        db_apartment.max_floor = data.max_floor
        db_apartment.square = data.square
        db_apartment.useful_square = data.useful_square
        db_apartment.kitchen_square = data.kitchen
        db_apartment.price = data.price
        db_apartment.currency = 'USD'
        db_apartment.description = data.description
        db_apartment.is_new = True
        db_apartment.is_starred = False

        for link in data.photos:
            db_apartment.photos.append(
                DbApartmentPhoto(absolute_photo_url=link)
            )

        return db_apartment
