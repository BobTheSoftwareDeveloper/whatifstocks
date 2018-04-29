"""Public section, including homepage."""
from flask import Blueprint, render_template


blueprint = Blueprint('public', __name__, static_folder='../static')


@blueprint.route('/')
def home():
    """Home page."""
    template_vars = {}
    return render_template('public/home.html', **template_vars)
