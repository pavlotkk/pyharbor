import logging
import time

import click

from harbor import conf
from harbor.app import App
from harbor.db import base as dbbase
from harbor.utils import GracefulInterruptHandler


logger = logging.getLogger(__name__)


@click.group()
def cli():
    pass


@cli.command()
def drop_db():
    dbbase.drop_all()


@cli.command()
def init_db():
    dbbase.drop_all()
    dbbase.create_all()


@cli.command()
@click.option('--url', prompt='Relative url')
def rieltor(url: str):
    from harbor.provider.service.rieltor import RieltorService
    service = RieltorService.get_default()
    print(service.load_item(url))


@cli.command()
def telegram():
    from harbor.bot.telegram.bot import TelegramBot
    bot = TelegramBot.get_default()
    bot.start_polling()
    bot.idle()


@cli.command()
def run():
    app = App()

    with GracefulInterruptHandler() as exit_handler:
        while True:
            try:
                app.load()
            except Exception as ex:
                logger.exception(ex)
                app.release()
                app = App()

            if exit_handler.released:
                app.release()
                break

            time.sleep(conf.UPDATE_FREQUENCY)


if __name__ == "__main__":
    cli()
