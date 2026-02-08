/**
 * Story Template Selection
 */
function selectTemplate(card) {
    var allCards = document.querySelectorAll('.template-card');
    var prompt = document.getElementById('prompt');
    if (!prompt) return;

    // If clicking already-selected card, deselect
    if (card.classList.contains('selected')) {
        card.classList.remove('selected');
        prompt.value = '';
        // Reset length to medium
        var mediumRadio = document.querySelector('input[name="length"][value="medium"]');
        if (mediumRadio) mediumRadio.checked = true;
        // Reset conflict_type to Any
        var anyConflict = document.querySelector('input[name="conflict_type"][value=""]');
        if (anyConflict) anyConflict.checked = true;
        // Clear character fields
        var charName = document.getElementById('character_name');
        var charDesc = document.getElementById('character_description');
        if (charName) charName.value = '';
        if (charDesc) charDesc.value = '';
        // Clear picker checkboxes
        document.querySelectorAll('.character-picker-item input[type="checkbox"]').forEach(function(cb) {
            cb.checked = false;
            cb.dispatchEvent(new Event('change'));
        });
        if (typeof updatePickerCount === 'function') updatePickerCount();
        var fallbackField = document.getElementById('template_fallback_characters');
        if (fallbackField) fallbackField.value = '';
        return;
    }

    // Deselect all, select this one
    allCards.forEach(function(c) { c.classList.remove('selected'); });
    card.classList.add('selected');

    // Pre-fill form
    prompt.value = card.dataset.prompt || '';

    var length = card.dataset.length || 'medium';
    var lengthRadio = document.querySelector('input[name="length"][value="' + length + '"]');
    if (lengthRadio) lengthRadio.checked = true;


    // Pre-select conflict_type radio
    var conflictType = card.dataset.conflictType || '';
    var conflictRadio = document.querySelector('input[name="conflict_type"][value="' + conflictType + '"]');
    if (conflictRadio) conflictRadio.checked = true;

    // Pre-fill character fields from template
    var characterNames = [];
    var characterData = [];
    try { characterNames = JSON.parse(card.dataset.characterNames || '[]'); } catch(e) {}
    try { characterData = JSON.parse(card.dataset.characterData || '[]'); } catch(e) {}

    var charName = document.getElementById('character_name');
    var charDesc = document.getElementById('character_description');

    // Try to match template characters against roster picker
    var pickerCheckboxes = document.querySelectorAll('.character-picker-item input[type="checkbox"]');
    var matchedInRoster = [];
    var fallbackChars = [];

    if (pickerCheckboxes.length > 0 && characterNames.length > 0) {
        // Uncheck all picker checkboxes first
        pickerCheckboxes.forEach(function(cb) { cb.checked = false; });

        characterNames.forEach(function(name, idx) {
            var matched = false;
            pickerCheckboxes.forEach(function(cb) {
                if (cb.dataset.characterName && cb.dataset.characterName.toLowerCase() === name.toLowerCase()) {
                    cb.checked = true;
                    cb.dispatchEvent(new Event('change'));
                    matched = true;
                    matchedInRoster.push(name);
                }
            });
            if (!matched && characterData[idx]) {
                fallbackChars.push(characterData[idx]);
            }
        });

        // Update picker count display
        if (typeof updatePickerCount === 'function') updatePickerCount();
    } else if (characterNames.length > 0) {
        // No picker available — use fallback data in manual fields
        characterData.forEach(function(cd) { fallbackChars.push(cd); });
    }

    // Fill manual fields with first fallback character (if any didn't match roster)
    if (fallbackChars.length > 0) {
        if (charName) charName.value = fallbackChars[0].name || '';
        if (charDesc) charDesc.value = fallbackChars[0].description || '';
    } else {
        if (charName) charName.value = '';
        if (charDesc) charDesc.value = '';
    }

    // Store additional fallback characters as hidden field for story start
    var fallbackField = document.getElementById('template_fallback_characters');
    if (fallbackField) {
        fallbackField.value = fallbackChars.length > 0 ? JSON.stringify(fallbackChars) : '';
    }

    // Scroll to the form
    prompt.scrollIntoView({ behavior: 'smooth', block: 'center' });
}

