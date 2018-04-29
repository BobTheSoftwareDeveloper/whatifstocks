"""The app module, containing the app factory function."""
from flask import Flask, render_template

from whatifstocks import commands
from whatifstocks.assets import assets
from whatifstocks.extensions import (db, debug_toolbar, mail, mailgun,
                                     migrate)
from whatifstocks.public.views import blueprint as public_bp
from whatifstocks.settings import ProdConfig
from whatifstocks.stockanalysis.commands import stockanalysis as stockanalysis_cmds
from whatifstocks.stockanalysis.views import blueprint as stockanalysis_bp
from whatifstocks.utils import send_mail


def create_app(config_object=ProdConfig):
    """An application factory.

    As explained here:
    http://flask.pocoo.org/docs/patterns/appfactories/.

    :param config_object: The configuration object to use.
    """
    app = Flask(__name__)
    app.config.from_object(config_object)
    register_loggers(app)
    register_extensions(app)
    register_blueprints(app)
    register_jinja_env(app)
    register_errorhandlers(app)
    register_shellcontext(app)
    register_commands(app)
    return app


def register_extensions(app):
    """Register Flask extensions."""
    assets.init_app(app)
    mail.init_app(app)
    mailgun.init_app(app)
    db.init_app(app)
    debug_toolbar.init_app(app)
    migrate.init_app(app, db)

    return None


def register_blueprints(app):
    """Register Flask blueprints."""
    app.register_blueprint(public_bp)
    app.register_blueprint(stockanalysis_bp)
    return None


def register_jinja_env(app):
    """Register Jinja environment."""
    app.jinja_env.add_extension('jinja2.ext.do')


def register_errorhandlers(app):
    """Register error handlers."""
    def render_error(error):
        """Render error template."""
        # If a HTTPException, pull the `code` attribute; default to 500
        error_code = getattr(error, 'code', 500)
        return render_template('{0}.html'.format(error_code)), error_code
    for errcode in [401, 404, 500]:
        app.errorhandler(errcode)(render_error)
    return None


def register_loggers(app):
    import logging
    from logging.handlers import SMTPHandler

    log_formatter = logging.Formatter(
        '%(levelname)s %(asctime)s %(message)s',
        '[%Y-%m-%d %H:%M:%S]')

    if len(app.logger.handlers):
        app.logger.handlers[0].setFormatter(log_formatter)

    if not app.debug:
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(log_formatter)
        app.logger.addHandler(stream_handler)
        app.logger.setLevel(logging.INFO)

        if (
                app.config['ADMINS'] and
                not app.config.get('MAILGUN_LOGGING_RECIPIENT')):
            smtp_handler_args = {}
            if app.config.get('MAIL_USERNAME'):
                smtp_handler_args['credentials'] = (
                    app.config['MAIL_USERNAME'],
                    app.config['MAIL_PASSWORD'])
                smtp_handler_args['secure'] = ()

            mail_handler = SMTPHandler(
                (app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
                app.config['MAIL_DEFAULT_SENDER'],
                app.config['ADMINS'],
                ('[%s] Error report' % app.config['SITE_NAME']),
                **smtp_handler_args)
            mail_handler.setLevel(logging.ERROR)
            mail_handler.setFormatter(
                logging.Formatter(app.config['ERROR_MAIL_FORMAT']))
            app.logger.addHandler(mail_handler)

        app.logger.info('whatifstocks startup')


def register_shellcontext(app):
    """Register shell context objects."""
    def shell_context():
        """Shell context objects."""
        return {'db': db}

    app.shell_context_processor(shell_context)


def register_commands(app):
    """Register Click commands."""
    app.cli.add_command(commands.test)
    app.cli.add_command(commands.lint)
    app.cli.add_command(commands.clean)
    app.cli.add_command(commands.urls)

    app.cli.add_command(stockanalysis_cmds)
