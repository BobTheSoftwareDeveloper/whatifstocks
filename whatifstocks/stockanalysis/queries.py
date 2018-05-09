"""Stock analysis queries."""
from sqlalchemy import select, text
from sqlalchemy.sql import func

from whatifstocks.extensions import db
from whatifstocks.stockanalysis.models import (Stock, Exchange,
                                               IndustrySector,
                                               StockYearlyPrice)


def yeartoyear_price_percent_change_query(exchange_id, from_year, to_year):
    """Query percent change in prices between from and to year."""
    s_t = Stock.__table__.alias('stock')
    is_t = IndustrySector.__table__.alias('industry_sector')
    syp_from_t = StockYearlyPrice.__table__.alias('syp_from')
    syp_to_t = StockYearlyPrice.__table__.alias('syp_to')

    avg_close_price_from_col = text(
        'ROUND(CAST(prices_from.avg_close_price AS numeric), 2) '
        'AS avg_close_price_from')
    avg_close_price_to_col = text(
        'ROUND(CAST(prices_to.avg_close_price AS numeric), 2) '
        'AS avg_close_price_to')
    price_change_percent_col = text(
        'ROUND('
        '('
        '(prices_to.avg_close_price - prices_from.avg_close_price) / '
        'CASE prices_from.avg_close_price '
        'WHEN 0.0 THEN 0.01 '
        'ELSE prices_from.avg_close_price '
        'END) '
        '* 100.0, '
        '2) AS price_change_percent')

    stock_cols = [
        s_t.c.id, s_t.c.title, s_t.c.ticker_symbol, s_t.c.exchange_id,
        s_t.c.industry_sector_id]
    industry_sector_cols = [is_t.c.id, is_t.c.title]

    select_cols = (
        stock_cols + industry_sector_cols + [
            avg_close_price_from_col, avg_close_price_to_col,
            price_change_percent_col])

    prices_from_sq = (
        select(
            [
                syp_from_t.c.stock_id.label('stock_id'),
                func.avg(syp_from_t.c.close_price).label('avg_close_price')],
            use_labels=True)
            .select_from(syp_from_t)
            .where(func.extract('year', syp_from_t.c.close_at) == from_year)
            .group_by(syp_from_t.c.stock_id)
            .alias('prices_from'))

    prices_to_sq = (
        select(
            [
                syp_to_t.c.stock_id.label('stock_id'),
                func.avg(syp_to_t.c.close_price).label('avg_close_price')],
            use_labels=True)
            .select_from(syp_to_t)
            .where(func.extract('year', syp_to_t.c.close_at) == to_year)
            .group_by(syp_to_t.c.stock_id)
            .alias('prices_to'))

    from_query = (
        s_t.join(is_t, s_t.c.industry_sector_id == is_t.c.id)
           .join(prices_from_sq, s_t.c.id == prices_from_sq.c.stock_id)
           .join(prices_to_sq, s_t.c.id == prices_to_sq.c.stock_id))

    group_by_cols = (
        stock_cols + industry_sector_cols + [
            text('avg_close_price_from'), text('avg_close_price_to'),
            prices_from_sq.c.avg_close_price, prices_to_sq.c.avg_close_price])

    query = (
        select(select_cols, use_labels=True)
            .select_from(from_query)
            .where(s_t.c.exchange_id == exchange_id)
            .group_by(*group_by_cols)
            .order_by(text('price_change_percent DESC')))

    return query


def yeartoyear_price_percent_change_result(exchange_id, from_year, to_year):
    """Result for percent change in prices between from and to year."""
    query = yeartoyear_price_percent_change_query(
        exchange_id, from_year, to_year)

    # Craft the results such that each row gets populated with proper
    # model instances for all the models in question, plus the score.
    result = (
        db.session
          .query(
              Stock, IndustrySector,
              'avg_close_price_from', 'avg_close_price_to',
              'price_change_percent')
          .from_statement(query))

    return result
