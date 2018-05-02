"""Views related to stockanalysis."""
from flask import Blueprint

from whatifstocks.stockanalysis.models import Exchange


blueprint = Blueprint('stockanalysis', __name__, static_folder='../static')
