def get_weather(city: str):
    return {
        "city": city,
        "temperature": 25,
        "condition": "Sunny"
    }


def get_air_quality(city: str):
    return {
        "city": city,
        "aqi": 165,
        "status": "Unhealthy"
    }


def send_email(to: str, subject: str):
    # Simulation only. No real email is sent.
    print(f"[SIMULATED EMAIL] To: {to}")
    return {
        "sent": False,
        "simulated": True,
        "message": "Email execution is simulated"
    }


TOOLS = {
    "get_weather": get_weather,
    "get_air_quality": get_air_quality,
    "send_email": send_email
}
