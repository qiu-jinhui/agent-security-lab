import pytest

from app.security.authorization import (
    ToolAuthorizationEngine
)

from app.security.context import ExecutionContext

from app.security.resource_authorization import (
    ResourceAuthorizationEngine
)

from app.security.tool_gateway import (
    ToolExecutionGateway
)

from app.tools.argument_schemas import (
    TOOL_ARGUMENT_SCHEMAS
)


@pytest.fixture
def execution_counter():
    return {"count": 0}


@pytest.fixture
def resource_gateway(execution_counter):

    def get_customer_profile(customer_id):
        execution_counter["count"] += 1

        return {
            "customer_id": customer_id,
            "name": "Mock Customer"
        }

    tools = {
        "get_customer_profile": get_customer_profile
    }

    authorization = ToolAuthorizationEngine(
        allowed_tools_by_role={
            "user": {"get_customer_profile"}
        }
    )

    resource_authorizer = ResourceAuthorizationEngine(
        access_control={
            ("TENANT_A", "USER_001"): {
                "CUSTOMER_001"
            },
            ("TENANT_A", "USER_002"): {
                "CUSTOMER_002"
            }
        }
    )

    return ToolExecutionGateway(
        authorization_engine=authorization,
        tools=tools,
        argument_schemas=TOOL_ARGUMENT_SCHEMAS,
        resource_authorizer=resource_authorizer,
        resource_protected_tools={
            "get_customer_profile"
        }
    )


def test_user_can_access_owned_customer(
    resource_gateway,
    execution_counter
):

    context = ExecutionContext(
        user_id="USER_001",
        tenant_id="TENANT_A",
        role="user"
    )

    result = resource_gateway.execute(
        role="user",
        tool_name="get_customer_profile",
        arguments={
            "customer_id": "CUSTOMER_001"
        },
        context=context
    )

    assert result["status"] == "EXECUTED"
    assert execution_counter["count"] == 1


def test_user_cannot_access_other_customer(
    resource_gateway,
    execution_counter
):

    context = ExecutionContext(
        user_id="USER_001",
        tenant_id="TENANT_A",
        role="user"
    )

    result = resource_gateway.execute(
        role="user",
        tool_name="get_customer_profile",
        arguments={
            "customer_id": "CUSTOMER_002"
        },
        context=context
    )

    assert result["status"] == "DENIED"
    assert execution_counter["count"] == 0


def test_cross_tenant_access_is_denied(
    resource_gateway,
    execution_counter
):

    context = ExecutionContext(
        user_id="USER_001",
        tenant_id="TENANT_B",
        role="user"
    )

    result = resource_gateway.execute(
        role="user",
        tool_name="get_customer_profile",
        arguments={
            "customer_id": "CUSTOMER_001"
        },
        context=context
    )

    assert result["status"] == "DENIED"
    assert execution_counter["count"] == 0


def test_missing_context_is_denied(
    resource_gateway,
    execution_counter
):

    result = resource_gateway.execute(
        role="user",
        tool_name="get_customer_profile",
        arguments={
            "customer_id": "CUSTOMER_001"
        }
    )

    assert result["status"] == "DENIED"
    assert execution_counter["count"] == 0


def test_llm_cannot_override_tenant_id(
    resource_gateway,
    execution_counter
):

    context = ExecutionContext(
        user_id="USER_001",
        tenant_id="TENANT_A",
        role="user"
    )

    result = resource_gateway.execute(
        role="user",
        tool_name="get_customer_profile",
        arguments={
            "customer_id": "CUSTOMER_001",
            "tenant_id": "TENANT_B"
        },
        context=context
    )

    assert result["status"] == "INVALID_ARGUMENTS"
    assert execution_counter["count"] == 0


def test_role_context_mismatch_is_denied(
    resource_gateway,
    execution_counter
):

    context = ExecutionContext(
        user_id="USER_001",
        tenant_id="TENANT_A",
        role="user"
    )

    result = resource_gateway.execute(
        role="admin",
        tool_name="get_customer_profile",
        arguments={
            "customer_id": "CUSTOMER_001"
        },
        context=context
    )

    assert result["status"] == "DENIED"
    assert execution_counter["count"] == 0

def test_unknown_user_is_denied(
    resource_gateway,
    execution_counter
):

    context = ExecutionContext(
        user_id="UNKNOWN_USER",
        tenant_id="TENANT_A",
        role="user"
    )

    result = resource_gateway.execute(
        role="user",
        tool_name="get_customer_profile",
        arguments={
            "customer_id": "CUSTOMER_001"
        },
        context=context
    )

    assert result["status"] == "DENIED"
    assert execution_counter["count"] == 0

def test_missing_resource_authorizer_denies_execution(
    execution_counter
):

    def get_customer_profile(customer_id):
        execution_counter["count"] += 1
        return {"customer_id": customer_id}

    authorization = ToolAuthorizationEngine(
        allowed_tools_by_role={
            "user": {"get_customer_profile"}
        }
    )

    gateway = ToolExecutionGateway(
        authorization_engine=authorization,
        tools={
            "get_customer_profile": get_customer_profile
        },
        argument_schemas=TOOL_ARGUMENT_SCHEMAS,
        resource_authorizer=None,
        resource_protected_tools={
            "get_customer_profile"
        }
    )

    context = ExecutionContext(
        user_id="USER_001",
        tenant_id="TENANT_A",
        role="user"
    )

    result = gateway.execute(
        role="user",
        tool_name="get_customer_profile",
        arguments={
            "customer_id": "CUSTOMER_001"
        },
        context=context
    )

    assert result["status"] == "DENIED"
    assert execution_counter["count"] == 0

def test_second_user_can_access_own_customer(
    resource_gateway,
    execution_counter
):

    context = ExecutionContext(
        user_id="USER_002",
        tenant_id="TENANT_A",
        role="user"
    )

    result = resource_gateway.execute(
        role="user",
        tool_name="get_customer_profile",
        arguments={
            "customer_id": "CUSTOMER_002"
        },
        context=context
    )

    assert result["status"] == "EXECUTED"
    assert execution_counter["count"] == 1

def test_unknown_tenant_is_denied(
    resource_gateway,
    execution_counter
):

    context = ExecutionContext(
        user_id="USER_001",
        tenant_id="UNKNOWN_TENANT",
        role="user"
    )

    result = resource_gateway.execute(
        role="user",
        tool_name="get_customer_profile",
        arguments={
            "customer_id": "CUSTOMER_001"
        },
        context=context
    )

    assert result["status"] == "DENIED"
    assert execution_counter["count"] == 0