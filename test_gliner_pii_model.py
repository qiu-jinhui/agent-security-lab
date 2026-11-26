
import time
import torch

from gliner import GLiNER

MODEL_NAME = "urchade/gliner_multi_pii-v1"

print("===== ENVIRONMENT =====")
print("PyTorch:", torch.__version__)
print("Device: CPU")

print("\n===== LOADING MODEL =====")

start = time.perf_counter()

model = GLiNER.from_pretrained(MODEL_NAME)

load_time = time.perf_counter() - start

print(f"Model loaded in {load_time:.2f}s")


samples = [
    {
        "id": "sample-001",
        "text": (
            "Contact John Smith at "
            "john.smith@example.com."
        )
    },
    {
        "id": "sample-002",
        "text": "Please call me at 415-555-0132."
    },
    {
        "id": "sample-003",
        "text": (
            "My credit card number is "
            "4111111111111111."
        )
    },
    {
        "id": "sample-004",
        "text": (
            "Jane Doe works at Acme Corporation "
            "in San Francisco."
        )
    },
    {
        "id": "sample-005",
        "text": (
            "The Kubernetes cluster is running normally."
        )
    }
]

labels = [
    "person",
    "organization",
    "phone number",
    "email",
    "credit card number",
    "address",
    "location",
    "social security number"
]

print("\n===== INFERENCE =====")

for sample in samples:

    start = time.perf_counter()

    entities = model.predict_entities(
        sample["text"],
        labels,
        threshold=0.5
    )

    elapsed = time.perf_counter() - start

    print(f"\n--- {sample['id']} ---")
    print("Text:", sample["text"])

    for entity in entities:
        print({
            "text": entity["text"],
            "label": entity["label"],
            "score": round(entity["score"], 4),
            "start": entity["start"],
            "end": entity["end"]
        })

    print(f"Latency: {elapsed * 1000:.2f} ms")
