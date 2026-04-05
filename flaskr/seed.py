import click

from .stores import create_store, seed_stores


@click.command("seed")
def seed_db_command():
    seed_stores()
    click.echo("Seeded database.")
