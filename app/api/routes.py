from flask import Blueprint, request, jsonify, render_template
from app.services.chat_service import ChatService
from app.services.trace_service import TraceService
from app.schemas.trace_schema import validate_chat_request, validate_trace_request

api_bp = Blueprint("api", __name__)

chat_service = ChatService()
trace_service = TraceService()


# ---------------- DASHBOARD ----------------

@api_bp.route("/")
def dashboard():
    try:
        return render_template("dashboard.html")
    except Exception as e:
        return jsonify({"error": "Failed to load dashboard", "details": str(e)}), 500


# ---------------- CHAT ----------------

@api_bp.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.json

        try:
            validate_chat_request(data)
        except ValueError as ve:
            return jsonify({"error": "Invalid input", "details": str(ve)}), 400

        user_message = data["message"]

        reply, response_time = chat_service.generate_reply(user_message)

        return jsonify({
            "user_message": user_message,
            "bot_response": reply,
            "response_time_ms": response_time
        })

    except Exception as e:
        return jsonify({"error": "Failed to process chat", "details": str(e)}), 500


# ---------------- TRACES ----------------

@api_bp.route("/traces", methods=["POST"])
def create_trace():
    try:
        data = request.json
        try:
            validate_trace_request(data)
        except ValueError as ve:
            return jsonify({"error": "Invalid input", "details": str(ve)}), 400

        trace = trace_service.create_trace(
            user_message=data["user_message"],
            bot_response=data["bot_response"]
        )

        return jsonify({
            "id": trace.id,
            "timestamp": trace.timestamp.isoformat(),
            "user_message": trace.user_message,
            "bot_response": trace.bot_response,
            "category": trace.category,
            "response_time_ms": trace.response_time_ms
        }), 201

    except Exception as e:
        return jsonify({"error": "Failed to create trace", "details": str(e)}), 500


@api_bp.route("/traces", methods=["GET"])
def get_traces():
    try:
        category = request.args.get("category")
        traces = trace_service.list_traces(category)

        return jsonify([
            {
                "id": t.id,
                "timestamp": t.timestamp.isoformat(),
                "user_message": t.user_message,
                "bot_response": t.bot_response,
                "category": t.category,
                "response_time_ms": t.response_time_ms
            }
            for t in traces
        ])
    except Exception as e:
        return jsonify({"error": "Failed to fetch traces", "details": str(e)}), 500


# ---------------- ANALYTICS ----------------

@api_bp.route("/analytics", methods=["GET"])
def analytics():
    try:
        return jsonify(trace_service.analytics())
    except Exception as e:
        return jsonify({"error": "Failed to fetch analytics", "details": str(e)}), 500


# ---------------- GLOBAL ERROR HANDLER ----------------

@api_bp.errorhandler(404)
def not_found_error(error):
    return jsonify({"error": "Endpoint not found"}), 404


@api_bp.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error", "details": str(error)}), 500