import json
from pathlib import Path

DATASET = Path("datasets/pii/golden_v1.jsonl")


def validate_dataset():

    seen_ids = set()
    total = 0
    errors = []

    with DATASET.open(encoding="utf-8") as f:

        for line_number, line in enumerate(f, 1):

            if not line.strip():
                continue

            try:
                item = json.loads(line)
            except json.JSONDecodeError as exc:
                errors.append(
                    f"Line {line_number}: Invalid JSON: {exc}"
                )
                continue

            total += 1

            sample_id = item.get("id")
            text = item.get("text")
            annotations = item.get("annotations")

            if not sample_id or sample_id in seen_ids:
                errors.append(
                    f"Line {line_number}: Missing or duplicate ID"
                )

            seen_ids.add(sample_id)

            if not isinstance(text, str):
                errors.append(
                    f"Line {line_number}: Invalid text"
                )
                continue

            if not isinstance(annotations, list):
                errors.append(
                    f"Line {line_number}: Invalid annotations"
                )
                continue

            for ann in annotations:

                start = ann.get("start")
                end = ann.get("end")
                entity_type = ann.get("entity_type")

                if not isinstance(start, int):
                    errors.append(
                        f"{sample_id}: Invalid start"
                    )
                    continue

                if not isinstance(end, int):
                    errors.append(
                        f"{sample_id}: Invalid end"
                    )
                    continue

                if not 0 <= start < end <= len(text):
                    errors.append(
                        f"{sample_id}: Invalid span"
                    )
                    continue

                if not entity_type:
                    errors.append(
                        f"{sample_id}: Missing entity_type"
                    )

    print("===== DATASET VALIDATION =====")
    print("Total samples:", total)
    print("Unique IDs:", len(seen_ids))
    print("Errors:", len(errors))

    for error in errors:
        print("[ERROR]", error)

    if errors:
        raise SystemExit(1)

    print("VALIDATION PASSED")


if __name__ == "__main__":
    validate_dataset()
