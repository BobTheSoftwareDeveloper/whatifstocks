from whatifstocks.database import (Model, reference_col, SurrogatePK,
                                   Titled)
from whatifstocks.extensions import db


class Exchange(SurrogatePK, Titled, Model):
    __tablename__ = 'exchange'

    exchange_symbol = db.Column(
        db.String(255), nullable=False, default='')

    stocks = db.relationship(
        'Stock', backref=db.backref('exchange'),
        cascade="all, delete-orphan", lazy='dynamic')

    __table_args__ = (
        db.UniqueConstraint(
            'exchange_symbol', name='_exch_symbol_uc'),)

    def __repr__(self):
        return ((
            'Exchange(id={0}, exchange_symbol="{1}", '
            'title="{2}")').format(
                self.id, self.exchange_symbol, self.title))


class Stock(SurrogatePK, Titled, Model):
    __tablename__ = 'stock'

    ticker_symbol = db.Column(
        db.String(255), nullable=False, default='')
    exchange_id = reference_col('exchange')

    stock_monthly_prices = db.relationship(
        'StockMonthlyPrice', backref=db.backref('stock'),
        cascade="all, delete-orphan", lazy='dynamic')

    __table_args__ = (
        db.UniqueConstraint(
            'exchange_id', 'ticker_symbol',
            name='_stock_eid_symbol_uc'),)


class StockMonthlyPrice(SurrogatePK, Model):
    __tablename__ = 'stock_monthly_price'

    close_at = db.Column(db.Date(), nullable=False)
    close_price = db.Column(db.Numeric(12,4), nullable=False)
    stock_id = reference_col('stock')

    __table_args__ = (
        db.UniqueConstraint(
            'stock_id', 'close_at', name='_smp_sid_price_uc'),)
