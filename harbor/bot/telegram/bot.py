import logging
import traceback
from typing import Union, List

from harbor.bot.telegram.client import BotClient, BotAction
from harbor.db.models import DbApartment, DbApartmentPhoto
from harbor.db.service import DbService

logger = logging.getLogger()
ChatId = Union[str, int]


class TelegramBot:
    def __init__(self, api_token: str, main_chat_id: ChatId):
        self._client = BotClient(api_token, main_chat_id)
        self._db = DbService()

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

    def remove_broken_messages(self):
        apts = self._db.get_partially_sent_messages_to_telegram()
        if not apts:
            return

        logger.info(f"Remove {len(apts)} broken telegram messages")
        for apt in apts:
            self._client.delete_apartment_message(apt)
            self._db.remove_telegram_messages(apt)

    def post_new_apartments(self):
        logger.info("Publish new apartments to Bot")
        apts = self._db.get_new_apartments(2)
        for apt in apts:
            self.post_apartment(apt)

    def post_apartment(self, apartment: DbApartment) -> List[str]:
        photos = apartment.photos  # type: List[DbApartmentPhoto]
        message_media_ids = self._client.post_apartment_photos(photos)
        self._db.add_telegram_apartment_photo_messages(apartment.row_id, [str(m) for m in message_media_ids])

        message_description_id = self._client.post_apartment_description(apartment)
        self._db.add_telegram_apartment_description_message(apartment.row_id, str(message_description_id))

        return [str(m) for m in message_media_ids] + [str(message_description_id)]

    def _like_action_handler(self, message_id: int, apt_id: int):
        apartment = self._db.get_apartment_by_id(apt_id)

        if not apartment:
            return

        self._client.update_apartment_message(message_id, apartment)

        self._db.set_is_liked(apartment.row_id)

    def _dislike_action_handler(self, message_id: int, apt_id: int):
        apartment = self._db.get_apartment_by_id(apt_id)
        if not apartment:
            return

        self._client.delete_apartment_message(apartment)

        self._db.remove_telegram_messages(apartment)

    def _error_action_handler(self, e):
        logger.error('telegram - {}'.format(str(e)))
        traceback.print_exc()
        self.restart_polling()
