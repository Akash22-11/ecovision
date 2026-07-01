"""
YOLOv8-based pollution detector.
"""

import random
from pathlib import Path
from typing import Any

from app.config import settings
from app.utils.constants import YOLO_POLLUTION_CLASSES
from app.utils.helpers import severity_from_confidence
from app.utils.logger import logger

_model_cache: dict[str, Any] = {}


def _load_model():
    """Lazily load and cache the YOLOv8 model. Returns None if unavailable."""
    
    if "model" in _model_cache:
        return _model_cache["model"]

    model_path = Path(settings.YOLO_MODEL_PATH)
    if not model_path.exists():
        logger.warning(
            f"YOLOv8 weights not found at '{model_path}'. "
            "Running pollution detector in MOCK MODE - see app/ai/yolo_detector.py."
        )
        _model_cache["model"] = None
        return None

    try:
        from ultralytics import YOLO        # imported lazily: heavy optional dependency

        model = YOLO(str(model_path))
        _model_cache["model"] = model
        logger.info(f"Loaded YOLOv8 pollution model from {model_path}")
        return model
    except Exception as exc:               # noqa: BLE001 - we want any load failure to degrade gracefully
        logger.error(f"Failed to load YOLOv8 model ({exc}). Falling back to mock mode.")
        _model_cache["model"] = None
        return None


def detect_pollution(image_path: str) -> dict[str, Any]:
  
    """
    Run pollution detection on an image.

    Returns:
        {
            "type": str,                # one of YOLO_POLLUTION_CLASSES
            "confidence": float,        # 0-1
            "severity": SeverityLevel,
            "boxes": list[tuple],       # (x1, y1, x2, y2) in pixel coords
            "labels": list[str],
            "confidences": list[float],
            "mock": bool,
        }
    """
    
    model = _load_model()

    if model is None:
        return _mock_detection()

    results = model.predict(
        source=image_path,
        conf=settings.YOLO_CONFIDENCE_THRESHOLD,
        verbose=False,
    )

    if not results or len(results[0].boxes) == 0:
        logger.info(f"No pollution detected above threshold for {image_path}")
        return {
            "type": "other",
            "confidence": 0.0,
            "severity": severity_from_confidence(0.0),
            "boxes": [],
            "labels": [],
            "confidences": [],
            "mock": False,
        }

    result = results[0]
    names = result.names

    boxes: list[tuple[float, float, float, float]] = []
    labels: list[str] = []
    confidences: list[float] = []

    for box in result.boxes:
        xyxy = box.xyxy[0].tolist()
        boxes.append((xyxy[0], xyxy[1], xyxy[2], xyxy[3]))
        class_id = int(box.cls[0].item())
        labels.append(names.get(class_id, "other"))
        confidences.append(float(box.conf[0].item()))

    # Use the highest-confidence detection as the report's primary classification.
    best_idx = max(range(len(confidences)), key=lambda i: confidences[i])

    return {
        "type": labels[best_idx],
        "confidence": confidences[best_idx],
        "severity": severity_from_confidence(confidences[best_idx]),
        "boxes": boxes,
        "labels": labels,
        "confidences": confidences,
        "mock": False,
    }


def _mock_detection() -> dict[str, Any]:
    """Deterministic-ish, plausible fake detection used when no model is present."""
    pollution_type = random.choice(YOLO_POLLUTION_CLASSES)
    confidence = round(random.uniform(0.55, 0.93), 2)
    return {
        "type": pollution_type,
        "confidence": confidence,
        "severity": severity_from_confidence(confidence),
        "boxes": [(40.0, 40.0, 260.0, 220.0)],
        "labels": [pollution_type],
        "confidences": [confidence],
        "mock": True,
    }


# --- TEST BLOCK ---
if __name__ == "__main__":
    print("Testing YOLOv8 Detector...")
    
    # Pass a dummy path; if the model exists, YOLO will throw an error about the missing file,
    # but if it's in mock mode, it will gracefully return our fake data!
    result = detect_pollution("dummy_image.jpg")
    
    print("\n--- Detection Results ---")
    print(f"Mode:          {'MOCK' if result['mock'] else 'REAL'}")
    print(f"Primary Type:  {result['type']}")
    print(f"Confidence:    {result['confidence']}")
    print(f"Severity:      {result['severity']}")
    print(f"Boxes found:   {len(result['boxes'])}")
    if result['boxes']:
        print(f"First Box:     {result['boxes'][0]}")
