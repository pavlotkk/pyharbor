from datetime import datetime
from typing import List, Optional, Union

import sqlalchemy as sa
from sqlalchemy.orm import relationship

from harbor.db.base import Base
from harbor.utils import trim_content


class DbApartment(Base):
    __tablename__ = 'apartments'

    row_id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    external_id = sa.Column(sa.Text, nullable=False)
    provider = sa.Column(sa.Text, nullable=False)
    rel_url = sa.Column(sa.Text, nullable=True)
    absolute_url = sa.Column(sa.Text, nullable=True)
    address = sa.Column(sa.Text, nullable=True)
    rooms = sa.Column(sa.Integer, nullable=False, default=0)
    floor = sa.Column(sa.Integer, nullable=False, default=0)
    max_floor = sa.Column(sa.Integer, nullable=False, default=0)
    square = sa.Column(sa.Integer, nullable=False, default=0)
    useful_square = sa.Column(sa.Integer, nullable=False, default=0)
    kitchen_square = sa.Column(sa.Integer, nullable=False, default=0)
    price = sa.Column(sa.Integer, nullable=False)
    description = sa.Column(sa.Text, nullable=True)
    create_dts = sa.Column(sa.DateTime, nullable=False, default=datetime.utcnow)

    is_new = sa.Column(sa.Boolean, nullable=False, default=False)
    is_liked = sa.Column(sa.Boolean, nullable=False, default=False)

    telegram_mgs_id = sa.Column(sa.Text, nullable=True)

    photos = relationship("DbApartmentPhoto", back_populates="apartment")

    @property
    def short_description(self) -> str:
        return trim_content(self.description)

    def get_telegram_message_ids(self) -> List[str]:
        if not self.telegram_mgs_id:
            return []
        return self.telegram_mgs_id.split(',')

    def set_telegram_message_ids(self, message_id: Optional[Union[List[str], str]]):
        if not message_id:
            self.telegram_mgs_id = None
            return

        ids = self.get_telegram_message_ids()

        if isinstance(message_id, str):
            ids.append(message_id)
        else:
            ids.extend(message_id)

        self.telegram_mgs_id = ','.join((list(set(ids))))


class DbApartmentPhoto(Base):
    __tablename__ = 'apartments_photos'

    row_id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    apartment_id = sa.Column(sa.Integer, sa.ForeignKey('apartments.row_id'))
    absolute_photo_url = sa.Column(sa.Text, nullable=False)
    apartment = relationship("DbApartment", back_populates="photos")
