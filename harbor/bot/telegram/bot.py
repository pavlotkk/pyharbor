import logging
import traceback
from typing import Union, List

from harbor.bot.telegram.client import BotClient, BotAction
from harbor.db.base import create_session
from harbor.db.models import DbApartment, DbApartmentPhoto

logger = logging.getLogger()
ChatId = Union[str, int]


class TelegramBot:
    def __init__(self, api_token: str, main_chat_id: ChatId):
        self._client = BotClient(api_token, main_chat_id)
        self._db = create_session()

        self._client.add_handler(BotAction.Like, self._like_action_handler)
        self._client.add_handler(BotAction.Dislike, self._dislike_action_handler)
        self._client.add_handler(BotAction.Error, self._error_action_handler)

    @classmethod
    def get_default(cls):
        from harbor import conf
        return cls(conf.TELEGRAM_API_KEY, conf.TELEGRAM_CHAT_ID)

    def start_polling(self):
        self._client.start_polling()

    def idle(self):
        self._client.idle()

    def stop_polling(self):
        self._client.stop_polling()

    def restart_polling(self):
        self.stop_polling()
        self.start_polling()

    def post_new_apartments(self):
        logger.info("Publish new apartments to Bot")
        apts = self._get_new_apartments()
        for apt in apts:
            ids = self.post_apartment(apt)
            apt.set_telegram_message_ids(ids)
            apt.is_new = False
            self._db.commit()

    def post_apartment(self, apartment: DbApartment) -> List[str]:
        photos = apartment.photos  # type: List[DbApartmentPhoto]
        message_ids = self._client.post_apartment_message(apartment, photos)

        return [str(m) for m in message_ids]

    def _get_new_apartments(self) -> List[DbApartment]:
        return self._db.query(
            DbApartment
        ).filter(
            DbApartment.is_new
        ).order_by(
            DbApartment.create_dts
        ).limit(
            2
        ).all()

    def _like_action_handler(self, message_id: int, apt_id: int):
        apartment = self._db.query(
            DbApartment
        ).filter(
            DbApartment.row_id == apt_id
        ).first()  # type: DbApartment

        if not apartment:
            return

        self._client.update_apartment_message(message_id, apartment)

        apartment.is_liked = True

        self._db.commit()

    def _dislike_action_handler(self, message_id: int, apt_id: int):
        apartment = self._db.query(
            DbApartment
        ).filter(
            DbApartment.row_id == apt_id
        ).first()  # type: DbApartment
        if not apartment:
            return

        self._client.delete_apartment_message(apartment)

        apartment.set_telegram_message_ids(None)

        self._db.commit()

    def _error_action_handler(self, e):
        logger.error('telegram - {}'.format(str(e)))
        traceback.print_exc()
        self.restart_polling()
