import logging
import threading
import traceback
from typing import Union, List

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from telegram.ext import CommandHandler, Updater, CallbackQueryHandler, CallbackContext

from harbor.db.base import create_session
from harbor.db.models import DbApartment, DbApartmentPhoto

logger = logging.getLogger()
ChatId = Union[str, int]


class TelegramHandler:
    def __init__(self, callback):
        self._callback = callback

    def __call__(self, update: 'Update', context: CallbackContext, *args):
        try:
            self._callback(update, context)
        except Exception as e:
            logger.error('telegram - {}'.format(str(e)))
            traceback.print_exc()


class TelegramBot:
    def __init__(self, api_token: str, main_chat_id: ChatId):
        self._main_chat_id = main_chat_id

        self._updater = Updater(token=api_token, use_context=True)
        self._dispatcher = self._updater.dispatcher
        self._db = create_session()

        self._dispatcher.add_handler(
            CommandHandler('ping', TelegramHandler(self._ping_cmd_handler))
        )
        self._dispatcher.add_handler(
            CallbackQueryHandler(TelegramHandler(self._user_apt_decision_handler), pattern=r'^star|^skip')
        )
        self._dispatcher.add_error_handler(self._error_callback)

        self._polling_thread = None

    def start_polling(self):
        """
        Start receiving events
        """
        self._polling_thread = threading.Thread(target=self._updater.start_polling)
        self._polling_thread.start()

    def idle(self):
        """
        Waiting CTRL+C for exit
        """
        self._updater.idle()

    def stop_polling(self):
        """
        Stop receiving events
        """
        self._db.close()
        self._updater.stop()
        self._polling_thread = None

    def post_all_apartments(self):
        logger.info("Publish data to Bot")
        apts = self._db.query(DbApartment).filter(DbApartment.is_new).limit(2).all()  # type: List[DbApartment]
        for apt in apts:
            ids = self.post_apartment(apt)
            apt.set_telegram_message_ids(ids)
            apt.is_new = False
            self._db.commit()

    def post_apartment(self, apartment: 'DbApartment') -> List[str]:
        photos = apartment.photos  # type: List[DbApartmentPhoto]
        photos = [InputMediaPhoto(p.absolute_photo_url) for p in photos]
        photo_messages = self._updater.bot.send_media_group(
            chat_id=self._main_chat_id,
            media=photos,
            timeout=20,
        )
        message_ids = [str(m.message_id) for m in photo_messages]

        star_btn = InlineKeyboardButton(
            text="👍",
            callback_data=f'star;{apartment.row_id}'
        )
        skip_btn = InlineKeyboardButton(
            text="Не интересно",
            callback_data=f'skip;{apartment.row_id}'
        )

        reply_markup = InlineKeyboardMarkup(
            [[star_btn, skip_btn]]
        )

        response = self._updater.bot.send_message(
            chat_id=self._main_chat_id,
            text=f'{apartment.price}\n'
                 f'{apartment.square} / {apartment.useful_square} / {apartment.kitchen_square} m2\n'
                 f'{apartment.address}\n'
                 f'{apartment.short_description}\n\n'
                 f'{apartment.absolute_url}',
            reply_markup=reply_markup,
            timeout=20,
        )
        message_ids.append(str(response.message_id))

        return message_ids

    def send_pong(self, chat_id: Union[int, str], telegram_user: str):
        self._updater.bot.send_message(chat_id=chat_id, text='pong from user {} in chat {}'.format(
            telegram_user,
            chat_id
        ))
        logger.info('telegram - response - pong')

    def _ping_cmd_handler(self, update: Update, context: CallbackContext):
        """
        Handler for /ping command. This is for tests.
        """
        logger.info('telegram - request - /ping')
        self.send_pong(update.message.chat_id, update.message.from_user.name)

    def _user_apt_decision_handler(self, update: Update, context: CallbackContext):
        logger.info('telegram - request - ask about matching: response = {}'.format(update.callback_query.data))
        query_data = update.callback_query.data  # type: str
        query_type, query_value = tuple(query_data.split(';'))
        message_id = update.callback_query.message.message_id

        apartment = self._db.query(
            DbApartment
        ).filter(
            DbApartment.row_id == int(query_value)
        ).first()  # type: DbApartment
        if not apartment:
            return

        if query_type == 'star':
            response = self._updater.bot.edit_message_text(
                chat_id=self._main_chat_id,
                message_id=message_id,
                text=f'{apartment.price}\n'
                     f'{apartment.square} / {apartment.useful_square} / {apartment.kitchen_square} m2\n'
                     f'{apartment.address}\n'
                     f'{apartment.short_description}\n\n'
                     f'{apartment.absolute_url}',
                reply_markup=None
            )
            apartment.set_telegram_message_ids(str(response.message_id))
            apartment.is_starred = True
        elif query_type == 'skip':
            tel_message_ids = apartment.get_telegram_message_ids()
            for m_id in tel_message_ids:
                self._updater.bot.delete_message(self._main_chat_id, int(m_id))
            apartment.set_telegram_message_ids(None)

        self._db.commit()

    def _get_chat_id(self) -> str:
        """
        Internal method for retrieving target chat it. Will send `System Check` message to current provided channel
        """

        message = self._updater.bot.send_message(chat_id=self._main_chat_id, text='System Check')
        return message.chat_id

    def _error_callback(self, update: 'Update', context):
        logger.error('telegram - {}'.format(str(context.error)))
        traceback.print_exc()
        if self._polling_thread:
            self.stop_polling()
            self.start_polling()
