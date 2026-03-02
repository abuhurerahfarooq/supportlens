import logging
import time
import uuid
from threading import Lock

from flask import Flask, g, jsonify, request
from sqlalchemy import text

from app.api.routes import api_bp
from app.core.config import Config
from app.core.extensions import cors, db
from app.core.logging import configure_logging, log_event
from app.llm.openai_client import OpenAILLM


START_TIME = time.monotonic()
LLM_HEALTH_CACHE = {
    "expires_at": 0.0,
    "result": {
        "configured": False,
        "reachable": None,
        "mode": "fallback",
        "info": "LLM health probe not executed yet",
    },
}
LLM_HEALTH_CACHE_LOCK = Lock()


def create_app():
    configure_logging()
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    cors.init_app(app)

    app.register_blueprint(api_bp, url_prefix="/api")

    logger = logging.getLogger("supportlens.http")

    @app.before_request
    def before_request_logging():
        g.request_start = time.perf_counter()
        g.request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())

    @app.after_request
    def after_request_logging(response):
        request_id = getattr(g, "request_id", str(uuid.uuid4()))
        duration_ms = round((time.perf_counter() - getattr(g, "request_start", time.perf_counter())) * 1000, 2)

        response.headers["X-Request-ID"] = request_id

        if request.path != "/health":
            log_event(
                logger,
                logging.INFO,
                "http_request",
                request_id=request_id,
                method=request.method,
                path=request.path,
                query=request.query_string.decode("utf-8"),
                status_code=response.status_code,
                duration_ms=duration_ms,
                remote_addr=request.headers.get("X-Forwarded-For", request.remote_addr),
                user_agent=request.user_agent.string,
            )

        return response

    @app.get("/health")
    def health():
        db_start = time.perf_counter()
        db_result = {"reachable": False}
        try:
            db.session.execute(text("SELECT 1"))
            db_result["reachable"] = True
            db_result["latency_ms"] = round((time.perf_counter() - db_start) * 1000, 2)
        except Exception as exc:
            db_result["error"] = str(exc)

        llm = OpenAILLM()
        now = time.monotonic()
        ttl = max(1.0, app.config.get("LLM_HEALTH_CACHE_TTL_SECONDS", 30))

        if not llm.is_configured:
            llm_result = {
                "configured": False,
                "reachable": None,
                "mode": "fallback",
                "info": "OPENAI_API_KEY is not set; fallback responses/classification will be used",
            }
        else:
            with LLM_HEALTH_CACHE_LOCK:
                if LLM_HEALTH_CACHE["expires_at"] > now:
                    llm_result = dict(LLM_HEALTH_CACHE["result"])
                    llm_result["cached"] = True
                else:
                    llm_start = time.perf_counter()
                    llm_result = {
                        "configured": True,
                        "reachable": None,
                        "mode": "live",
                        "cached": False,
                    }
                    try:
                        llm.probe()
                        llm_result["reachable"] = True
                        llm_result["latency_ms"] = round((time.perf_counter() - llm_start) * 1000, 2)
                    except Exception as exc:
                        llm_result["reachable"] = False
                        llm_result["error"] = str(exc)
                        llm_result["mode"] = "fallback"

                    LLM_HEALTH_CACHE["result"] = dict(llm_result)
                    LLM_HEALTH_CACHE["expires_at"] = now + ttl

        status = "healthy"
        should_page = False
        can_serve_traffic = db_result["reachable"]

        if not db_result["reachable"]:
            status = "unhealthy"
            should_page = True
        elif llm_result["configured"] and llm_result["reachable"] is False:
            status = "degraded"

        if not llm_result["configured"]:
            status = "degraded"

        body = {
            "status": status,
            "can_serve_traffic": can_serve_traffic,
            "should_page": should_page,
            "uptime_seconds": int(time.monotonic() - START_TIME),
            "checks": {
                "database": db_result,
                "llm": llm_result,
            },
        }

        http_status = 200 if can_serve_traffic else 503

        if http_status != 200:
            log_event(
                logger,
                logging.WARNING,
                "health_check_failed",
                request_id=getattr(g, "request_id", None),
                checks=body["checks"],
                status=status,
            )

        return jsonify(body), http_status

    return app