/**
 * PWA Install Prompt
 */
let deferredPrompt = null;

window.addEventListener('beforeinstallprompt', (e) => {
    e.preventDefault();
    deferredPrompt = e;

    // Don't show if user previously dismissed
    if (localStorage.getItem('pwa-install-dismissed')) return;

    const banner = document.getElementById('install-banner');
    if (banner) banner.style.display = 'flex';
});

function installApp() {
    if (!deferredPrompt) return;
    deferredPrompt.prompt();
    deferredPrompt.userChoice.then((choice) => {
        deferredPrompt = null;
        const banner = document.getElementById('install-banner');
        if (banner) banner.style.display = 'none';
    });
}

function dismissInstallBanner() {
    const banner = document.getElementById('install-banner');
    if (banner) banner.style.display = 'none';
    localStorage.setItem('pwa-install-dismissed', '1');
}

window.addEventListener('appinstalled', () => {
    const banner = document.getElementById('install-banner');
    if (banner) banner.style.display = 'none';
    deferredPrompt = null;
});

/**
 * Rotating progress messages shown during image generation.
 */
const progressMessages = [
    'Creating your illustration...',
    'Painting the scene...',
    'Adding the finishing touches...',
    'Bringing the story to life...',
    'Crafting something special...',
];

let progressInterval = null;
let isGenerating = false;

/**
 * Start cycling through progress messages in the placeholder.
 */
function startProgressMessages(container) {
    const textEl = container.querySelector('.image-progress-text');
    if (!textEl) return;

    let index = 0;
    textEl.textContent = progressMessages[0];

    progressInterval = setInterval(() => {
        index = (index + 1) % progressMessages.length;
        textEl.style.opacity = '0';
        setTimeout(() => {
            textEl.textContent = progressMessages[index];
            textEl.style.opacity = '1';
        }, 300);
    }, 3000);
}

/**
 * Stop cycling progress messages.
 */
function stopProgressMessages() {
    if (progressInterval) {
        clearInterval(progressInterval);
        progressInterval = null;
    }
}

/**
 * Show the generating placeholder with pulsing animation.
 */
function showGeneratingPlaceholder(container, sceneId) {
    container.innerHTML = `
        <div class="image-generating-placeholder">
            <span class="image-progress-text">Creating your illustration...</span>
        </div>
    `;
    container.dataset.sceneId = sceneId;
    startProgressMessages(container);
}

/**
 * Show failed state with retry button.
 */
function showFailedState(container, sceneId) {
    stopProgressMessages();
    isGenerating = false;
    container.innerHTML = `
        <div class="image-failed-state">
            <p>Image generation failed</p>
            <button class="btn-retry" onclick="retryImage('${sceneId}')">Retry</button>
        </div>
    `;
}

/**
 * Retry a failed image or regenerate an existing one.
 */
async function retryImage(sceneId) {
    const container = document.getElementById('scene-image-container');
    if (!container || isGenerating) return;

    const urlPrefix = document.body.dataset.urlPrefix || '';

    try {
        const response = await fetch(`${urlPrefix}/story/image/${sceneId}/retry`, {
            method: 'POST',
        });
        const data = await response.json();

        if (data.status === 'generating') {
            showGeneratingPlaceholder(container, sceneId);
            pollImageStatus(sceneId);
        }
    } catch (err) {
        showFailedState(container, sceneId);
    }
}

/**
 * Poll for image generation status and swap placeholder when ready.
 * Also updates extra images if present in the response.
 */
