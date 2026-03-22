from pathlib import Path

from flask import Flask, jsonify, render_template, request

from image_service import (
    ImageProcessingError,
    RESOLUTION_PRESETS,
    ensure_directories,
    process_image,
)


BASE_DIR = Path(__file__).resolve().parent
PROCESSED_DIR = BASE_DIR / "static" / "processed"

ensure_directories(PROCESSED_DIR)

app = Flask(__name__)


@app.get("/")
def index():
    return render_template("index.html", resolution_presets=RESOLUTION_PRESETS)


@app.post("/process")
def process_uploaded_image():
    try:
        result = process_image(
            file=request.files.get("file"),
            processed_dir=PROCESSED_DIR,
            raw_resolution=request.form.get("resolution", ""),
            raw_quality=request.form.get("quality", ""),
        )
    except ImageProcessingError as error:
        return jsonify({"error": str(error)}), 400
    except Exception:
        return jsonify({"error": "Unexpected error while processing the image."}), 500

    return jsonify(
        {
            "filename": result.filename,
            "preview_url": f"/static/processed/{result.filename}",
            "download_url": f"/static/processed/{result.filename}",
            "original_filename": result.original_filename,
            "requested_size": {"width": result.requested_size[0], "height": result.requested_size[1]},
            "output_size": {"width": result.output_size[0], "height": result.output_size[1]},
            "original_size": {"width": result.original_size[0], "height": result.original_size[1]},
            "quality": {"label": result.quality_label, "value": result.quality_value},
        }
    )


if __name__ == "__main__":
    app.run(debug=True)
