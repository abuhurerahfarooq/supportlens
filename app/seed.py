from datetime import datetime
from app.models.trace import Trace
from app.core.extensions import db

CATEGORIES = [
    "Billing",
    "Refund",
    "Account Access",
    "Cancellation",
    "General Inquiry"
]

def seed_if_empty():
    if Trace.query.first():
        return

    sample_traces = [
        ("Why am I charged and my account is locked?",
         "Your account may be locked due to an unpaid invoice or a billing issue. Please check your payment method and ensure that your subscription is up to date. If you need further assistance, please provide your account details, and I can help resolve the issue.",
         "Billing", 758),
        ("Can I cancel and get a refund?",
         "Refund eligibility depends on our refund policy. If you cancel within the specified timeframe, you may qualify for a refund. Please check our terms of service or provide your account details for specific assistance.",
         "Cancellation", 706),
        ("I want a refund but can’t log in.",
         "I can help with that! Please provide the email associated with your account, and I’ll assist you in processing your refund. If you’re having trouble logging in, I can also guide you through the password reset process.",
         "Refund", 984),
        ("What are the supported browsers for this platform?",
         "The supported browsers for our SaaS billing platform are:\n\n- Google Chrome (latest version)\n- Mozilla Firefox (latest version)\n- Microsoft Edge (latest version)\n- Safari (latest version)\n\nFor the best experience, please ensure your browser is up to date.",
         "General Inquiry", 787),
        ("Is there a mobile app for Android?",
         "Yes, we have a mobile app available for Android. You can download it from the Google Play Store. If you need assistance with installation or features, feel free to ask!",
         "General Inquiry", 900),
        ("How does the new feature work?",
         "Could you please specify which new feature you are referring to? This will help me provide you with accurate information.",
         "General Inquiry", 979),
        ("Where can I find tutorials for the app?",
         "You can find tutorials for the app in the following places:\n\n1. **Help Center**: Visit our Help Center on the website for comprehensive guides and articles.\n2. **YouTube Channel**: Check our official YouTube channel for video tutorials.\n3. **In-App Resources**: Look for the 'Help' or 'Tutorials' section within the app itself.\n4. **Community Forum**: Join our community forum for user-generated tips and tutorials.\n\nIf you need specific assistance, feel free to ask!",
         "General Inquiry", 728),
        ("I’m thinking of cancelling, what’s the process?",
         "To cancel your subscription, please follow these steps:\n\n1. Log in to your account.\n2. Navigate to the 'Billing' or 'Subscription' section.\n3. Select 'Cancel Subscription.'\n4. Follow the prompts to confirm your cancellation.\n\nIf you need further assistance, feel free to reach out!",
         "Cancellation", 656),
        ("Please close my account permanently.",
         "I can assist you with that. Please confirm your account details (email associated with the account) so I can proceed with the closure.",
         "Cancellation", 891),
        ("Can I downgrade my plan from Premium to Basic?",
         "Yes, you can downgrade your plan from Premium to Basic. Please log in to your account, go to the billing section, and select the option to change your plan. If you need further assistance, feel free to reach out!",
         "Cancellation", 698),
        ("I want to cancel my subscription immediately.",
         "I can help with that. Please provide your account email or username, and I’ll process the cancellation for you.",
         "Cancellation", 777),
        ("How do I reset my account password?",
         "To reset your account password, follow these steps:\n\n1. Go to the login page of the platform.\n2. Click on the 'Forgot Password?' link.\n3. Enter your registered email address and submit.\n4. Check your email for a password reset link.\n5. Follow the instructions in the email to create a new password.\n\nIf you don't receive the email, please check your spam folder or contact support for assistance.",
         "Account Access", 1814),
        ("I can’t receive my MFA code on my phone.",
         "Please check the following:\n\n1. **Signal Strength**: Ensure you have a good mobile signal.\n2. **Phone Number**: Verify that the correct phone number is linked to your account.\n3. **Do Not Disturb**: Check if your phone is in Do Not Disturb mode.\n4. **SMS Block**: Ensure that your carrier isn’t blocking SMS from short codes.\n\nIf the issue persists, try using an alternative method for MFA, such as an authenticator app, or contact support for further assistance.",
         "Account Access", 798),
        ("My account is locked after multiple failed login attempts.",
         "To unlock your account, please follow these steps:\n\n1. Wait for a few minutes, as accounts typically unlock automatically after a short period.\n2. If you still can't access your account, use the 'Forgot Password?' link on the login page to reset your password.\n3. If you need further assistance, please contact our support team directly.\n\nLet me know if you need help with anything else!",
         "Account Access", 947),
        ("I forgot my password and can’t log in.",
         "Please click on the 'Forgot Password?' link on the login page. Follow the instructions to reset your password. If you need further assistance, let me know!",
         "Account Access", 824),
        ("I cancelled my subscription but haven’t received a refund yet.",
         "I’m sorry to hear that. Refunds typically process within 5-10 business days after cancellation. Please check your bank account or payment method. If you still don’t see it, I can help you look into this further. Could you provide your account email or subscription details?",
         "Refund", 997),
        ("Can I get a credit for the month I didn’t use the service?",
         "To determine if you qualify for a credit, please provide the specific month you didn't use the service and any relevant account details. Our policy typically allows for credits under certain conditions.",
         "Refund", 715),
        ("There’s a disputed charge on my account, please refund it.",
         "I can help with that. Please provide the details of the disputed charge, including the amount and the date it was processed. Once I have that information, I can assist you further.",
         "Refund", 708),
        ("I want my money back for last month’s payment.",
         "I can help with that. Please provide your account details and the reason for the refund request, and I'll assist you further.",
         "Refund", 1464),
        ("I see an unexpected fee on my invoice.",
         "I can help with that! Please provide the details of the fee, including the amount and any relevant invoice numbers, so I can investigate further.",
         "Billing", 954),
        ("Is the premium plan more expensive than the standard one?",
         "Yes, the premium plan is more expensive than the standard plan. If you need specific pricing details, please let me know!",
         "Billing", 919),
        ("Can I change my payment method for next month?",
         "Yes, you can change your payment method for next month. Please log into your account, go to the billing section, and update your payment information. If you need further assistance, feel free to ask!",
         "Billing", 794),
        ("Why was I charged $15 twice this month?",
         "You may have been charged twice due to a duplicate subscription or an error in the billing system. Please check your account for any active subscriptions. If everything looks correct, I recommend reaching out to our support team for a detailed review and resolution.",
         "Billing", 871),
    ]

    for user_msg, bot_msg, category, response_time in sample_traces:
        trace = Trace(
            user_message=user_msg,
            bot_response=bot_msg,
            category=category,
            timestamp=datetime.utcnow(),
            response_time_ms=response_time
        )
        db.session.add(trace)

    db.session.commit()