"""Extensions module.

Each extension is initialized in the app factory located in app.py.
"""
from flask_debugtoolbar import DebugToolbarExtension
from flask_mail import Mail
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from whatifstocks.mailgun_extension import Mailgun

db = SQLAlchemy()
mail = Mail()
mailgun = Mailgun()
migrate = Migrate()
debug_toolbar = DebugToolbarExtension()
