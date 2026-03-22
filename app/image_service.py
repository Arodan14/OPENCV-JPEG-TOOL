from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from uuid import uuid4

import cv2
import numpy as np
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename


ALLOWED_EXTENSIONS = {"jpg", "jpeg"}
QUALITY_MAP = {"low": 35, "medium": 65, "high": 90}
RESOLUTION_PRESETS = {
    "2560x1440": "1440p",
    "1920x1080": "1080p",
    "1280x720": "720p",
    "854x480": "480p",
    "640x360": "360p",
    "256x144": "144p",
}


class ImageProcessingError(ValueError):
    """Raised when the uploaded file or processing options are invalid."""


@dataclass(frozen=True)
class ProcessedImageResult:
    filename: str
    original_filename: str
    original_size: tuple[int, int]
    output_size: tuple[int, int]
    requested_size: tuple[int, int]
    quality_label: str
    quality_value: int


def ensure_directories(*directories: Path) -> None:
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)


def validate_file(file: FileStorage | None) -> FileStorage:
    if file is None:
        raise ImageProcessingError("No file was uploaded.")

    if not file.filename:
        raise ImageProcessingError("Please choose a JPEG image.")

    extension = Path(file.filename).suffix.lower().lstrip(".")
    if extension not in ALLOWED_EXTENSIONS:
        raise ImageProcessingError("Only .jpg and .jpeg files are supported.")

    return file


def parse_resolution(raw_resolution: str) -> tuple[int, int]:
    if raw_resolution not in RESOLUTION_PRESETS:
        raise ImageProcessingError("Unsupported resolution preset selected.")

    width, height = raw_resolution.split("x", maxsplit=1)
    return int(width), int(height)


def parse_quality(raw_quality: str) -> tuple[str, int]:
    normalized_quality = (raw_quality or "").strip().lower()
    if normalized_quality not in QUALITY_MAP:
        raise ImageProcessingError("Unsupported quality preset selected.")

    return normalized_quality, QUALITY_MAP[normalized_quality]


def build_output_name(original_name: str, requested_size: tuple[int, int], quality_label: str) -> str:
    safe_stem = secure_filename(Path(original_name).stem) or "image"
    width, height = requested_size
    unique_suffix = uuid4().hex[:8]
    return f"{safe_stem}_{width}x{height}_{quality_label}_{unique_suffix}.jpg"


def fit_within_resolution(
    current_size: tuple[int, int], requested_size: tuple[int, int]
) -> tuple[int, int]:
    original_width, original_height = current_size
    requested_width, requested_height = requested_size

    aspect_ratio = original_width / original_height
    requested_ratio = requested_width / requested_height

    if requested_ratio > aspect_ratio:
        output_height = requested_height
        output_width = max(1, int(round(output_height * aspect_ratio)))
    else:
        output_width = requested_width
        output_height = max(1, int(round(output_width / aspect_ratio)))

    return output_width, output_height


def decode_image_from_upload(file: FileStorage) -> np.ndarray:
    file.stream.seek(0)
    file_bytes = file.read()
    if not file_bytes:
        raise ImageProcessingError("The uploaded file is empty.")

    image_buffer = np.frombuffer(file_bytes, dtype=np.uint8)
    image = cv2.imdecode(image_buffer, cv2.IMREAD_COLOR)
    if image is None:
        raise ImageProcessingError("The uploaded image could not be decoded.")

    return image


def encode_jpeg_image(image: np.ndarray, quality_value: int) -> np.ndarray:
    success, encoded_image = cv2.imencode(".jpg", image, [cv2.IMWRITE_JPEG_QUALITY, quality_value])
    if not success:
        raise ImageProcessingError("The processed image could not be encoded.")

    return encoded_image


def process_image(
    file: FileStorage, processed_dir: Path, raw_resolution: str, raw_quality: str
) -> ProcessedImageResult:
    validated_file = validate_file(file)
    requested_size = parse_resolution(raw_resolution)
    quality_label, quality_value = parse_quality(raw_quality)

    original_filename = secure_filename(validated_file.filename or "") or "image.jpg"
    image = decode_image_from_upload(validated_file)

    original_height, original_width = image.shape[:2]
    output_size = fit_within_resolution((original_width, original_height), requested_size)
    resized_image = cv2.resize(image, output_size, interpolation=cv2.INTER_AREA)
    encoded_image = encode_jpeg_image(resized_image, quality_value)

    output_filename = build_output_name(original_filename, requested_size, quality_label)
    output_path = processed_dir / output_filename
    saved = output_path.write_bytes(encoded_image.tobytes())
    if not saved:
        raise ImageProcessingError("The processed image could not be saved.")

    return ProcessedImageResult(
        filename=output_filename,
        original_filename=original_filename,
        original_size=(original_width, original_height),
        output_size=output_size,
        requested_size=requested_size,
        quality_label=quality_label,
        quality_value=quality_value,
    )
