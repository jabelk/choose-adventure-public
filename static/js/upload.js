/**
 * Reference Photo Upload - Client-side validation, previews, and drag-drop.
 *
 * Expects the form to contain:
 *   #reference-photos-input  — hidden file input (multiple, accept=image/*)
 *   #upload-drop-zone        — drop zone div
 *   #upload-previews         — thumbnail container
 *   #upload-status           — status/error message area
 *   #start-form              — the parent form
 */
(function () {
    'use strict';

    const MAX_FILES = 3;
    const MAX_SIZE = 10 * 1024 * 1024; // 10 MB
    const ALLOWED = new Set(['image/jpeg', 'image/png']);

    // Current file list (managed separately from the file input)
    let selectedFiles = [];

    const form = document.getElementById('start-form');
    const fileInput = document.getElementById('reference-photos-input');
    const dropZone = document.getElementById('upload-drop-zone');
    const previews = document.getElementById('upload-previews');
    const status = document.getElementById('upload-status');

    if (!fileInput || !dropZone || !previews || !form) return;

    // --- File validation ---
    function validateFile(file) {
        if (!ALLOWED.has(file.type)) {
            return `"${file.name}" is not a supported format. Only JPEG and PNG allowed.`;
        }
        if (file.size > MAX_SIZE) {
            const sizeMB = (file.size / (1024 * 1024)).toFixed(1);
            return `"${file.name}" is too large (${sizeMB} MB). Maximum is 10 MB.`;
        }
        return null;
    }

    // --- Add files to selection ---
    function addFiles(newFiles) {
        status.textContent = '';
        status.className = 'upload-status';

        for (const file of newFiles) {
            if (selectedFiles.length >= MAX_FILES) {
                status.textContent = `Maximum ${MAX_FILES} photos allowed.`;
                status.className = 'upload-status upload-status-error';
                break;
            }
            const err = validateFile(file);
            if (err) {
                status.textContent = err;
                status.className = 'upload-status upload-status-error';
                continue;
            }
            selectedFiles.push(file);
        }

        syncInputAndPreviews();
    }

    // --- Remove a file by index ---
    function removeFile(index) {
        selectedFiles.splice(index, 1);
        status.textContent = '';
        status.className = 'upload-status';
        syncInputAndPreviews();
    }

    // --- Sync file input and render thumbnails ---
    function syncInputAndPreviews() {
        // Update the actual file input using DataTransfer
        const dt = new DataTransfer();
        selectedFiles.forEach(function (f) { dt.items.add(f); });
        fileInput.files = dt.files;

        // Form always uses multipart/form-data (set in template) since the
        // server handler expects File() parameters. No need to toggle encoding.

        // Update drop zone text
        const label = dropZone.querySelector('.upload-drop-label');
        if (label) {
            label.textContent = selectedFiles.length > 0
                ? `${selectedFiles.length}/${MAX_FILES} photo${selectedFiles.length !== 1 ? 's' : ''} selected`
                : 'Drag & drop photos here or click to browse';
        }

        // Render thumbnails
        previews.innerHTML = '';
        selectedFiles.forEach(function (file, idx) {
            const thumb = document.createElement('div');
            thumb.className = 'upload-thumb';

            const img = document.createElement('img');
            const reader = new FileReader();
            reader.onload = function (e) { img.src = e.target.result; };
            reader.readAsDataURL(file);
            thumb.appendChild(img);

            const name = document.createElement('span');
            name.className = 'upload-thumb-name';
            name.textContent = file.name.length > 15
                ? file.name.substring(0, 12) + '...'
                : file.name;
            thumb.appendChild(name);

            const removeBtn = document.createElement('button');
            removeBtn.type = 'button';
            removeBtn.className = 'upload-thumb-remove';
            removeBtn.textContent = '\u00D7';
            removeBtn.title = 'Remove';
            removeBtn.onclick = function (e) {
                e.stopPropagation();
                removeFile(idx);
            };
            thumb.appendChild(removeBtn);

            previews.appendChild(thumb);
        });
    }

    // --- Click on drop zone opens file picker ---
    dropZone.addEventListener('click', function () {
        fileInput.click();
    });

    // --- File input change ---
    fileInput.addEventListener('change', function () {
        if (fileInput.files.length > 0) {
            addFiles(Array.from(fileInput.files));
        }
    });

    // --- Drag and drop ---
    dropZone.addEventListener('dragover', function (e) {
        e.preventDefault();
        dropZone.classList.add('upload-drop-active');
    });

    dropZone.addEventListener('dragleave', function (e) {
        e.preventDefault();
        dropZone.classList.remove('upload-drop-active');
    });

    dropZone.addEventListener('drop', function (e) {
        e.preventDefault();
        dropZone.classList.remove('upload-drop-active');
        if (e.dataTransfer.files.length > 0) {
            addFiles(Array.from(e.dataTransfer.files));
        }
    });

    // Prevent drop zone click from propagating to file input twice
    fileInput.addEventListener('click', function (e) {
        e.stopPropagation();
    });
})();
