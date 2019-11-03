from datetime import datetime

import sqlalchemy as sa
from sqlalchemy.orm import relationship, backref

from harbor.db.base import Base


class DbApartment(Base):
    __tablename__ = 'apartments'

    row_id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    external_id = sa.Column(sa.Text, nullable=False)
    provider = sa.Column(sa.Text, nullable=False)
    rel_url = sa.Column(sa.Text, nullable=True)
    address = sa.Column(sa.Text, nullable=True)
    rooms = sa.Column(sa.Integer, nullable=False, default=0)
    floor = sa.Column(sa.Integer, nullable=False, default=0)
    max_floor = sa.Column(sa.Integer, nullable=False, default=0)
    square = sa.Column(sa.Integer, nullable=False, default=0)
    useful_square = sa.Column(sa.Integer, nullable=False, default=0)
    kitchen_square = sa.Column(sa.Integer, nullable=False, default=0)
    price = sa.Column(sa.Integer, nullable=False)
    currency = sa.Column(sa.Text, nullable=False)
    description = sa.Column(sa.Text, nullable=True)
    create_dts = sa.Column(sa.DateTime, nullable=False, default=datetime.utcnow)

    is_new = sa.Column(sa.Boolean, nullable=False, default=False)
    is_starred = sa.Column(sa.Boolean, nullable=False, default=False)

    telegram_mgs_id = sa.Column(sa.Text, nullable=True)


class DbApartmentPhoto(Base):
    __tablename__ = 'apartments_photos'

    row_id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    apartment_id = sa.Column(sa.Integer, sa.ForeignKey('apartments.row_id'))
    absolute_photo_url = sa.Column(sa.Text, nullable=False)
    actor = relationship("DbApartment", backref=backref("photos", uselist=True))
