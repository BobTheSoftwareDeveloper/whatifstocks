"""Application assets."""
from flask_assets import Bundle, Environment

css = Bundle(
    'libs/bootstrap/css/bootstrap.min.css',
    filters='cssmin',
    output='public/css/common.css'
)

js = Bundle(
    'libs/jquery/js/jquery.min.js',
    'libs/bootstrap/js/bootstrap.min.js',
    filters='jsmin',
    output='public/js/common.js'
)

assets = Environment()

assets.register('js_all', js)
assets.register('css_all', css)
