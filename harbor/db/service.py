from datetime import datetime
from threading import Lock
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import or_

from harbor.db.base import create_session
from harbor.db.models import DbApartment, DbTelegram

if TYPE_CHECKING:
    from sqlalchemy.orm import SqlSession, joinedload

_lock = Lock()


class DbService:
    def __init__(self, session: 'SqlSession' = None):
        self._session = session

        if not self._session:
            self._session = create_session()

    def is_apartment_exists(self, provider: str, apt_id: int) -> bool:
        with _lock:
            return self._session.query(
                self._session.query(
                    DbApartment
                ).filter(
                    DbApartment.external_id == apt_id,
                    DbApartment.provider == provider
                ).exists()
            ).scalar()

    def add_apartment(self, apt: DbApartment) -> DbApartment:
        with _lock:
            self._session.add(apt)
            self._session.commit()
            self._session.expunge_all()
            return apt

    def get_partially_sent_messages_to_telegram(self):
        with _lock:
            data = self._session.query(
                DbApartment
            ).options(
                joinedload(DbApartment.photos),
                joinedload(DbApartment.telegram),
            ).filter(
                or_(
                    DbApartment.telegram.photo_sent_dts == None,
                    DbApartment.telegram.description_sent_dts == None
                )
            ).all()

            self._session.expunge_all()

            return data

    def get_new_apartments(self, limit: int = 0) -> List[DbApartment]:
        with _lock:
            query = self._session.query(
                DbApartment
            ).options(
                joinedload(DbApartment.photos),
                joinedload(DbApartment.telegram),
            ).filter(
                DbApartment.telegram.photo_sent_dts != None,
                DbApartment.telegram.description_sent_dts != None
            ).order_by(
                DbApartment.create_dts
            )

        if not limit:
            query = query.limit(limit)

        data = query.all()
        self._session.expunge_all()

        return data

    def get_apartment_by_id(self, apt_id: int) -> Optional[DbApartment]:
        with _lock:
            data = self._session.query(
                DbApartment
            ).options(
                joinedload(DbApartment.photos),
                joinedload(DbApartment.telegram),
            ).filter(
                DbApartment.row_id == apt_id
            ).first()

            if data:
                self._session.expunge_all()

            return data

    def set_is_liked(self, apt_id: int):
        with _lock:
            self._session.query(
                DbApartment
            ).filter(
                DbApartment.row_id == apt_id
            ).update(
                {DbApartment.is_liked: True}
            )
            self._session.commit()

    def add_telegram_apartment_photo_messages(self, apt_id: int, message_ids: List['str']):
        with _lock:
            apt = self._session.query(DbApartment).filter(DbApartment.row_id == apt_id).first()  # type: DbApartment
            telegram = apt.telegram  # type: DbTelegram
            if telegram:
                telegram.set_message_ids(message_ids)
                telegram.photo_sent_dts = datetime.utcnow()
            else:
                telegram = DbTelegram(apartment_id=apt_id, photo_sent_dts=datetime.utcnow())
                telegram.set_message_ids(message_ids)
                self._session.add(telegram)
            self._session.commit()

    def add_telegram_apartment_description_message(self, apt_id: int, message_description_id: str):
        with _lock:
            apt = self._session.query(DbApartment).filter(DbApartment.row_id == apt_id).first()  # type: DbApartment
            telegram = apt.telegram  # type: DbTelegram
            if telegram:
                telegram.set_message_ids(message_description_id)
                telegram.description_sent_dts = datetime.utcnow()
            else:
                telegram = DbTelegram(apartment_id=apt_id, description_sent_dts=datetime.utcnow())
                telegram.set_message_ids(message_description_id)
                self._session.add(telegram)
            self._session.commit()

    def remove_telegram_messages(self, apt: DbApartment):
        with _lock:
            self._session.query(
                DbTelegram
            ).filter(
                DbTelegram.apartment_id == apt.row_id
            ).delete()
            self._session.commit()
