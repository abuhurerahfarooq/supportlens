from app.repositories.trace_repository import TraceRepository
from app.models.trace import Trace
from app.services.classification_service import ClassificationService
from collections import defaultdict

VALID_CATEGORIES = [
    "Billing",
    "Refund",
    "Account Access",
    "Cancellation",
    "General Inquiry"
]

class TraceService:

    def __init__(self):
        self.repo = TraceRepository()
        self.classifier = ClassificationService()

    def create_trace(self, user_message, bot_response):
        category,response_time = self.classifier.classify(user_message, bot_response)

        trace = Trace(
            user_message=user_message,
            bot_response=bot_response,
            category=category,
            response_time_ms=response_time
        )

        return self.repo.create(trace)

    def list_traces(self, category=None):
        return self.repo.get_all(category)

    def analytics(self):
        traces = self.repo.get_all_raw()
        total = len(traces)

        breakdown = {}
        for cat in VALID_CATEGORIES:
            cat_traces = [t for t in traces if t.category == cat]
            count = len(cat_traces)
            avg_response = round(
                sum(t.response_time_ms for t in cat_traces) / count, 2
            ) if count else 0
            breakdown[cat] = {
                "count": count,
                "percentage": round((count / total * 100), 2) if total else 0,
                "average_response_time_ms": avg_response
            }

        avg = round(
            sum(t.response_time_ms for t in traces) / total, 2
        ) if total else 0

        return {
            "total_traces": total,
            "average_response_time_ms": avg,
            "breakdown": breakdown
        }

    def analytics_trends(self, category=None):
        traces = self.repo.get_all_raw()

        if category:
            traces = [t for t in traces if t.category == category]

        buckets = defaultdict(list)
        for trace in traces:
            day = trace.timestamp.strftime("%Y-%m-%d")
            buckets[day].append(trace)

        points = []
        for day in sorted(buckets.keys()):
            day_traces = buckets[day]
            avg_response = round(
                sum(t.response_time_ms for t in day_traces) / len(day_traces), 2
            ) if day_traces else 0
            points.append({
                "date": day,
                "count": len(day_traces),
                "average_response_time_ms": avg_response
            })

        return {
            "category": category or "All",
            "total_points": len(points),
            "points": points
        }
