import time

import click

from harbor import conf
from harbor.app import App
from harbor.db import base as dbbase


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
def run():
    app = App()
    while True:
        app.load()
        time.sleep(conf.UPDATE_FREQUENCY)


if __name__ == "__main__":
    cli()
