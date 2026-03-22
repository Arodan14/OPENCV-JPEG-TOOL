# JPEG Tool

A modern Flask web app for resizing and compressing JPEG images with OpenCV.

This project started as coursework for a System Programming course, then evolved into a cleaner portfolio project with both a web interface and a CLI workflow.

## Features

- Upload `.jpg` and `.jpeg` images
- Run the same processing pipeline from a command-line interface
- Choose a target resolution preset
- Apply low, medium, or high JPEG quality
- Preserve aspect ratio while fitting inside the selected resolution
- Preview the processed output and open it in a new tab
- Return useful metadata for original size, requested size, output size, and quality level

## Tech stack

- Python
- Flask
- OpenCV
- HTML, CSS, JavaScript

## Project structure

```text
JPEG_TOOL/
|-- app/
|   |-- app.py
|   |-- image_service.py
|   |-- static/
|   |   |-- css/base.css
|   |   |-- js/upload.js
|   |   |-- processed/
|   |   `-- uploads/
|   `-- templates/
|       |-- base.html
|       `-- index.html
|-- jpeg_tool_cli.py
|-- requirements.txt
`-- README.md
```

## Setup

1. Create and activate a virtual environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Start the app:

```bash
python app/app.py
```

4. Open `http://127.0.0.1:5000`

## CLI usage

You can also use the project from the terminal:

```bash
python jpeg_tool_cli.py "path/to/image.jpg" --resolution 1280x720 --quality medium
```

Optional output directory:

```bash
python jpeg_tool_cli.py "path/to/image.jpg" --resolution 854x480 --quality low --output-dir output
```

The CLI saves the processed image and prints the original size, requested size, output size, and selected quality.

## Course context

This project was originally built for a System Programming course, and covers:

- file handling
- input validation
- image processing with OpenCV
- shared logic reused across web and CLI interfaces
- practical software structure and documentation

## Possible Improvement:
- Adding batch upload support as a next feature.

## Notes

- Processed images are stored in `app/static/processed`.
- The app and CLI share the same OpenCV processing service.
- The processing flow decodes uploads in memory with OpenCV, resizes them with OpenCV, and re-encodes the final JPEG with OpenCV before saving.
- The current output keeps the original aspect ratio and fits the image inside the selected preset.
