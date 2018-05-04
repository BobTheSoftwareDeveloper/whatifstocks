"""stockanalysis commands."""
import click
from flask.cli import with_appcontext

from whatifstocks.stockanalysis.models import Exchange, Stock


@click.group()
def stockanalysis():
    """Manage stockanalysis."""


@stockanalysis.command()
@click.option('--exchange-symbol', prompt=True,
              help='Exchange symbol')
@click.option('--title', prompt=True,
              help='Exchange title')
@with_appcontext
def create_exchange(exchange_symbol, title):
    """Create an exchange."""
    if (Exchange.query
                .filter_by(exchange_symbol=exchange_symbol)
                .first()):
        raise click.BadParameter('Exchange "{0}" already exists'.format(
            exchange_symbol))

    exch = Exchange.create(exchange_symbol=exchange_symbol, title=title)
    click.echo('Created: {0}'.format(exch))


@stockanalysis.command()
@click.option('--exchange-symbol', prompt=True,
              help='Exchange symbol')
@click.option('--ticker-symbols-file', type=click.File('r'),
              help='Stock tickers text file')
@with_appcontext
def import_stocks_and_monthly_prices(
        exchange_symbol, ticker_symbols_file):
    """Import stocks and monthly prices."""
    if not ticker_symbols_file:
        raise click.BadParameter(
            '--ticker-symbols-file option is required')

    exch = (Exchange.query
                    .filter_by(exchange_symbol=exchange_symbol)
                    .first())

    if not exch:
        raise click.BadParameter('Exchange "{0}" not found'.format(
            exchange_symbol))

    ticker_symbols_raw = ticker_symbols_file.readlines()
    ticker_symbols = [l.replace('\n', '') for l in ticker_symbols_raw]

    click.echo('{0} ticker symbols to process'.format(len(ticker_symbols)))

    with \
            click.progressbar(
                ticker_symbols,
                label='Importing stocks and monthly prices') \
            as bar:
        for ticker_symbol in bar:
            if (Stock.query
                     .filter_by(
                         exchange=exch,
                         ticker_symbol=ticker_symbol)
                     .first()):
                raise click.BadParameter(
                    'Stock "{0}" already exists'.format(ticker_symbol))

            stock = Stock.create(
                exchange=exch, ticker_symbol=ticker_symbol)
