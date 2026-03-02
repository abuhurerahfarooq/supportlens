import logging

from flask import Blueprint, g, jsonify, request

from app.core.logging import log_event
from app.schemas.trace_schema import validate_chat_request, validate_trace_request
from app.services.chat_service import ChatService
from app.services.trace_service import TraceService

api_bp = Blueprint("api", __name__)

chat_service = ChatService()
trace_service = TraceService()
logger = logging.getLogger("supportlens.api")


def _request_id():
    return getattr(g, "request_id", None)


def _error_response(message, details, status_code):
    return jsonify({"error": message, "details": details, "request_id": _request_id()}), status_code


def _payload_size_bytes():
    return request.content_length or 0


@api_bp.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json(silent=True) or {}

        try:
            validate_chat_request(data)
        except ValueError as ve:
            return _error_response("Invalid input", str(ve), 400)

        user_message = data["message"]
        log_event(
            logger,
            logging.INFO,
            "chat_request_payload",
            payload_size_bytes=_payload_size_bytes(),
            message_length=len(user_message),
        )
        reply, response_time = chat_service.generate_reply(user_message)

        log_event(
            logger,
            logging.INFO,
            "chat_processed",
            payload_size_bytes=_payload_size_bytes(),
            message_length=len(user_message),
            bot_response_length=len(reply),
            llm_response_time_ms=response_time,
        )

        return jsonify(
            {
                "user_message": user_message,
                "bot_response": reply,
                "response_time_ms": response_time,
                "request_id": _request_id(),
            }
        )

    except Exception as exc:
        log_event(
            logger,
            logging.ERROR,
            "chat_failed",
            request_id=_request_id(),
            error=str(exc),
        )
        return _error_response("Failed to process chat", str(exc), 500)


@api_bp.route("/traces", methods=["POST"])
def create_trace():
    try:
        data = request.get_json(silent=True) or {}
        try:
            validate_trace_request(data)
        except ValueError as ve:
            return _error_response("Invalid input", str(ve), 400)

        user_message = data["user_message"]
        bot_response = data["bot_response"]
        log_event(
            logger,
            logging.INFO,
            "trace_request_payload",
            payload_size_bytes=_payload_size_bytes(),
            user_message_length=len(user_message),
            bot_response_length=len(bot_response),
        )

        trace = trace_service.create_trace(
            user_message=user_message,
            bot_response=bot_response
        )

        log_event(
            logger,
            logging.INFO,
            "trace_created",
            trace_id=trace.id,
            category=trace.category,
            response_time_ms=trace.response_time_ms,
        )

        return (
            jsonify(
                {
                    "id": trace.id,
                    "timestamp": trace.timestamp.isoformat(),
                    "user_message": trace.user_message,
                    "bot_response": trace.bot_response,
                    "category": trace.category,
                    "response_time_ms": trace.response_time_ms,
                    "request_id": _request_id(),
                }
            ),
            201
        )

    except Exception as exc:
        log_event(
            logger,
            logging.ERROR,
            "trace_create_failed",
            request_id=_request_id(),
            error=str(exc)
        )
        return _error_response("Failed to create trace", str(exc), 500)


@api_bp.route("/traces", methods=["GET"])
def get_traces():
    try:
        category = request.args.get("category")
        traces = trace_service.list_traces(category)

        return jsonify(
            [
                {
                    "id": t.id,
                    "timestamp": t.timestamp.isoformat(),
                    "user_message": t.user_message,
                    "bot_response": t.bot_response,
                    "category": t.category,
                    "response_time_ms": t.response_time_ms,
                }
                for t in traces
            ]
        )
    except Exception as exc:
        log_event(
            logger,
            logging.ERROR,
            "traces_fetch_failed",
            request_id=_request_id(),
            error=str(exc)
        )
        return _error_response("Failed to fetch traces", str(exc), 500)


@api_bp.route("/analytics", methods=["GET"])
def analytics():
    try:
        return jsonify(trace_service.analytics())
    except Exception as exc:
        log_event(
            logger,
            logging.ERROR,
            "analytics_failed",
            request_id=_request_id(),
            error=str(exc)
        )
        return _error_response("Failed to fetch analytics", str(exc), 500)


@api_bp.route("/analytics/trends", methods=["GET"])
def analytics_trends():
    try:
        category = request.args.get("category")
        return jsonify(trace_service.analytics_trends(category=category))
    except Exception as exc:
        log_event(
            logger,
            logging.ERROR,
            "analytics_trends_failed",
            request_id=_request_id(),
            error=str(exc)
        )
        return _error_response("Failed to fetch trend analytics", str(exc), 500)


@api_bp.errorhandler(404)
def not_found_error(_error):
    return jsonify({"error": "Endpoint not found", "request_id": _request_id()}), 404


@api_bp.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error", "details": str(error), "request_id": _request_id()}), 500
