"""
Image preprocessing utilities used before running YOLOv8 inference, and for
saving annotated detection output.
"""

from pathlib import Path

import cv2
import numpy as np

from app.utils.logger import logger

# Standard input size most YOLOv8 export configs expect; the model itself
# will internally letterbox/resize again, this just keeps very large
# citizen-uploaded photos from blowing up memory/latency.

MAX_DIMENSION = 1280


def load_image(image_path: str) -> np.ndarray:
    """Load an image from disk as a BGR numpy array (OpenCV convention)."""
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError(f"Could not read image at path: {image_path}")
    return image


def resize_if_needed(image: np.ndarray, max_dimension: int = MAX_DIMENSION) -> np.ndarray:
    """Downscale an image (preserving aspect ratio) if it exceeds max_dimension."""
    height, width = image.shape[:2]
    longest_side = max(height, width)
    if longest_side <= max_dimension:
        return image

    scale = max_dimension / longest_side
    new_size = (int(width * scale), int(height * scale))
    return cv2.resize(image, new_size, interpolation=cv2.INTER_AREA)


def draw_detections(
    image: np.ndarray,
    boxes: list[tuple[float, float, float, float]],
    labels: list[str],
    confidences: list[float],
) -> np.ndarray:
    """Draw bounding boxes + labels onto a copy of the image for the annotated output."""
    annotated = image.copy()
    for (x1, y1, x2, y2), label, conf in zip(boxes, labels, confidences):
        pt1, pt2 = (int(x1), int(y1)), (int(x2), int(y2))
        cv2.rectangle(annotated, pt1, pt2, color=(0, 140, 255), thickness=2)
        caption = f"{label} {conf * 100:.1f}%"
        cv2.putText(
            annotated,
            caption,
            (pt1[0], max(pt1[1] - 8, 0)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (0, 140, 255),
            2,
            cv2.LINE_AA,
        )
    return annotated


def save_image(image: np.ndarray, output_path: str) -> str:
    """Save an image array to disk, creating parent directories as needed."""
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    success = cv2.imwrite(output_path, image)
    if not success:
        raise IOError(f"Failed to write image to {output_path}")
    logger.debug(f"Saved processed image to {output_path}")
    return output_path
