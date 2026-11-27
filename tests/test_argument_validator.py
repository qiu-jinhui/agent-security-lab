import pytest

from app.security.argument_validator import (
    ToolArgumentValidator,
    ArgumentValidationError
)

from app.tools.argument_schemas import (
    TOOL_ARGUMENT_SCHEMAS
)


@pytest.fixture
def validator():
    return ToolArgumentValidator()


def test_valid_arguments(validator):

    assert validator.validate(
        "get_customer_profile",
        {"customer_id": "CUSTOMER_001"},
        TOOL_ARGUMENT_SCHEMAS
    )


def test_missing_required_argument(validator):

    with pytest.raises(ArgumentValidationError):
        validator.validate(
            "get_customer_profile",
            {},
            TOOL_ARGUMENT_SCHEMAS
        )


def test_wrong_argument_type(validator):

    with pytest.raises(ArgumentValidationError):
        validator.validate(
            "get_customer_profile",
            {"customer_id": 123},
            TOOL_ARGUMENT_SCHEMAS
        )


def test_extra_argument_rejected(validator):

    with pytest.raises(ArgumentValidationError):
        validator.validate(
            "get_customer_profile",
            {
                "customer_id": "CUSTOMER_001",
                "tenant_id": "TENANT_B"
            },
            TOOL_ARGUMENT_SCHEMAS
        )


def test_empty_string_rejected(validator):

    with pytest.raises(ArgumentValidationError):
        validator.validate(
            "get_customer_profile",
            {"customer_id": "   "},
            TOOL_ARGUMENT_SCHEMAS
        )


def test_invalid_arguments_object(validator):

    with pytest.raises(ArgumentValidationError):
        validator.validate(
            "get_customer_profile",
            ["CUSTOMER_001"],
            TOOL_ARGUMENT_SCHEMAS
        )


def test_unknown_tool_schema_rejected(validator):

    with pytest.raises(ArgumentValidationError):
        validator.validate(
            "unknown_tool",
            {},
            TOOL_ARGUMENT_SCHEMAS
        )


def test_valid_email_arguments(validator):

    assert validator.validate(
        "send_email",
        {
            "to": "john@example.com",
            "subject": "Hello"
        },
        TOOL_ARGUMENT_SCHEMAS
    )
