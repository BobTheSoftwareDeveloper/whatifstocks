"""Public section, including homepage."""
from flask import abort, Blueprint, render_template, request

from whatifstocks.stockanalysis.models import Exchange
from whatifstocks.stockanalysis.queries import yeartoyear_price_percent_change_result


blueprint = Blueprint('public', __name__, static_folder='../static')


@blueprint.route('/')
def home():
    """Home page."""
    exch = None
    from_year = None
    to_year = None
    yeartoyear_price_percent_changes = None

    exchange_symbol_raw = request.args.get('exchange_symbol')
    from_year_raw = request.args.get('from_year')
    to_year_raw = request.args.get('to_year')

    exchanges = Exchange.query.all()
    exchanges_by_symbol = {e.exchange_symbol: e for e in exchanges}

    if exchange_symbol_raw and from_year_raw and to_year_raw:
        try:
            from_year = int(from_year_raw)
        except ValueError:
            abort(404)

        try:
            to_year = int(to_year_raw)
        except ValueError:
            abort(404)

        if exchange_symbol_raw in exchanges_by_symbol:
            exch = exchanges_by_symbol[exchange_symbol_raw]
        else:
            abort(404)

        exchange_id = exch.id

        yeartoyear_price_percent_changes = yeartoyear_price_percent_change_result(
            exchange_id, from_year, to_year)

    template_vars = {
        'exchanges': exchanges,
        'exchange': exch,
        'from_year': from_year,
        'to_year': to_year,
        'yeartoyear_price_percent_changes': yeartoyear_price_percent_changes}

    return render_template('public/home.html', **template_vars)
