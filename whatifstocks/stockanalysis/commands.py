"""stockanalysis commands."""
from datetime import date
from decimal import Decimal
from time import sleep

import click
from flask import current_app as app
from flask.cli import with_appcontext
import requests

from whatifstocks.extensions import db
from whatifstocks.stockanalysis.models import (Exchange, Stock,
                                               StockMonthlyPrice)


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
@click.option('--sleep-time-secs', default=0,
              help='Sleep time (secs)')
@with_appcontext
def import_stocks_and_monthly_prices(
        exchange_symbol, ticker_symbols_file, sleep_time_secs):
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

    monthly_prices_url_pattern = app.config[
        'STOCKANALYSIS_MONTHLY_PRICES_URL_PATTERN']
    alphavantage_apikey = app.config['STOCKANALYSIS_ALPHAVANTAGE_APIKEY']

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

            monthly_prices_url = monthly_prices_url_pattern.format(
                ticker_symbol, exchange_symbol, alphavantage_apikey)

            r = requests.get(monthly_prices_url)
            monthly_prices_json = r.json()

            try:
                monthly_prices_raw = (
                    monthly_prices_json['Monthly Adjusted Time Series'])
            except KeyError:
                raise click.BadParameter(
                    'URL: "{0}"; Stock: "{1}"; json: {2}'.format(monthly_prices_url, ticker_symbol, monthly_prices_json))

            stock = Stock.create(
                exchange=exch, ticker_symbol=ticker_symbol)

            for close_at_raw, prices_raw in monthly_prices_raw.items():
                close_at = date(*[
                    int(n.lstrip('0')) for n in close_at_raw.split('-')])
                close_price = Decimal(prices_raw['5. adjusted close'])

                smp = StockMonthlyPrice(
                    stock=stock, close_at=close_at,
                    close_price=close_price)

                db.session.add(smp)

            db.session.commit()

            if sleep_time_secs:
                sleep(sleep_time_secs)
