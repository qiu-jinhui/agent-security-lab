from app.guardrails.entity_schema import (
    normalize_entity_type,
    normalize_entity
)


def test_full_name_mapping():

    assert normalize_entity_type(
        "FULL_NAME"
    ) == "PERSON"


def test_first_name_mapping():

    assert normalize_entity_type(
        "FIRST_NAME"
    ) == "PERSON_NAME_PART"


def test_email_mapping():

    assert normalize_entity_type(
        "EMAIL"
    ) == "EMAIL_ADDRESS"


def test_credit_card_mapping():

    assert normalize_entity_type(
        "CREDIT_CARD"
    ) == "PAYMENT_CARD"


def test_unknown_entity_preserved():

    assert normalize_entity_type(
        "CUSTOM_SENSITIVE_ENTITY"
    ) == "CUSTOM_SENSITIVE_ENTITY"


def test_normalized_entity_preserves_source():

    entity = normalize_entity(
        source_entity_type="FULL_NAME",
        start=0,
        end=10,
        score=0.998669
    )

    assert entity["entity_type"] == "PERSON"
    assert entity["source_entity_type"] == "FULL_NAME"
    assert entity["start"] == 0
    assert entity["end"] == 10
    assert entity["score"] == 0.9987
