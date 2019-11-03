import click

from harbor.app import App


@click.group()
def cli():
    pass


@cli.command()
def run():
    app = App()
    app.load()


if __name__ == "__main__":
    cli()
