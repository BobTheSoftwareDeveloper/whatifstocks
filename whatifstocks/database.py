"""Database module.

Includes the SQLAlchemy database object and DB-related utilities.
"""
from datetime import datetime

from sqlalchemy.orm import relationship

from .compat import basestring
from .extensions import db

# Alias common SQLAlchemy names
Column = db.Column
relationship = relationship


def iter_pages(
        pages, page, left_edge=2, left_current=2, right_current=5,
        right_edge=2):
    """From Flask-SQLAlchemy's Pagination class. Modified to accept `pages`
    and `page` params, so that it can operate without being coupled to a
    specific query object (i.e. so it can work with a custom raw SQL query,
    not just with an SQLAlchemy ORM query).

    Iterates over the page numbers in the pagination.  The four
    parameters control the thresholds how many numbers should be produced
    from the sides.  Skipped page numbers are represented as `None`.
    """
    last = 0
    for num in range(1, pages + 1):
        if num <= left_edge or \
           (num > page - left_current - 1 and \
            num < page + right_current) or \
           num > pages - right_edge:
            if last + 1 != num:
                yield None
            yield num
            last = num


class CRUDMixin(object):
    """
    convenience methods for CRUD.

    Mixin that adds convenience methods for CRUD (create, read, update,
    delete) operations.
    """

    @classmethod
    def create(cls, **kwargs):
        """Create a new record and save it the database."""
        instance = cls(**kwargs)
        return instance.save()

    def update(self, commit=True, **kwargs):
        """Update specific fields of a record."""
        for attr, value in kwargs.items():
            setattr(self, attr, value)
        return commit and self.save() or self

    def save(self, commit=True):
        """Save the record."""
        db.session.add(self)
        if commit:
            db.session.commit()
        return self

    def delete(self, commit=True):
        """Remove the record from the database."""
        db.session.delete(self)
        return commit and db.session.commit()


class Model(CRUDMixin, db.Model):
    """Base model class that includes CRUD convenience methods."""

    __abstract__ = True


# From Mike Bayer's "Building the app" talk
# https://speakerdeck.com/zzzeek/building-the-app
class SurrogatePK(object):
    """
    Primary key mixin.

    A mixin that adds a surrogate integer 'primary key' column named
    ``id`` to any declarative-mapped class.
    """

    __table_args__ = {'extend_existing': True}

    id = Column(db.Integer, primary_key=True)

    @classmethod
    def get_by_id(cls, record_id):
        """Get record by ID."""
        if any(
                (isinstance(record_id, basestring) and record_id.isdigit(),
                 isinstance(record_id, (int, float))),
        ):
            return cls.query.get(int(record_id))
        return None


def reference_col(tablename, nullable=False, pk_name='id', **kwargs):
    """Column that adds primary key foreign key reference.

    Usage: ::

        category_id = reference_col('category')
        category = relationship('Category', backref='categories')
    """
    return Column(
        db.ForeignKey('{0}.{1}'.format(tablename, pk_name)),
        nullable=nullable, **kwargs)


class Titled(object):
    """Mixin that adds ``title`` field."""

    title = Column(db.String(255), nullable=False, default='')


class TimeStamped(object):
    """Mixin that adds ``created_at`` and ``updated_at`` fields."""

    created_at = Column(db.DateTime())
    updated_at = Column(db.DateTime())


def update_timestamps_before_insert(mapper, connection, target):
    """Event listener callback to update created / updated fields."""
    ts = datetime.utcnow()
    target.created_at = ts
    target.updated_at = ts


def update_timestamps_before_update(mapper, connection, target):
    """Event listener callback to update the updated at field."""
    target.updated_at = datetime.utcnow()
