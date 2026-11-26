
import csv
import json
import math
import time

from pathlib import Path
from statistics import mean

from gliner import GLiNER
from gliner2 import GLiNER2

from presidio_analyzer import AnalyzerEngine
from presidio_analyzer.nlp_engine import NlpEngineProvider

from app.guardrails.entity_schema import normalize_entity_type


DATASET = Path("datasets/pii/golden_v1.jsonl")
REPORT_DIR = Path("benchmarks/pii/reports")

GLINER_MODEL = "urchade/gliner_multi_pii-v1"
GLINER2_MODEL = "fastino/GLiNER2-Guardrails-PII-Multi"

GLINER_LABELS = [
    "person",
    "email",
    "phone number",
    "credit card number"
]

GLINER2_LABELS = [
    "person",
    "full_name",
    "first_name",
    "last_name",
    "email",
    "phone_number",
    "credit_card"
]

PRESIDIO_ENTITIES = [
    "PERSON",
    "EMAIL_ADDRESS",
    "PHONE_NUMBER",
    "CREDIT_CARD"
]

PII_TYPES = {
    "PERSON",
    "PERSON_NAME_PART",
    "EMAIL_ADDRESS",
    "PHONE_NUMBER",
    "PAYMENT_CARD"
}


def load_dataset():

    samples = []

    with DATASET.open(encoding="utf-8") as f:
        for line in f:
            if line.strip():
                samples.append(json.loads(line))

    return samples


def percentile(values, p):

    if not values:
        return 0.0

    values = sorted(values)

    index = math.ceil(p * len(values)) - 1

    return values[max(0, index)]


def normalize_prediction(label, start, end, score):

    entity_type = normalize_entity_type(label)

    if entity_type not in PII_TYPES:
        return None

    return (
        entity_type,
        int(start),
        int(end)
    )


# ----------------------------------
# Presidio
# ----------------------------------

def load_presidio():

    configuration = {
        "nlp_engine_name": "spacy",
        "models": [
            {
                "lang_code": "en",
                "model_name": "en_core_web_sm"
            }
        ]
    }

    provider = NlpEngineProvider(
        nlp_configuration=configuration
    )

    nlp_engine = provider.create_engine()

    return AnalyzerEngine(
        nlp_engine=nlp_engine,
        supported_languages=["en"]
    )


def predict_presidio(model, text):

    results = model.analyze(
        text=text,
        language="en",
        entities=PRESIDIO_ENTITIES,
        score_threshold=0.35
    )

    predictions = set()

    for item in results:

        result = normalize_prediction(
            item.entity_type,
            item.start,
            item.end,
            item.score
        )

        if result:
            predictions.add(result)

    return predictions


# ----------------------------------
# GLiNER
# ----------------------------------

def load_gliner():

    return GLiNER.from_pretrained(
        GLINER_MODEL
    )


def predict_gliner(model, text):

    results = model.predict_entities(
        text,
        GLINER_LABELS,
        threshold=0.5
    )

    predictions = set()

    for item in results:

        result = normalize_prediction(
            item["label"],
            item["start"],
            item["end"],
            item["score"]
        )

        if result:
            predictions.add(result)

    return predictions


# ----------------------------------
# GLiNER2
# ----------------------------------

def load_gliner2():

    model = GLiNER2.from_pretrained(
        GLINER2_MODEL
    )

    model.to("cpu")

    return model


def predict_gliner2(model, text):

    result = model.extract_entities(
        text,
        GLINER2_LABELS,
        threshold=0.5,
        include_confidence=True,
        include_spans=True
    )

    predictions = set()

    entities = result.get("entities", {})

    for label, items in entities.items():

        for item in items:

            prediction = normalize_prediction(
                label,
                item["start"],
                item["end"],
                item.get("confidence", 0.0)
            )

            if prediction:
                predictions.add(prediction)

    return predictions

