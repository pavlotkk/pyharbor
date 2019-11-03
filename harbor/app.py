from harbor.db.base import create_session
from harbor.db.models import DbApartment, DbApartmentPhoto
from harbor.provider.manager import provider_manager


class App:
    def __init__(self):
        self.db = create_session()

    def load(self):
        print('start loading')
        loaded_items = provider_manager.load()

        for i in loaded_items:
            exists = self.db.query(
                self.db.query(
                    DbApartment
                ).filter(
                    DbApartment.external_id == i.external_id,
                    DbApartment.provider == i.provider
                ).exists()
            ).scalar()

            if exists:
                continue

            db_apartment = DbApartment()
            db_apartment.external_id = i.external_id
            db_apartment.provider = i.provider
            db_apartment.rel_url = i.rel_url
            db_apartment.address = i.address
            db_apartment.rooms = i.rooms
            db_apartment.floor = i.floor
            db_apartment.max_floor = i.max_floor
            db_apartment.square = i.square
            db_apartment.useful_square = i.useful_square
            db_apartment.kitchen_square = i.kitchen
            db_apartment.price = i.price
            db_apartment.currency = 'USD'
            db_apartment.description = i.description
            db_apartment.is_new = True
            db_apartment.is_starred = False

            for l in i.photos:
                db_apartment.photos.append(
                    DbApartmentPhoto(absolute_photo_url=l)
                )

            self.db.add(db_apartment)
            self.db.flush()

            print(f'New item:\n{i}')

        self.db.commit()
