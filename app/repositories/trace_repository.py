from app.models.trace import Trace
from app.core.extensions import db

class TraceRepository:

    @staticmethod
    def create(trace: Trace):
        db.session.add(trace)
        db.session.commit()
        return trace

    @staticmethod
    def get_all(category=None):
        query = Trace.query
        if category:
            query = query.filter_by(category=category)
        return query.order_by(Trace.timestamp.desc()).all()

    @staticmethod
    def get_all_raw():
        return Trace.query.all()