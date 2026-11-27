import pytest

from app.security.authorization import (
    ToolAuthorizationEngine
)

from app.security.tool_gateway import (
    ToolExecutionGateway
)

from app.tools.argument_schemas import TOOL_ARGUMENT_SCHEMAS

@pytest.fixture
def execution_counter():
    return {"count": 0}


@pytest.fixture
def tools(execution_counter):

    def get_weather(city):
        execution_counter["count"] += 1
        return {
            "city": city,
            "temperature": 25
        }

    def send_email(to, subject):
        execution_counter["count"] += 1
        return {"sent": True}

    return {
        "get_weather": get_weather,
        "send_email": send_email
    }


@pytest.fixture
def gateway(tools):

    engine = ToolAuthorizationEngine(
        allowed_tools_by_role={
            "user": {"get_weather"},
            "operator": {"get_weather", "send_email"}
        },
        approval_required_tools={"send_email"}
    )

    return ToolExecutionGateway(
        authorization_engine=engine,
        tools=tools,
        argument_schemas=TOOL_ARGUMENT_SCHEMAS
    )


def test_authorized_tool_executes(
    gateway,
    execution_counter
):

    result = gateway.execute(
        role="user",
        tool_name="get_weather",
        arguments={"city": "Tokyo"}
    )

    assert result["status"] == "EXECUTED"
    assert result["result"]["city"] == "Tokyo"
    assert execution_counter["count"] == 1


def test_unauthorized_tool_never_executes(
    gateway,
    execution_counter
):

    result = gateway.execute(
        role="user",
        tool_name="send_email",
        arguments={
            "to": "test@example.com",
            "subject": "Hello"
        }
    )

    assert result["status"] == "DENIED"
    assert execution_counter["count"] == 0


def test_approval_required_tool_never_executes(
    gateway,
    execution_counter
):

    result = gateway.execute(
        role="operator",
        tool_name="send_email",
        arguments={
            "to": "test@example.com",
            "subject": "Hello"
        }
    )

    assert result["status"] == "PENDING_APPROVAL"
    assert execution_counter["count"] == 0


def test_unknown_tool_never_executes(
    gateway,
    execution_counter
):

    result = gateway.execute(
        role="admin",
        tool_name="delete_database",
        arguments={}
    )

    assert result["status"] == "DENIED"
    assert execution_counter["count"] == 0


def test_missing_role_never_executes(
    gateway,
    execution_counter
):

    result = gateway.execute(
        role=None,
        tool_name="get_weather",
        arguments={"city": "Tokyo"}
    )

    assert result["status"] == "DENIED"
    assert execution_counter["count"] == 0


def test_invalid_arguments_do_not_execute(
    gateway,
    execution_counter
):

    result = gateway.execute(
        role="user",
        tool_name="get_weather",
        arguments={}
    )

    assert result["status"] == "INVALID_ARGUMENTS"
    assert execution_counter["count"] == 0

def test_operator_email_requires_approval_and_never_executes(
    gateway,
    execution_counter
):

    result = gateway.execute(
        role="operator",
        tool_name="send_email",
        arguments={
            "to": "john.smith@test.com",
            "subject": "Hello"
        }
    )

    assert result["status"] == "PENDING_APPROVAL"
    assert execution_counter["count"] == 0
