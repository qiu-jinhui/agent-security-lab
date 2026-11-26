import pytest
from app.security.authorization import ToolAuthorizationEngine


REGISTERED_TOOLS = {
    "get_weather",
    "get_air_quality",
    "send_email",
    "transfer_funds",
}


@pytest.fixture
def engine():
    return ToolAuthorizationEngine(
        allowed_tools_by_role={
            "user": {
                "get_weather",
                "get_air_quality",
            },
            "operator": {
                "get_weather",
                "get_air_quality",
                "send_email",
            },
            "admin": REGISTERED_TOOLS,
        },
        approval_required_tools={
            "send_email",
            "transfer_funds",
        },
    )


def test_user_can_call_weather(engine):

    result = engine.authorize(
        role="user",
        tool_name="get_weather",
        registered_tools=REGISTERED_TOOLS,
    )

    assert result.action == "ALLOW"


def test_user_cannot_transfer_funds(engine):

    result = engine.authorize(
        role="user",
        tool_name="transfer_funds",
        registered_tools=REGISTERED_TOOLS,
    )

    assert result.action == "DENY"


def test_operator_requires_approval_for_email(engine):

    result = engine.authorize(
        role="operator",
        tool_name="send_email",
        registered_tools=REGISTERED_TOOLS,
    )

    assert result.action == "REQUIRE_APPROVAL"


def test_admin_requires_approval_for_transfer(engine):

    result = engine.authorize(
        role="admin",
        tool_name="transfer_funds",
        registered_tools=REGISTERED_TOOLS,
    )

    assert result.action == "REQUIRE_APPROVAL"


def test_unknown_tool_is_denied(engine):

    result = engine.authorize(
        role="admin",
        tool_name="delete_database",
        registered_tools=REGISTERED_TOOLS,
    )

    assert result.action == "DENY"


def test_missing_role_is_denied(engine):

    result = engine.authorize(
        role=None,
        tool_name="get_weather",
        registered_tools=REGISTERED_TOOLS,
    )

    assert result.action == "DENY"


def test_unknown_role_is_denied(engine):

    result = engine.authorize(
        role="guest",
        tool_name="get_weather",
        registered_tools=REGISTERED_TOOLS,
    )

    assert result.action == "DENY"