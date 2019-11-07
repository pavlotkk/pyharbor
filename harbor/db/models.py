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

    is_liked = sa.Column(sa.Boolean, nullable=False, default=False)

    photos = relationship("DbApartmentPhoto", back_populates="apartment")
    telegram = relationship('DbTelegram', back_populates='apartment', uselist=False)

    @property
    def short_description(self) -> str:
        return trim_content(self.description)

    @provider
    def is_new(self):
        return False


class DbApartmentPhoto(Base):
    __tablename__ = 'apartments_photos'

    row_id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    apartment_id = sa.Column(sa.Integer, sa.ForeignKey('apartments.row_id'))
    absolute_photo_url = sa.Column(sa.Text, nullable=False)
    apartment = relationship("DbApartment", back_populates="photos")


class DbTelegram(Base):
    __tablename__ = 'telegram_messages'

    row_id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    apartment_id = sa.Column(sa.Integer, sa.ForeignKey('apartments.row_id'))
    mgs_ids = sa.Column(sa.Text, nullable=True)

    photo_sent_dts = sa.Column(sa.DateTime, nullable=True)
    description_sent_dts = sa.Column(sa.DateTime, nullable=True)

    apartment = relationship('DbApartment', back_populates='telegram', uselist=False)

    def get_message_ids(self) -> List[str]:
        if not self.mgs_ids:
            return []
        return self.mgs_ids.split(',')

    def set_message_ids(self, message_id: Optional[Union[List[str], str]]):
        if not message_id:
            self.mgs_ids = None
            return

        ids = self.get_message_ids()

        if isinstance(message_id, str):
            ids.append(message_id)
        else:
            ids.extend(message_id)

        self.mgs_ids = ','.join((list(set(ids))))
