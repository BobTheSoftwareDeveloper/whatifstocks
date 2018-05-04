"""Application configuration."""
import ast
import os

os_env = os.environ


class Config(object):
    """Base configuration."""

    SECRET_KEY = os.environ.get(
        'WHATIFSTOCKS_SECRET', 'secret-key')
    APP_DIR = os.path.abspath(os.path.dirname(__file__))  # This directory

    SQLALCHEMY_DATABASE_URI = os_env.get(
        'WHATIFSTOCKS_DATABASE_URI',
        'postgresql://localhost/example')
    ASSETS_DEBUG = False
    DEBUG_TB_ENABLED = False  # Disable Debug toolbar
    DEBUG_TB_INTERCEPT_REDIRECTS = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SITE_NAME = 'What If Stocks'

    ADMINS = (os_env.get('WHATIFSTOCKS_ADMINS')
              and os_env.get('WHATIFSTOCKS_ADMINS').split(',')
              or [])

    MAIL_DEFAULT_SENDER = os_env.get(
        'WHATIFSTOCKS_MAIL_DEFAULT_SENDER',
        'sender@nonexistentemailaddress.com')

    MAIL_SERVER = os_env.get(
        'WHATIFSTOCKS_MAIL_SERVER', 'localhost')
    MAIL_PORT = (
        os_env.get('WHATIFSTOCKS_MAIL_PORT')
        and ast.literal_eval(os_env.get('WHATIFSTOCKS_MAIL_PORT'))
        or 25)
    MAIL_USE_TLS = (
        os_env.get('WHATIFSTOCKS_MAIL_USE_TLS')
        and ast.literal_eval(
            os_env.get('WHATIFSTOCKS_MAIL_USE_TLS'))
        or False)
    MAIL_USE_SSL = (
        os_env.get('WHATIFSTOCKS_MAIL_USE_SSL')
        and ast.literal_eval(
            os_env.get('WHATIFSTOCKS_MAIL_USE_SSL'))
        or False)
    MAIL_USERNAME = os_env.get('WHATIFSTOCKS_MAIL_USERNAME', None)
    MAIL_PASSWORD = os_env.get('WHATIFSTOCKS_MAIL_PASSWORD', None)

    MAILGUN_DOMAIN = os_env.get('WHATIFSTOCKS_MAILGUN_DOMAIN', None)
    MAILGUN_KEY = os_env.get('WHATIFSTOCKS_MAILGUN_KEY', None)

    MAILGUN_LOGGING_SENDER = MAIL_DEFAULT_SENDER
    MAILGUN_LOGGING_RECIPIENT = ADMINS

    MAIL_ERROR_SUBJECT_TEMPLATE = os_env.get(
        'WHATIFSTOCKS_MAIL_ERROR_SUBJECT_TEMPLATE',
        '[{0}] Error report: {1}')

    SESSION_COOKIE_NAME = 'whatifstocks_session'
    REMEMBER_COOKIE_NAME = 'whatifstocks_remember_token'

    ERROR_MAIL_FORMAT = (
        '\n'
        'Message type:       %(levelname)s\n'
        'Location:           %(pathname)s:%(lineno)d\n'
        'Module:             %(module)s\n'
        'Function:           %(funcName)s\n'
        'Time:               %(asctime)s\n'
        '\n'
        'Message:\n'
        '\n'
        '%(message)s\n')

    STOCKANALYSIS_MONTHLY_PRICES_URL_PATTERN = os_env.get(
        'WHATIFSTOCKS_STOCKANALYSIS_MONTHLY_PRICES_URL_PATTERN',
        (
            'https://www.alphavantage.co/query?'
            'function=TIME_SERIES_MONTHLY_ADJUSTED&symbol={0}.{1}&'
            'apikey={2}'))
    STOCKANALYSIS_ALPHAVANTAGE_APIKEY = os_env.get(
        'WHATIFSTOCKS_STOCKANALYSIS_ALPHAVANTAGE_APIKEY',
        'A1B2C3D4E5F6G7H8')


class ProdConfig(Config):
    """Production configuration."""

    ENV = 'prod'
    DEBUG = False
    DEBUG_TB_ENABLED = False  # Disable Debug toolbar


class DevConfig(Config):
    """Development configuration."""

    ENV = 'dev'
    DEBUG = True
    DEBUG_TB_ENABLED = True
    ASSETS_DEBUG = True  # Don't bundle/minify static assets


class TestConfig(Config):
    """Test configuration."""

    TESTING = True
    DEBUG = True
