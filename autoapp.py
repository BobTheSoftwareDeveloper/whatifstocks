# -*- coding: utf-8 -*-
"""Create an application instance."""
from flask.helpers import get_debug_flag

from whatifstocks.app import create_app
from whatifstocks.settings import DevConfig, ProdConfig

CONFIG = DevConfig if get_debug_flag() else ProdConfig

app = create_app(CONFIG)