function pollImageStatus(sceneId) {
    const container = document.getElementById('scene-image-container');
    if (!container) return;

    isGenerating = true;
    const urlPrefix = document.body.dataset.urlPrefix || '';
    const maxAttempts = 30; // 60 seconds at 2s interval
    let attempts = 0;

    const poll = setInterval(async () => {
        attempts++;

        try {
            const response = await fetch(`${urlPrefix}/story/image/${sceneId}`);
            if (!response.ok) {
                clearInterval(poll);
                showFailedState(container, sceneId);
                return;
            }

            const data = await response.json();

            // Update extra images if present
            if (data.extra_images && data.extra_images.length > 0) {
                updateExtraImages(sceneId, data.extra_images);
            }

            if (data.status === 'complete' && data.url) {
                clearInterval(poll);
                showImage(container, data.url, sceneId);
            } else if (data.status === 'failed') {
                clearInterval(poll);
                showFailedState(container, sceneId);
            } else if (attempts >= maxAttempts) {
                clearInterval(poll);
                showFailedState(container, sceneId);
            }
        } catch (err) {
            // Network error — keep trying unless we've hit the limit
            if (attempts >= maxAttempts) {
                clearInterval(poll);
                showFailedState(container, sceneId);
            }
        }
    }, 2000);
}

/**
 * Poll specifically for extra images when main image may already be done
 * but extras are still generating.
 */
function pollExtraImages(sceneId, count) {
    const urlPrefix = document.body.dataset.urlPrefix || '';
    const maxAttempts = 30;
    let attempts = 0;

    const poll = setInterval(async () => {
        attempts++;
        try {
            const response = await fetch(`${urlPrefix}/story/image/${sceneId}`);
            if (!response.ok) { clearInterval(poll); return; }
            const data = await response.json();

            if (data.extra_images && data.extra_images.length > 0) {
                updateExtraImages(sceneId, data.extra_images);
                // Stop polling when all extra images are resolved
                const allDone = data.extra_images.every(
                    ei => ei.status === 'complete' || ei.status === 'failed'
                );
                if (allDone) clearInterval(poll);
            }

            if (attempts >= maxAttempts) clearInterval(poll);
        } catch (err) {
            if (attempts >= maxAttempts) clearInterval(poll);
        }
    }, 2000);
}

/**
 * Update individual extra image containers based on polling data.
 */
function updateExtraImages(sceneId, extraImages) {
    extraImages.forEach(function(ei) {
        const container = document.getElementById('extra-image-' + ei.index);
        if (!container) return;

        // Skip if already showing completed image
        if (container.dataset.resolved === 'true') return;

        if (ei.status === 'complete' && ei.url) {
            container.dataset.resolved = 'true';
            var label = container.querySelector('.extra-image-label');
            var labelHtml = label ? label.outerHTML : '';
            var img = document.createElement('img');
            img.src = ei.url;
            img.alt = ei.type === 'close-up' ? 'Character close-up' : 'Environment wide shot';
            img.style.opacity = '0';
            img.style.transition = 'opacity 0.5s ease-in';
            img.onload = function() {
                container.innerHTML = labelHtml;
                container.appendChild(img);
                requestAnimationFrame(function() { img.style.opacity = '1'; });
            };
        } else if (ei.status === 'failed') {
            container.dataset.resolved = 'true';
            var label = container.querySelector('.extra-image-label');
            var labelHtml = label ? label.outerHTML : '';
            container.innerHTML = labelHtml +
                '<div class="image-failed-state">' +
                '<p>Image generation failed</p>' +
                '<button class="btn-retry" onclick="retryExtraImage(\'' + sceneId + '\', ' + ei.index + ')">Retry</button>' +
                '</div>';
        }
    });
}

/**
 * Retry a failed extra image.
 */
async function retryExtraImage(sceneId, index) {
    const urlPrefix = document.body.dataset.urlPrefix || '';
    const container = document.getElementById('extra-image-' + index);
    if (!container) return;

    try {
        const response = await fetch(`${urlPrefix}/story/image/${sceneId}/retry-extra/${index}`, {
            method: 'POST',
        });
        const data = await response.json();

        if (data.status === 'generating') {
            container.dataset.resolved = '';
            var label = container.querySelector('.extra-image-label');
            var labelHtml = label ? label.outerHTML : '';
            container.innerHTML = labelHtml +
                '<div class="image-generating-placeholder">' +
                '<span class="image-progress-text">Creating illustration...</span>' +
                '</div>';
            pollExtraImages(sceneId, 1);
        }
    } catch (err) {
        // Leave as-is on error
    }
}

/**
 * Show the completed image with fade-in and regenerate button.
 */
