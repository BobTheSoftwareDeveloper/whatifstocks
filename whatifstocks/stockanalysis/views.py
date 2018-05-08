"""Views related to stockanalysis."""
from flask import Blueprint


blueprint = Blueprint('stockanalysis', __name__, static_folder='../static')