def validate_predictions(predictions, text):

    validated = set()

    for entity_type, start, end in predictions:

        value = text[start:end]

        if entity_type == "PAYMENT_CARD":

            from app.guardrails.validators.payment_card import (
                validate_payment_card
            )

            if not validate_payment_card(value):
                continue

        validated.add(
            (entity_type, start, end)
        )

    return validated

from benchmarks.pii.span_matcher import (
    aggregate_person_name_parts
)

from app.guardrails.validators.payment_card import (
    validate_payment_card
)


def postprocess_predictions(
    predictions,
    text,
    model_name
):
    """
    Apply model-specific normalization and
    common entity validation.

    Input/output format:
        (entity_type, start, end)
    """

    processed = set(predictions)

    # GLiNER2 returns granular name components.
    # Aggregate them for PERSON-level evaluation.
    if model_name == "GLiNER2":

        processed = aggregate_person_name_parts(
            processed,
            text
        )

    # Apply the same payment-card validation
    # to every detector.
    validated = set()

    for entity_type, start, end in processed:

        value = text[start:end]

        if entity_type == "PAYMENT_CARD":

            if not validate_payment_card(value):
                continue

        validated.add(
            (entity_type, start, end)
        )

    return validated

def calculate_metrics(samples, predictions_by_sample):

    tp = 0
    fp = 0
    fn = 0

    negative_samples = 0
    negative_false_positives = 0

    fp_details = []
    fp_by_type = {}

    for sample, predictions in zip(
        samples,
        predictions_by_sample
    ):

        text = sample["text"]

        ground_truth = {
            (
                ann["entity_type"],
                ann["start"],
                ann["end"]
            )
            for ann in sample["annotations"]
        }

        matched = predictions & ground_truth
        sample_fp = predictions - ground_truth
        sample_fn = ground_truth - predictions

        tp += len(matched)
        fp += len(sample_fp)
        fn += len(sample_fn)

        for entity_type, start, end in sample_fp:

            fp_by_type[entity_type] = (
                fp_by_type.get(entity_type, 0) + 1
            )

            fp_details.append({
                "sample_id": sample["id"],
                "text": text,
                "entity_type": entity_type,
                "start": start,
                "end": end,
                "predicted_text": text[start:end]
            })

        if sample["metadata"]["category"] == "negative":

            negative_samples += 1

            if predictions:
                negative_false_positives += 1

    precision = (
        tp / (tp + fp)
        if tp + fp else 0.0
    )

    recall = (
        tp / (tp + fn)
        if tp + fn else 0.0
    )

    f1 = (
        2 * precision * recall / (precision + recall)
        if precision + recall else 0.0
    )

    negative_fpr = (
        negative_false_positives / negative_samples
        if negative_samples else 0.0
    )

    return {
        "tp": tp,
        "fp": fp,
        "fn": fn,
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1": round(f1, 4),
        "negative_samples": negative_samples,
        "negative_false_positives": negative_false_positives,
        "negative_fpr": round(negative_fpr, 4),
        "fp_by_type": fp_by_type,
        "fp_details": fp_details
    }

# ----------------------------------
# Evaluation
# ----------------------------------

