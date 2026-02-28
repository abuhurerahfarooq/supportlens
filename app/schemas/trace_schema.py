def validate_chat_request(data):
    """Validate /chat request payload"""
    if not data:
        raise ValueError("Missing request body")

    if "message" not in data:
        raise ValueError("Missing 'message' field")

    if not isinstance(data["message"], str):
        raise ValueError("Message must be a string")

    if len(data["message"].strip()) == 0:
        raise ValueError("Message cannot be empty")


def validate_trace_request(data):
    """Validate /traces POST request payload"""
    if not data:
        raise ValueError("Missing request body")

    required_fields = ["user_message", "bot_response"]
    for field in required_fields:
        if field not in data:
            raise ValueError(f"Missing '{field}' field")
        if not isinstance(data[field], str):
            raise ValueError(f"'{field}' must be a string")
        if len(data[field].strip()) == 0:
            raise ValueError(f"'{field}' cannot be empty")