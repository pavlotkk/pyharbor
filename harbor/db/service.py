from threading import Lock
from typing import TYPE_CHECKING, List, Optional

from harbor.db.base import create_session
from harbor.db.models import DbApartment

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

    def get_new_apartments(self, limit: int = 0) -> List[DbApartment]:
        with _lock:
            query = self._session.query(
                DbApartment
            ).options(
                joinedload(DbApartment.photos)
            ).filter(
                DbApartment.is_new
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
            ).filter(
                DbApartment.row_id == apt_id
            ).first()

            if data:
                self._session.expunge_all()

            return data

    def set_is_not_new(self, apt_id: int, telegram_m_ids: List[str] = None):
        with _lock:
            apt = self._session.query(DbApartment).filter(DbApartment.row_id == apt_id).first()
            apt.set_telegram_message_ids(telegram_m_ids)
            apt.is_new = False
            self._session.commit()

            self._session.expunge_all()

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

    def set_disliked(self, apt_id: int):
        with _lock:
            self._session.query(
                DbApartment
            ).filter(
                DbApartment.row_id == apt_id
            ).update(
                {DbApartment.is_liked: True, DbApartment.telegram_mgs_id: None}
            )
            self._session.commit()
