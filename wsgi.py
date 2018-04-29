import os
import sys

wsgi_dir = os.path.abspath(os.path.dirname(__file__))  # This directory

activate_this = os.path.abspath(os.path.join(
    wsgi_dir, 'env/bin/activate_this.py'))

with open(activate_this) as source_file:
    exec(source_file.read())

sys.path.insert(0, wsgi_dir)

from werkzeug.contrib.fixers import ProxyFix

from autoapp import app

app.wsgi_app = ProxyFix(app.wsgi_app)

if __name__ == '__main__':
    app.run()
