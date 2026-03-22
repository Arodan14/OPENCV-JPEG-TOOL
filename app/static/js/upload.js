document.addEventListener("DOMContentLoaded", () => {
    const form = document.querySelector("#upload-form");
    const dropzone = document.querySelector("#dropzone");
    const fileInput = document.querySelector("#file-input");
    const previewImage = document.querySelector("#preview-image");
    const dropzoneContent = document.querySelector("#dropzone-content");
    const processButton = document.querySelector("#process-button");
    const statusText = document.querySelector("#status-text");
    const resultEmpty = document.querySelector("#result-empty");
    const resultContent = document.querySelector("#result-content");
    const resultImage = document.querySelector("#result-image");
    const downloadLink = document.querySelector("#download-link");
    const resultFilename = document.querySelector("#result-filename");
    const originalMeta = document.querySelector("#original-meta");
    const requestedMeta = document.querySelector("#requested-meta");
    const outputMeta = document.querySelector("#output-meta");
    const qualityMeta = document.querySelector("#quality-meta");

    let selectedFile = null;

    const setStatus = (message, state = "idle") => {
        statusText.textContent = message;
        statusText.dataset.state = state;
    };

    const formatSize = (size) => `${size.width} x ${size.height}`;

    const showPreview = (file) => {
        const reader = new FileReader();

        reader.addEventListener("load", (event) => {
            previewImage.src = event.target?.result || "";
            previewImage.classList.remove("hidden");
            dropzoneContent.classList.add("hidden");
        });

        reader.readAsDataURL(file);
    };

    const resetDropzone = () => {
        previewImage.src = "";
        previewImage.classList.add("hidden");
        dropzoneContent.classList.remove("hidden");
    };

    const handleFileSelection = (file) => {
        if (!file) {
            return;
        }

        const isJpeg = ["image/jpeg", "image/jpg"].includes(file.type) || /\.jpe?g$/i.test(file.name);
        if (!isJpeg) {
            selectedFile = null;
            fileInput.value = "";
            resetDropzone();
            setStatus("Please choose a valid JPEG image.", "error");
            return;
        }

        selectedFile = file;
        showPreview(file);
        setStatus(`${file.name} selected. Ready to process.`, "idle");
    };

    ["dragenter", "dragover"].forEach((eventName) => {
        dropzone.addEventListener(eventName, (event) => {
            event.preventDefault();
            dropzone.classList.add("is-dragover");
        });
    });

    ["dragleave", "dragend", "drop"].forEach((eventName) => {
        dropzone.addEventListener(eventName, (event) => {
            event.preventDefault();
            dropzone.classList.remove("is-dragover");
        });
    });

    dropzone.addEventListener("drop", (event) => {
        const file = event.dataTransfer?.files?.[0];
        handleFileSelection(file);
    });

    fileInput.addEventListener("change", (event) => {
        const file = event.target.files?.[0];
        handleFileSelection(file);
    });

    form.addEventListener("submit", async (event) => {
        event.preventDefault();

        if (!selectedFile) {
            setStatus("Select a JPEG before processing.", "error");
            return;
        }

        processButton.disabled = true;
        setStatus("Processing image...", "idle");

        const formData = new FormData();
        formData.append("file", selectedFile);
        formData.append("resolution", document.querySelector("#resolution").value);
        formData.append("quality", document.querySelector("#quality").value);

        try {
            const response = await fetch("/process", {
                method: "POST",
                body: formData,
            });
            const payload = await response.json();

            if (!response.ok) {
                throw new Error(payload.error || "Processing failed.");
            }

            resultImage.src = payload.preview_url;
            resultImage.alt = `Processed ${payload.original_filename}`;
            downloadLink.href = payload.download_url;
            resultFilename.textContent = payload.filename;
            originalMeta.textContent = formatSize(payload.original_size);
            requestedMeta.textContent = formatSize(payload.requested_size);
            outputMeta.textContent = formatSize(payload.output_size);
            qualityMeta.textContent = `${payload.quality.label} (${payload.quality.value})`;

            resultEmpty.classList.add("hidden");
            resultContent.classList.remove("hidden");
            setStatus("Processing complete. Your image is ready.", "success");
        } catch (error) {
            setStatus(error.message || "An unexpected error occurred.", "error");
        } finally {
            processButton.disabled = false;
        }
    });
});