def evaluate_model(name, loader, predictor, samples):

    print(f"\n===== {name} =====")

    load_start = time.perf_counter()
    model = loader()
    load_time = time.perf_counter() - load_start

    print(f"Model load: {load_time:.2f}s")

    # Warm-up: excluded from all latency metrics.
    predictor(model, samples[0]["text"])

    raw_predictions = []
    processed_predictions = []

    inference_latencies = []
    postprocessing_latencies = []

    for sample in samples:

        text = sample["text"]

        # 1. Model inference
        inference_start = time.perf_counter()

        raw = predictor(model, text)

        inference_ms = (
            time.perf_counter() - inference_start
        ) * 1000

        inference_latencies.append(inference_ms)

        # 2. Preserve canonical predictions before
        # additional post-processing.
        raw_predictions.append(set(raw))

        # 3. Post-processing
        postprocess_start = time.perf_counter()

        processed = postprocess_predictions(
            raw,
            text,
            name
        )

        postprocess_ms = (
            time.perf_counter() - postprocess_start
        ) * 1000

        postprocessing_latencies.append(
            postprocess_ms
        )

        processed_predictions.append(processed)

    # 4. Raw metrics
    raw_metrics = calculate_metrics(
        samples,
        raw_predictions
    )

    # 5. Post-processed metrics
    processed_metrics = calculate_metrics(
        samples,
        processed_predictions
    )

    def latency_summary(values):

        return {
            "mean_ms": round(mean(values), 2),
            "p50_ms": round(percentile(values, 0.50), 2),
            "p95_ms": round(percentile(values, 0.95), 2),
            "p99_ms": round(percentile(values, 0.99), 2)
        }

    result = {
        "model": name,
        "samples": len(samples),
        "load_time_seconds": round(load_time, 3),

        "raw": {
            key: value
            for key, value in raw_metrics.items()
            if key != "fp_details"
        },

        "post_processed": {
            key: value
            for key, value in processed_metrics.items()
            if key != "fp_details"
        },

        "latency": {
            "inference": latency_summary(
                inference_latencies
            ),
            "postprocessing": latency_summary(
                postprocessing_latencies
            )
        }
    }

    # 6. Save separate diagnostics
    for stage, metrics in [
        ("raw", raw_metrics),
        ("post_processed", processed_metrics)
    ]:

        diagnostics_path = (
            REPORT_DIR /
            f"{name.lower()}_{stage}_fp_details.json"
        )

        with diagnostics_path.open(
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                metrics["fp_details"],
                f,
                indent=2,
                ensure_ascii=False
            )

    print("\n===== RAW METRICS =====")

    print(json.dumps(
        result["raw"],
        indent=2,
        ensure_ascii=False
    ))

    print("\n===== POST-PROCESSED METRICS =====")

    print(json.dumps(
        result["post_processed"],
        indent=2,
        ensure_ascii=False
    ))

    print("\n===== LATENCY =====")

    print(json.dumps(
        result["latency"],
        indent=2,
        ensure_ascii=False
    ))

    return result



# ----------------------------------
# Main
# ----------------------------------

def main():

    samples = load_dataset()

    print("===== PII BENCHMARK =====")
    print("Dataset:", DATASET)
    print("Total samples:", len(samples))

    REPORT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    experiments = [
        (
            "Presidio",
            load_presidio,
            predict_presidio
        ),
        (
            "GLiNER",
            load_gliner,
            predict_gliner
        ),
        (
            "GLiNER2",
            load_gliner2,
            predict_gliner2
        )
    ]

    results = []

    for name, loader, predictor in experiments:

        result = evaluate_model(
            name,
            loader,
            predictor,
            samples
        )

        results.append(result)

    # JSON report
    json_path = REPORT_DIR / "pilot_results.json"

    with json_path.open("w", encoding="utf-8") as f:
        json.dump(
            results,
            f,
            indent=2,
            ensure_ascii=False
        )

    # CSV report - flattened comparison
    csv_path = REPORT_DIR / "pilot_results.csv"

    csv_rows = []

    for result in results:

        row = {
            "model": result["model"],
            "samples": result["samples"],
            "load_time_seconds": result["load_time_seconds"]
        }

        for stage in ["raw", "post_processed"]:

            for key, value in result[stage].items():

                if key != "fp_by_type":
                    row[f"{stage}_{key}"] = value

        for stage in ["inference", "postprocessing"]:

            for key, value in result["latency"][stage].items():

                row[f"{stage}_{key}"] = value

        csv_rows.append(row)

    with csv_path.open(
        "w",
        newline="",
        encoding="utf-8"
    ) as f:

        writer = csv.DictWriter(
            f,
            fieldnames=csv_rows[0].keys()
        )

        writer.writeheader()
        writer.writerows(csv_rows)


    print("\n===== BENCHMARK COMPLETED =====")
    print("JSON:", json_path)
    print("CSV:", csv_path)


if __name__ == "__main__":
    main()
