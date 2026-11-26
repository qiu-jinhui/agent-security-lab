from benchmarks.pii.span_matcher import (
    aggregate_person_name_parts
)

from app.guardrails.validators.payment_card import (
    validate_payment_card
)


def test_first_and_last_name_aggregation():

    text = "Contact John Smith today."

    predictions = {
        ("PERSON_NAME_PART", 8, 12),
        ("PERSON_NAME_PART", 13, 18)
    }

    result = aggregate_person_name_parts(
        predictions,
        text
    )

    assert result == {
        ("PERSON", 8, 18)
    }


def test_single_name_part_is_preserved():

    text = "Contact John today."

    predictions = {
        ("PERSON_NAME_PART", 8, 12)
    }

    result = aggregate_person_name_parts(
        predictions,
        text
    )

    assert result == predictions


def test_names_separated_by_punctuation_not_merged():

    text = "Contact John, Smith today."

    predictions = {
        ("PERSON_NAME_PART", 8, 12),
        ("PERSON_NAME_PART", 14, 19)
    }

    result = aggregate_person_name_parts(
        predictions,
        text
    )

    assert result == predictions


def test_valid_payment_card():

    assert validate_payment_card(
        "4111111111111111"
    ) is True


def test_invalid_payment_card():

    assert validate_payment_card(
        "4111111111111112"
    ) is False


def test_non_numeric_payment_card():

    assert validate_payment_card(
        "payment card"
    ) is False
