import logging
import time

from app.core.logging import log_event
from app.llm.openai_client import OpenAILLM

VALID_CATEGORIES = [
    "Billing",
    "Refund",
    "Account Access",
    "Cancellation",
    "General Inquiry"
]

CLASSIFICATION_PROMPT = """
You are a support interaction classification engine. Your task is to classify a single user message into EXACTLY ONE category.

Categories:
1. Billing — questions about invoices, charges, pricing, or payment methods.
   Example: "Why was I charged twice?", "How much is the subscription?"
2. Refund — requests to return money, dispute charges, or issue credits.
   Example: "I want my money back", "There’s a disputed charge on my account"
3. Account Access — login issues, password reset, multi-factor authentication (MFA), or locked accounts.
   Example: "I can't log in", "Forgot password", "MFA code not working"
4. Cancellation — subscription cancellation, plan downgrade, or account closure.
   Example: "Cancel my subscription", "Close my account"
5. General Inquiry — anything that does not fit the above categories.
   Example: "Where can I find tutorials?", "How does the app work?"

Rules:
- Always select ONLY ONE category, even if multiple intents appear.
- Determine the PRIMARY intent: the category that best represents the user's main concern.
- Do not return explanations, examples, or extra text — only the exact category name.
- Be strict: do not invent new categories or abbreviations.

Output:
- Return ONLY the category name (Billing, Refund, Account Access, Cancellation, or General Inquiry).
"""

class ClassificationService:
    def __init__(self):
        self.llm = OpenAILLM()
        self.logger = logging.getLogger("supportlens.classification")

    def classify(self, user_message: str, bot_response: str) -> str:
        combined = f"""
                Customer Message:
                {user_message}

                Bot Response:
                {bot_response}
            """
        start = time.time()

        try:
            category = self.llm.chat(CLASSIFICATION_PROMPT, combined)
        except Exception as exc:
            fallback = self._heuristic_category(user_message)
            log_event(
                self.logger,
                logging.WARNING,
                "llm_classification_failed",
                error=str(exc),
                fallback_category=fallback,
                message_preview=user_message[:120],
            )
            return fallback, int((time.time() - start) * 1000)

        if category not in VALID_CATEGORIES:
            fallback = self._heuristic_category(user_message)
            log_event(
                self.logger,
                logging.WARNING,
                "llm_unexpected_classification",
                raw_category=category,
                fallback_category=fallback,
                message_preview=user_message[:120],
            )
            return fallback, int((time.time() - start) * 1000)

        response_time = int((time.time() - start) * 1000)
        return category, response_time

    @staticmethod
    def _heuristic_category(user_message: str) -> str:
        text = user_message.lower()

        if any(token in text for token in ["refund", "money back", "credit", "disputed charge"]):
            return "Refund"
        if any(token in text for token in ["cancel", "downgrade", "close my account", "closure"]):
            return "Cancellation"
        if any(token in text for token in ["password", "log in", "login", "mfa", "locked", "account access"]):
            return "Account Access"
        if any(token in text for token in ["invoice", "charged", "billing", "payment", "plan cost", "pricing"]):
            return "Billing"
        return "General Inquiry"
