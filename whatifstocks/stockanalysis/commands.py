"""stockanalysis commands."""
from datetime import date
from decimal import Decimal
from time import sleep

import click
from flask import current_app as app
from flask.cli import with_appcontext
import requests
import unicodecsv as csv

from whatifstocks.extensions import db
from whatifstocks.stockanalysis.models import (Exchange, IndustrySector,
                                               Stock, StockYearlyPrice)


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
@click.option('--monthly-prices-output-file', type=click.File('w'),
              help='Monthly prices output file')
@with_appcontext
def download_stock_monthly_prices(
        exchange_symbol, ticker_symbols_file,
        monthly_prices_output_file):
    """Download stock monthly prices."""
    if not ticker_symbols_file:
        raise click.BadParameter(
            '--ticker-symbols-file option is required')

    ticker_symbols_raw = ticker_symbols_file.readlines()
    ticker_symbols = [l.replace('\n', '') for l in ticker_symbols_raw]

    click.echo('{0} ticker symbols to process'.format(len(ticker_symbols)))

    monthly_prices_url_pattern = app.config[
        'STOCKANALYSIS_MONTHLY_PRICES_URL_PATTERN']
    alphavantage_apikey = app.config['STOCKANALYSIS_ALPHAVANTAGE_APIKEY']
    alphavantage_toofrequent_errmsg = (
        'if you would like to have a higher API call volume')
    max_request_tries = 5

    monthly_prices_output_file.write(
        'ticker_symbol,close_at,close_price\n')

    for ticker_symbol in ticker_symbols:
        click.echo('Fetching monthly prices for {0}.{1}'.format(
            ticker_symbol, exchange_symbol))
        monthly_prices_url = monthly_prices_url_pattern.format(
            ticker_symbol, exchange_symbol, alphavantage_apikey)

        is_requested_successfully = False
        request_tries = 0

        while not is_requested_successfully and request_tries < max_request_tries:
            request_tries += 1

            click.echo('Try {0} fetching for {1}.{2}'.format(
                request_tries, ticker_symbol, exchange_symbol))

            r = requests.get(monthly_prices_url)
            monthly_prices_json = r.json()

            try:
                monthly_prices_raw = (
                    monthly_prices_json['Monthly Adjusted Time Series'])
                is_requested_successfully = True
                click.echo('Fetched successfully for {0}.{1}'.format(
                    ticker_symbol, exchange_symbol))
            except KeyError:
                monthly_prices_json_str = str(monthly_prices_json)
                if alphavantage_toofrequent_errmsg in monthly_prices_json_str:
                    click.echo('Failed for {0}.{1}: calling too frequently'.format(
                        ticker_symbol, exchange_symbol))
                    if request_tries < max_request_tries:
                        # Do a little exponential backoff each time
                        # the request fails due to too frequent usage.
                        sleep_secs = 10 ** request_tries
                        click.echo('Sleeping for {0} secs'.format(sleep_secs))
                        sleep(sleep_secs)
                    else:
                        click.echo('Give up on {0}.{1}'.format(
                            ticker_symbol, exchange_symbol))
                else:
                    click.echo(
                        'Failed for {0}.{1}, response was: {2}'.format(
                            ticker_symbol, exchange_symbol,
                            monthly_prices_json_str))

        if is_requested_successfully:
            if monthly_prices_raw:
                for close_at, prices_raw in monthly_prices_raw.items():
                    close_price = prices_raw['5. adjusted close']

                    monthly_prices_output_file.write('{0},{1},{2}\n'.format(
                        ticker_symbol, close_at, close_price))
            else:
                click.echo('No monthly prices returned for {0}.{1]'.format(
                    ticker_symbol, exchange_symbol))

    click.echo('Done!')


@stockanalysis.command()
@click.option('--ticker-symbols-file', type=click.File('r'),
              help='Stock tickers text file')
@click.option('--company-info-input-file', type=click.File('rb'),
              help='Company info input file')
@click.option('--company-info-output-file', type=click.File('w'),
              help='Company info output file')
@with_appcontext
def reduce_company_info_file(
        ticker_symbols_file, company_info_input_file, company_info_output_file):
    """Reduce the company info file."""
    if not ticker_symbols_file:
        raise click.BadParameter(
            '--ticker-symbols-file option is required')
    if not company_info_input_file:
        raise click.BadParameter(
            '--company-info-input-file option is required')
    if not company_info_output_file:
        raise click.BadParameter(
            '--company-info-output-file option is required')

    ticker_symbols_raw = ticker_symbols_file.readlines()
    ticker_symbols = {l.replace('\n', '') for l in ticker_symbols_raw}

    click.echo('{0} ticker symbols to process'.format(len(ticker_symbols)))

    ind_sectors_by_title = {}
    company_info_input_csv = csv.DictReader(
        company_info_input_file, encoding='utf-8-sig')

    company_info_output_file.write(
        'ticker_symbol,title,sector\n')

    for line in company_info_input_csv:
        ticker_symbol = line['ticker_symbol'].strip()
        company_title = line['title'].strip()
        ind_sector_title = line['sector'].strip()

        if ticker_symbol in ticker_symbols:
            company_info_output_file.write('{0},{1},{2}\n'.format(
                ticker_symbol, company_title, ind_sector_title))

    click.echo('Done!')


