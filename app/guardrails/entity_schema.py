from typing import Any

CANONICAL_ENTITY_TYPES = {
    "PERSON",
    "PERSON_NAME_PART",
    "EMAIL_ADDRESS",
    "PHONE_NUMBER",
    "PAYMENT_CARD",
    "US_SSN",
    "GOVERNMENT_ID",
    "TAX_ID",
    "BANK_ACCOUNT",
    "IBAN",
    "IP_ADDRESS",
    "USERNAME",
    "PASSWORD",
    "API_KEY",
    "ACCESS_TOKEN",
    "RECOVERY_CODE",
    "ADDRESS",
    "DATE_OF_BIRTH",
    "ORGANIZATION",
    "LOCATION",
    "POSTAL_CODE",
    "CARD_CVV"
}

# Model-specific labels -> canonical labels.
ENTITY_TYPE_MAPPING = {
    # Person
    "PERSON": "PERSON",
    "FULL_NAME": "PERSON",
    "FIRST_NAME": "PERSON_NAME_PART",
    "LAST_NAME": "PERSON_NAME_PART",

    # Contact
    "EMAIL": "EMAIL_ADDRESS",
    "EMAIL_ADDRESS": "EMAIL_ADDRESS",
    "PHONE_NUMBER": "PHONE_NUMBER",
    "PHONE NUMBER": "PHONE_NUMBER",

    # Financial
    "CREDIT_CARD": "PAYMENT_CARD",
    "CREDIT CARD NUMBER": "PAYMENT_CARD",
    "PAYMENT_CARD": "PAYMENT_CARD",
    "IBAN_CODE": "IBAN",
    "IBAN": "IBAN",

    # Government identity
    "US_SSN": "US_SSN",
    "NATIONAL_ID_NUMBER": "GOVERNMENT_ID",
    "PASSPORT_NUMBER": "GOVERNMENT_ID",

    # Other sensitive data
    "TAX_ID": "TAX_ID",
    "BANK_ACCOUNT": "BANK_ACCOUNT",
    "CARD_CVV": "CARD_CVV",
    "IP_ADDRESS": "IP_ADDRESS",
    "USERNAME": "USERNAME",
    "PASSWORD": "PASSWORD",
    "API_KEY": "API_KEY",
    "ACCESS_TOKEN": "ACCESS_TOKEN",
    "RECOVERY_CODE": "RECOVERY_CODE",

    # General entities
    "ADDRESS": "ADDRESS",
    "DATE_OF_BIRTH": "DATE_OF_BIRTH",
    "ORGANIZATION": "ORGANIZATION",
    "LOCATION": "LOCATION",
    "POSTAL_CODE": "POSTAL_CODE"
}

def normalize_entity_type(source_entity_type: str) -> str:

    normalized = source_entity_type.strip().upper()

    return ENTITY_TYPE_MAPPING.get(
        normalized,
        normalized
    )

def normalize_entity(
        source_entity_type: str,
        start: int,
        end: int,
        score: float,
        **extra: Any
) -> dict: 

    canonical_type = normalize_entity_type(
        source_entity_type
    )

    return {
        "entity_type": canonical_type,
        "source_entity_type": source_entity_type,
        "start": start,
        "end": end,
        "score": round(float(score), 4),
        **extra
    }