import json
import random
from pathlib import Path

OUTPUT = Path("datasets/pii/golden_v1.jsonl")

random.seed(42)

samples = []

# Person
people = [
    ("John Smith", "person"),
    ("Jane Doe", "person"),
    ("Michael Brown", "person"),
    ("Emily Johnson", "person"),
    ("Robert Wilson", "person"),
    ("Sarah Miller", "person"),
    ("David Taylor", "person"),
    ("Alice Anderson", "person"),
    ("Daniel Thomas", "person"),
    ("Sophia Martin", "person"),
]

for i, (name, _) in enumerate(people, 1):
    text = f"Contact {name} for further information."
    start = text.index(name)

    samples.append({
        "id": f"pii-person-{i:03d}",
        "text": text,
        "annotations": [{
            "entity_type": "PERSON",
            "start": start,
            "end": start + len(name)
        }],
        "metadata": {
            "category": "person",
            "source": "synthetic",
            "difficulty": "easy"
        }
    })


# Email
emails = [
    "john.smith@example.com",
    "jane.doe@example.org",
    "support123@example.net",
    "alice@example.com",
    "admin.team@example.org",
    "user_2026@example.net",
    "david.wilson@example.com",
    "security@example.org",
    "contact.us@example.net",
    "test.user@example.com",
]

for i, email in enumerate(emails, 1):
    text = f"Please contact us at {email}."
    start = text.index(email)

    samples.append({
        "id": f"pii-email-{i:03d}",
        "text": text,
        "annotations": [{
            "entity_type": "EMAIL_ADDRESS",
            "start": start,
            "end": start + len(email)
        }],
        "metadata": {
            "category": "email",
            "source": "synthetic",
            "difficulty": "easy"
        }
    })


# Phone
phones = [
    "+1-415-555-0132",
    "415-555-0132",
    "+44 20 7946 0958",
    "+1 (650) 555-0199",
    "020 7946 0958",
    "+65 6123 4567",
    "13800138000",
    "+81 3-1234-5678",
    "212.555.0198",
    "+61 2 9876 5432",
]

for i, phone in enumerate(phones, 1):
    text = f"Call me at {phone}."
    start = text.index(phone)

    samples.append({
        "id": f"pii-phone-{i:03d}",
        "text": text,
        "annotations": [{
            "entity_type": "PHONE_NUMBER",
            "start": start,
            "end": start + len(phone)
        }],
        "metadata": {
            "category": "phone",
            "source": "synthetic",
            "difficulty": "mixed"
        }
    })


# Financial
cards = [
    "4111111111111111",
    "5555555555554444",
    "4012888888881881",
    "378282246310005",
    "6011111111111117",
    "3530111333300000",
    "5105105105105100",
    "4222222222222",
    "2223003122003222",
    "4000056655665556",
]

for i, card in enumerate(cards, 1):
    text = f"Test payment card: {card}."
    start = text.index(card)

    samples.append({
        "id": f"pii-financial-{i:03d}",
        "text": text,
        "annotations": [{
            "entity_type": "PAYMENT_CARD",
            "start": start,
            "end": start + len(card)
        }],
        "metadata": {
            "category": "financial",
            "source": "synthetic",
            "difficulty": "easy"
        }
    })


# Negative samples
negative_texts = [
    "The Kubernetes cluster is running normally.",
    "The weather is sunny today.",
    "Please review the architecture document.",
    "The application returned HTTP 200.",
    "The deployment completed successfully.",
    "Python is a popular programming language.",
    "The database contains 120 records.",
    "The model achieved 95 percent accuracy.",
    "Please restart the development environment.",
    "The service is available in three regions.",
    "We need to improve the inference latency.",
    "The API endpoint returned a successful response.",
    "The software team completed the sprint.",
    "The server has 64 GB of memory.",
    "The container image was successfully built.",
]

for i, text in enumerate(negative_texts, 1):

    samples.append({
        "id": f"pii-negative-{i:03d}",
        "text": text,
        "annotations": [],
        "metadata": {
            "category": "negative",
            "source": "synthetic",
            "difficulty": "easy"
        }
    })


random.shuffle(samples)

OUTPUT.parent.mkdir(parents=True, exist_ok=True)

with OUTPUT.open("w", encoding="utf-8") as f:

    for sample in samples:
        f.write(json.dumps(
            sample,
            ensure_ascii=False
        ) + "\n")

print("Generated:", len(samples))
print("Output:", OUTPUT)
