import argparse
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent
APP_DIR = PROJECT_ROOT / "app"
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

from image_service import (  # noqa: E402
    ImageProcessingError,
    QUALITY_MAP,
    RESOLUTION_PRESETS,
    ensure_directories,
    process_image_file,
)


DEFAULT_OUTPUT_DIR = APP_DIR / "static" / "processed"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Resize and compress a JPEG image using the OpenCV pipeline from JPEG Tool."
    )
    parser.add_argument("input", help="Path to the input .jpg or .jpeg file.")
    parser.add_argument(
        "--resolution",
        default="1920x1080",
        choices=sorted(RESOLUTION_PRESETS.keys(), reverse=True),
        help="Target resolution preset.",
    )
    parser.add_argument(
        "--quality",
        default="medium",
        choices=tuple(QUALITY_MAP.keys()),
        help="JPEG quality preset.",
    )
    parser.add_argument(
        "--output-dir",
        default=str(DEFAULT_OUTPUT_DIR),
        help="Directory where the processed JPEG will be saved.",
    )
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    output_dir = Path(args.output_dir).resolve()
    ensure_directories(output_dir)

    try:
        result = process_image_file(
            input_path=Path(args.input),
            processed_dir=output_dir,
            raw_resolution=args.resolution,
            raw_quality=args.quality,
        )
    except ImageProcessingError as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1

    print(f"Saved: {output_dir / result.filename}")
    print(f"Original size: {result.original_size[0]}x{result.original_size[1]}")
    print(f"Requested size: {result.requested_size[0]}x{result.requested_size[1]}")
    print(f"Output size: {result.output_size[0]}x{result.output_size[1]}")
    print(f"Quality: {result.quality_label} ({result.quality_value})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