@stockanalysis.command()
@click.option('--exchange-symbol', prompt=True,
              help='Exchange symbol')
@click.option('--company-info-file', type=click.File('rb'),
              help='Company info file')
@with_appcontext
def import_stocks(exchange_symbol, company_info_file):
    """Import stocks."""
    if not company_info_file:
        raise click.BadParameter(
            '--company-info-file option is required')

    exch = (Exchange.query
                    .filter_by(exchange_symbol=exchange_symbol)
                    .first())

    if not exch:
        raise click.BadParameter('Exchange "{0}" not found'.format(
            exchange_symbol))

    ind_sectors_by_title = {}
    company_info_csv = csv.DictReader(
        company_info_file, encoding='utf-8-sig')

    for line in company_info_csv:
        ticker_symbol = line['ticker_symbol'].strip()
        company_title = line['title'].strip()
        ind_sector_title = line['sector'].strip()

        if not ind_sector_title:
            raise click.BadParameter(
                'Missing sector for {0}'.format(ticker_symbol))

        if ind_sector_title not in ind_sectors_by_title:
            ind_sector = IndustrySector(title=ind_sector_title)
            db.session.add(ind_sector)
            ind_sectors_by_title[ind_sector_title] = ind_sector
        else:
            ind_sector = ind_sectors_by_title[ind_sector_title]

        stock = Stock(
            exchange=exch, ticker_symbol=ticker_symbol,
            title=company_title,
            industry_sector=ind_sector)
        db.session.add(stock)

    db.session.commit()

    click.echo('Done!')


def create_stock_yearly_prices(stock, prices_by_year):
    """Create stock yearly prices."""
    for year, prices in prices_by_year.items():
        close_at = date(year, 1, 1)
        close_price = sum(prices) / Decimal(len(prices))

        syp = StockYearlyPrice(
            stock=stock, close_at=close_at,
            close_price=close_price)

        db.session.add(syp)

    db.session.commit()


@stockanalysis.command()
@click.option('--exchange-symbol', prompt=True,
              help='Exchange symbol')
@click.option('--monthly-prices-file', type=click.File('rb'),
              help='Monthly prices file')
@with_appcontext
def import_monthly_prices(exchange_symbol, monthly_prices_file):
    """Import monthly prices."""
    if not monthly_prices_file:
        raise click.BadParameter(
            '--monthly-prices-file option is required')

    exch = (Exchange.query
                    .filter_by(exchange_symbol=exchange_symbol)
                    .first())

    if not exch:
        raise click.BadParameter('Exchange "{0}" not found'.format(
            exchange_symbol))

    monthly_prices_csv = csv.DictReader(
        monthly_prices_file, encoding='utf-8-sig')

    num_prices = 0

    for i, line in enumerate(monthly_prices_csv):
        num_prices += 1

    click.echo('Monthly prices file scanned, {0} prices in file'.format(
        num_prices))

    monthly_prices_file.seek(0)
    monthly_prices_csv = csv.DictReader(
        monthly_prices_file, encoding='utf-8-sig')

    with click.progressbar(monthly_prices_csv,
                           length=num_prices,
                           label='Importing monthly prices') as bar:
        stock = None
        prices_by_year = {}

        for monthly_price_raw in bar:
            ticker_symbol = monthly_price_raw['ticker_symbol']

            if stock is not None and stock.ticker_symbol != ticker_symbol:
                create_stock_yearly_prices(stock, prices_by_year)
                prices_by_year = {}

            if stock is None or stock.ticker_symbol != ticker_symbol:
                stock = (Stock.query
                              .filter_by(
                                  exchange=exch,
                                  ticker_symbol=ticker_symbol)
                              .first())

            if not stock:
                raise click.BadParameter(
                    'No stock found for ticker symbol "{0}"'.format(
                        ticker_symbol))

            close_at_raw = monthly_price_raw['close_at']
            close_at_year = int(close_at_raw.split('-')[0].lstrip('0'))

            close_price_raw = monthly_price_raw['close_price']
            close_price = Decimal(close_price_raw)

            if close_at_year not in prices_by_year:
                prices_by_year[close_at_year] = []

            prices_by_year[close_at_year].append(close_price)

        create_stock_yearly_prices(stock, prices_by_year)

    click.echo('Done!')
