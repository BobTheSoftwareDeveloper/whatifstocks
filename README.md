# What If Stocks

Based on a start and end period, and a pool of stocks and historical prices, calculates what would have been the best stocks to invest in for the given period.


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
