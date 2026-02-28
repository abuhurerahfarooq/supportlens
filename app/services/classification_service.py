from app.llm.openai_client import OpenAILLM
import time

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

    def classify(self, user_message: str, bot_response: str) -> str:
        combined = f"""
                Customer Message:
                {user_message}

                Bot Response:
                {bot_response}
            """
        start = time.time()

        category = self.llm.chat(CLASSIFICATION_PROMPT, combined)

        if category not in VALID_CATEGORIES:
            return "General Inquiry"
        
        response_time = int((time.time() - start) * 1000)
        return category, response_time
