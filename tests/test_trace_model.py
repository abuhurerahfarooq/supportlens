import uuid
from datetime import datetime

from app.core.extensions import db
from app.models.trace import Trace


def test_trace_model_persists_required_fields(app_ctx):
    trace = Trace(
        user_message="Customer cannot log in",
        bot_response="Please reset your password",
        category="Account Access",
        response_time_ms=450,
    )

    db.session.add(trace)
    db.session.commit()

    saved = Trace.query.one()

    assert saved.user_message == "Customer cannot log in"
    assert saved.bot_response == "Please reset your password"
    assert saved.category == "Account Access"
    assert saved.response_time_ms == 450


def test_trace_model_generates_id_and_timestamp_defaults(app_ctx):
    before = datetime.now()

    trace = Trace(
        user_message="Why was I charged twice?",
        bot_response="I can help you investigate that charge.",
        category="Billing",
        response_time_ms=320,
    )
    db.session.add(trace)
    db.session.commit()

    after = datetime.now()

    parsed_id = uuid.UUID(trace.id)

    assert str(parsed_id) == trace.id
    assert trace.timestamp is not None
    assert before <= trace.timestamp <= after
