/**
 * Prompt Edit — edit image prompt and regenerate.
 * Usage: initPromptEdit({ container, prompt, regenerateUrl })
 */
function initPromptEdit(config) {
    var container = config.container;
    var originalPrompt = config.prompt || '';
    var regenerateUrl = config.regenerateUrl;

    if (!container || !originalPrompt || !regenerateUrl) return;

    // Create edit icon button
    var editBtn = document.createElement('button');
    editBtn.className = 'prompt-edit-icon';
    editBtn.innerHTML = '&#9998;';  // pencil
    editBtn.setAttribute('aria-label', 'Edit image prompt');
    editBtn.setAttribute('type', 'button');
    container.appendChild(editBtn);

    // Create edit panel (hidden by default)
    var panel = document.createElement('div');
    panel.className = 'prompt-edit-panel hidden';

    var textarea = document.createElement('textarea');
    textarea.className = 'prompt-edit-textarea';
    textarea.value = originalPrompt;
    panel.appendChild(textarea);

    var actions = document.createElement('div');
    actions.className = 'prompt-edit-actions';

    var regenBtn = document.createElement('button');
    regenBtn.className = 'btn-regenerate-prompt';
    regenBtn.textContent = 'Regenerate';
    regenBtn.setAttribute('type', 'button');
    actions.appendChild(regenBtn);

    var cancelBtn = document.createElement('button');
    cancelBtn.className = 'btn-cancel-prompt';
    cancelBtn.textContent = 'Cancel';
    cancelBtn.setAttribute('type', 'button');
    actions.appendChild(cancelBtn);

    var loadingEl = document.createElement('span');
    loadingEl.className = 'prompt-edit-loading';
    loadingEl.style.display = 'none';
    loadingEl.textContent = 'Generating...';
    actions.appendChild(loadingEl);

    panel.appendChild(actions);

    var errorEl = document.createElement('div');
    errorEl.className = 'prompt-edit-error';
    errorEl.style.display = 'none';
    panel.appendChild(errorEl);

    // Insert panel after the container
    container.parentNode.insertBefore(panel, container.nextSibling);

    // Event handlers
    editBtn.addEventListener('click', function() {
        panel.classList.remove('hidden');
        textarea.value = originalPrompt;
        errorEl.style.display = 'none';
        textarea.focus();
    });

    cancelBtn.addEventListener('click', function() {
        panel.classList.add('hidden');
        errorEl.style.display = 'none';
    });

    regenBtn.addEventListener('click', function() {
        var newPrompt = textarea.value.trim();
        if (!newPrompt) {
            errorEl.textContent = 'Prompt cannot be empty.';
            errorEl.style.display = 'block';
            return;
        }

        errorEl.style.display = 'none';
        regenBtn.disabled = true;
        loadingEl.style.display = 'inline';

        fetch(regenerateUrl, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ prompt: newPrompt })
        })
        .then(function(resp) { return resp.json(); })
        .then(function(data) {
            if (data.status === 'complete' && data.image_url) {
                // Gallery reader: synchronous, image_url returned
                var img = container.querySelector('img');
                if (img) {
                    img.src = data.image_url;
                }
                originalPrompt = newPrompt;
                panel.classList.add('hidden');
            } else if (data.status === 'generating') {
                // Active story: async, will poll for completion
                originalPrompt = newPrompt;
                panel.classList.add('hidden');
                // Trigger existing poll mechanism if available
                if (typeof pollImageStatus === 'function') {
                    var sceneId = container.getAttribute('data-scene-id');
                    if (sceneId) {
                        // Show generating placeholder
                        container.innerHTML = '';
                        var placeholder = document.createElement('div');
                        placeholder.className = 'image-generating-placeholder';
                        var span = document.createElement('span');
                        span.className = 'image-progress-text';
                        span.textContent = 'Regenerating your illustration...';
                        placeholder.appendChild(span);
                        container.appendChild(placeholder);
                        pollImageStatus(sceneId);
                    }
                }
            } else if (data.status === 'failed') {
                errorEl.textContent = data.error || 'Image generation failed. Try again.';
                errorEl.style.display = 'block';
            }
        })
        .catch(function(err) {
            errorEl.textContent = 'Request failed. Please try again.';
            errorEl.style.display = 'block';
        })
        .finally(function() {
            regenBtn.disabled = false;
            loadingEl.style.display = 'none';
        });
    });
}
