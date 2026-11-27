TOOL_ARGUMENT_SCHEMAS = {

    "get_weather": {
        "type": "object",
        "properties": {
            "city": {"type": "string"}
        },
        "required": ["city"],
        "additionalProperties": False
    },

    "get_air_quality": {
        "type": "object",
        "properties": {
            "city": {"type": "string"}
        },
        "required": ["city"],
        "additionalProperties": False
    },

    "send_email": {
        "type": "object",
        "properties": {
            "to": {"type": "string"},
            "subject": {"type": "string"}
        },
        "required": ["to", "subject"],
        "additionalProperties": False
    },

    "get_customer_profile": {
        "type": "object",
        "properties": {
            "customer_id": {"type": "string"}
        },
        "required": ["customer_id"],
        "additionalProperties": False
    }
}