function showImage(container, url, sceneId) {
    stopProgressMessages();
    isGenerating = false;

    const img = document.createElement('img');
    img.src = url;
    img.alt = 'Scene illustration';
    img.style.opacity = '0';
    img.style.transition = 'opacity 0.5s ease-in';

    img.onload = () => {
        container.innerHTML = '';
        container.appendChild(img);

        // Add regenerate button (only in active story, not gallery reader)
        if (sceneId && !document.querySelector('.reader-header')) {
            const btn = document.createElement('button');
            btn.className = 'btn-regenerate';
            btn.textContent = '\u21BB Regenerate';
            btn.onclick = () => retryImage(sceneId);
            container.appendChild(btn);
        }

        // Trigger fade-in
        requestAnimationFrame(() => {
            img.style.opacity = '1';
        });
    };

    img.onerror = () => {
        showFailedState(container, sceneId);
    };
}

/**
 * Poll for video generation status and swap placeholder when ready.
 */
function pollVideoStatus(sceneId) {
    const container = document.getElementById('scene-video-container');
    if (!container) return;

    const urlPrefix = document.body.dataset.urlPrefix || '';
    const maxAttempts = 60; // 5 minutes at 5s interval
    let attempts = 0;

    const poll = setInterval(async () => {
        attempts++;

        try {
            const response = await fetch(`${urlPrefix}/story/video/${sceneId}`);
            if (!response.ok) {
                clearInterval(poll);
                showVideoFailed(container, sceneId);
                return;
            }

            const data = await response.json();

            if (data.status === 'complete' && data.url) {
                clearInterval(poll);
                showVideo(container, data.url);
            } else if (data.status === 'failed') {
                clearInterval(poll);
                showVideoFailed(container, sceneId);
            } else if (attempts >= maxAttempts) {
                clearInterval(poll);
                showVideoFailed(container, sceneId);
            }
        } catch (err) {
            if (attempts >= maxAttempts) {
                clearInterval(poll);
                showVideoFailed(container, sceneId);
            }
        }
    }, 5000);
}

/**
 * Show completed video with fade-in.
 */
function showVideo(container, url) {
    container.innerHTML = `
        <video controls playsinline preload="metadata" style="opacity:0;transition:opacity 0.5s ease-in">
            <source src="${url}" type="video/mp4">
        </video>
    `;
    const video = container.querySelector('video');
    video.onloadedmetadata = () => {
        video.style.opacity = '1';
    };
}

/**
 * Show video failed state with retry button.
 */
function showVideoFailed(container, sceneId) {
    container.innerHTML = `
        <div class="video-failed">
            <p>Video generation failed</p>
            <button class="btn-retry" onclick="retryVideo('${sceneId}')">Retry</button>
        </div>
    `;
}

/**
 * Retry a failed video generation.
 */
async function retryVideo(sceneId) {
    const container = document.getElementById('scene-video-container');
    if (!container) return;

    const urlPrefix = document.body.dataset.urlPrefix || '';

    try {
        const response = await fetch(`${urlPrefix}/story/video/${sceneId}/retry`, {
            method: 'POST',
        });
        const data = await response.json();

        if (data.status === 'generating') {
            container.innerHTML = '<div class="video-loading">Generating video clip...</div>';
            pollVideoStatus(sceneId);
        }
    } catch (err) {
        showVideoFailed(container, sceneId);
    }
}

/**
 * Show loading overlay when starting a story or making a choice.
 */
function showLoading(message) {
    const overlay = document.createElement('div');
    overlay.className = 'loading-overlay';
    overlay.innerHTML = `
        <div class="spinner"></div>
        <p>${message || 'Generating your story...'}</p>
    `;
    document.body.appendChild(overlay);
}

// Attach loading overlay to story forms
document.addEventListener('DOMContentLoaded', () => {
    // Start story form
    const startForm = document.getElementById('start-form');
    if (startForm) {
        startForm.addEventListener('submit', () => {
            showLoading('Creating your adventure...');
        });
    }

    // Choice buttons (forms)
    document.querySelectorAll('.choice-form').forEach(form => {
        form.addEventListener('submit', () => {
            showLoading('Continuing the story...');
        });
    });
});
