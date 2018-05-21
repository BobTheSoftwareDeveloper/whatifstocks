# What If Stocks

Based on a start and end period, and a pool of stocks and historical prices, calculates what would have been the best stocks to invest in for the given period.

Here's a [demo of the app in action](https://whatifstocks.herokuapp.com/).


## Quickstart

First, set your site's secret key as an environment variable. For example, add the following to `.bashrc` or `.bash_profile`:

```sh
export WHATIFSTOCKS_SECRET='something-really-secret'
```

Before running shell commands, set the `FLASK_APP` and `FLASK_DEBUG` environment variables:

```sh
export FLASK_APP=/path/to/autoapp.py
export FLASK_DEBUG=1
```

Then run the following commands to bootstrap your environment:

```sh
git clone user@server.here:/path/to/whatifstocks
cd whatifstocks
pip install -r requirements/dev.txt
flask run
```

You will see a pretty welcome screen.


## DB config and migrations

You must specify the DB credentials before starting the site in normal mode:

```sh
export WHATIFSTOCKS_DATABASE_URI="postgresql://whatifstocks:whatifstocks@localhost:5432/whatifstocks"
```

This is for getting started with migrations (shouldn't need to ever run it, initial migrations are included in the codebase):

```sh
flask db init
```

Each time you need to create a new migration script, run the following:

```sh
flask db migrate
```

Run the following to create or upgrade the DB schema:

```sh
flask db upgrade
```

For a full migration command reference, run `flask db --help`.


## Creating an exchange

To create an exchange that will appear in the "exchanges" drop-down on the front page, use the `create_exchange` command. For example, to create an exchange for Australian stocks:

```sh
flask stockanalysis create_exchange --exchange-symbol="AX" --title="Australian Stock Exchange"
```


## Downloading historical prices

To download historical prices from [Alpha Vantage](https://www.alphavantage.co/), you should register for an Alpha Vantage API key. Then tell whatifstocks what the API key is:

```sh
export WHATIFSTOCKS_STOCKANALYSIS_ALPHAVANTAGE_APIKEY=A1B2C3D4E5F6G7H8
```

You will need a text file that lists the stocks for which you would like to fetch prices. You may find this [ASX stocks list](https://github.com/Jaza/whatifstocks-asx-data/blob/master/asx-stocks.txt) handy to get started.

For example, to download prices for ASX stocks and save them to a CSV:

```sh
flask stockanalysis download_stock_monthly_prices --exchange-symbol="AX" --ticker-symbols-file=/path/to/asx-stocks.txt --monthly-prices-output-file=/path/to/asx-stock-prices.csv
```


## Importing data

To import a list of stocks containing ticker symbols, descriptions, and sector names, use the `import_stocks` command. For example, to import ASX stocks:

```sh
flask stockanalysis import_stocks --exchange-symbol="AX" --company-info-file=- < /path/to/asx-company-info.csv
```

You may find this [ASX company info CSV](https://raw.githubusercontent.com/Jaza/whatifstocks-asx-data/master/asx-company-info.csv) useful to get started.

To import historical prices, use the `import_monthly_prices` command. For example, to import historical ASX prices:

```sh
flask stockanalysis import_monthly_prices --exchange-symbol="AX" --monthly-prices-file=- < /path/to/asx-stock-prices.csv
```

You may find this [ASX stock prices CSV](https://raw.githubusercontent.com/Jaza/whatifstocks-asx-data/master/asx-stock-prices.csv) useful to get started.


## Querying price changes

To see the change in price for all stocks in a given exchange, between two given years, simply go to the front page URL, select an exchange, select a "from year", and select a "to year". You will see all stocks in a table, listed in descending order of price increase.


## Deployment

In your production environment, make sure the `FLASK_DEBUG` environment variable is unset or is set to `0`, so that `ProdConfig` is used.


## Shell

To open the interactive shell, run:

```sh
flask shell
```

By default, you will have access to `app` and `db`.


## Running Tests

To run all tests, run:

```sh
flask test
```
