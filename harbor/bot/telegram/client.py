import threading
from enum import Enum
from typing import Union, List, TYPE_CHECKING

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from telegram.ext import Updater, CallbackQueryHandler, CallbackContext

if TYPE_CHECKING:
    from harbor.db.models import DbApartment, DbApartmentPhoto

ChatId = Union[str, int]


class BotAction(Enum):
    Error = 'error'
    Like = 'like'
    Dislike = 'dislike'


class BotClient:
    def __init__(self, api_token: str, main_chat_id: ChatId):
        self._main_chat_id = main_chat_id

        self._updater = Updater(token=api_token, use_context=True)
        self._dispatcher = self._updater.dispatcher

        self._dispatcher.add_handler(
            CallbackQueryHandler(
                self._error_decorator(self._apartment_action_callback), pattern=r'^like|^dislike'
            )
        )
        self._dispatcher.add_error_handler(self._error_callback)

        self._polling_thread = None

        self._handlers = {
            BotAction.Like: None,
            BotAction.Dislike: None,
            BotAction.Error: None
        }

    def start_polling(self):
        """
        Start receiving events
        """
        if not self._polling_thread:
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
        if self._polling_thread:
            self._updater.stop()
        self._polling_thread = None

    def add_handler(self, action: BotAction, callback):
        self._handlers[action] = callback

    def post_apartment_photos(self, photos: List['DbApartmentPhoto']) -> List[int]:
        media = [InputMediaPhoto(p.absolute_photo_url) for p in photos]
        photo_messages = self._updater.bot.send_media_group(
            chat_id=self._main_chat_id,
            media=media,
            timeout=20,
        )
        message_ids = [m.message_id for m in photo_messages]

        return message_ids

    def post_apartment_description(self, apartment: 'DbApartment') -> int:
        star_btn = InlineKeyboardButton(
            text="👍",
            callback_data=f'{BotAction.Like.value};{apartment.row_id}'
        )
        skip_btn = InlineKeyboardButton(
            text="Не интересно",
            callback_data=f'{BotAction.Dislike.value};{apartment.row_id}'
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

        return response.message_id

    def update_apartment_message(self, message_id: int, apartment: 'DbApartment') -> int:
        response = self._updater.bot.edit_message_text(
            chat_id=self._main_chat_id,
            message_id=message_id,
            text=f'{apartment.price}\n'
                 f'{apartment.square} / {apartment.useful_square} / {apartment.kitchen_square} m2\n'
                 f'{apartment.address}\n'
                 f'{apartment.short_description}\n\n'
                 f'{apartment.absolute_url}',
            reply_markup=None,
            timeout=20,
        )

        return response.message_id

    def delete_apartment_message(self, apartment: 'DbApartment'):
        tel_message_ids = apartment.telegram.get_message_ids()
        for m_id in tel_message_ids:
            self._updater.bot.delete_message(self._main_chat_id, int(m_id), timeout=20)

    def _apartment_action_callback(self, update: Update, context: CallbackContext):
        query_data = update.callback_query.data  # type: str
        query_action, query_value = tuple(query_data.split(';'))
        message_id = update.callback_query.message.message_id
        query_action = BotAction(query_action)
        query_value = int(query_value)

        if query_action == BotAction.Like:
            self._on_like_handler(message_id, query_value)
        elif query_action == BotAction.Dislike:
            self._on_dislike_handler(message_id, query_value)

    def _error_decorator(self, callback):
        def decorator(update: 'Update', context: 'CallbackContext', *args):
            try:
                callback(update, context)
            except Exception as e:
                self._on_error_handler(e)
        return decorator

    def _error_callback(self, update: 'Update', context: 'CallbackContext'):
        self._on_error_handler(context.error)

    def _on_error_handler(self, error):
        callback = self._handlers.get(BotAction.Error, None)
        if callback:
            callback(error)

    def _on_like_handler(self, message_id: int, obj_id: int):
        callback = self._handlers.get(BotAction.Like, None)
        if callback:
            callback(message_id, obj_id)

    def _on_dislike_handler(self, message_id: int, obj_id: int):
        callback = self._handlers.get(BotAction.Dislike, None)
        if callback:
            callback(message_id, obj_id)
