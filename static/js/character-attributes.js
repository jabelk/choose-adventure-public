/**
 * Character Attribute Pill Selectors
 *
 * Renders grouped pill selectors for structured character creation.
 * Each attribute category is single-select (radio-style).
 * Composes a description preview from selected attributes.
 */

/**
 * Initialize attribute selectors inside a container.
 *
 * @param {string} containerId - DOM id of the container div
 * @param {Object} attributesConfig - Grouped attribute definitions from server
 *   { "physical": [ {key, label, options}, ... ], "personality": [...], "style": [...] }
 * @param {Object} preselected - Previously saved selections, e.g. { "hair_color": "Blonde" }
 * @param {string} fieldPrefix - Prefix for hidden field names (default "attr_")
 */
function initAttributeSelectors(containerId, attributesConfig, preselected, fieldPrefix) {
    var container = document.getElementById(containerId);
    if (!container) return;

    var prefix = fieldPrefix || 'attr_';
    var selected = preselected || {};
    var groupLabels = {
        'physical': 'Physical',
        'personality': 'Personality',
        'style': 'Style'
    };

    // Build UI for each group
    var groupOrder = ['physical', 'personality', 'style'];
    for (var g = 0; g < groupOrder.length; g++) {
        var groupKey = groupOrder[g];
        var attrs = attributesConfig[groupKey];
        if (!attrs || attrs.length === 0) continue;

        var sectionTitle = document.createElement('div');
        sectionTitle.className = 'attr-section-title';
        sectionTitle.textContent = groupLabels[groupKey] || groupKey;
        container.appendChild(sectionTitle);

        for (var i = 0; i < attrs.length; i++) {
            var attr = attrs[i];
            var group = document.createElement('div');
            group.className = 'attr-group';

            var label = document.createElement('div');
            label.className = 'attr-group-label';
            label.textContent = attr.label;
            group.appendChild(label);

            var pills = document.createElement('div');
            pills.className = 'attr-pills';

            // "None" option to deselect
            var noneLabel = document.createElement('label');
            noneLabel.className = 'attr-pill-label';
            var noneRadio = document.createElement('input');
            noneRadio.type = 'radio';
            noneRadio.name = prefix + attr.key;
            noneRadio.value = '';
            if (!selected[attr.key]) noneRadio.checked = true;
            noneRadio.addEventListener('change', updatePreview.bind(null, container, attributesConfig, prefix));
            var noneSpan = document.createElement('span');
            noneSpan.className = 'attr-pill';
            noneSpan.textContent = 'Any';
            noneLabel.appendChild(noneRadio);
            noneLabel.appendChild(noneSpan);
            pills.appendChild(noneLabel);

            for (var j = 0; j < attr.options.length; j++) {
                var opt = attr.options[j];
                var pillLabel = document.createElement('label');
                pillLabel.className = 'attr-pill-label';

                var radio = document.createElement('input');
                radio.type = 'radio';
                radio.name = prefix + attr.key;
                radio.value = opt;
                if (selected[attr.key] === opt) radio.checked = true;
                radio.addEventListener('change', updatePreview.bind(null, container, attributesConfig, prefix));

                var span = document.createElement('span');
                span.className = 'attr-pill';
                span.textContent = opt;

                pillLabel.appendChild(radio);
                pillLabel.appendChild(span);
                pills.appendChild(pillLabel);
            }

            group.appendChild(pills);
            container.appendChild(group);
        }
    }

    // Add composed description preview
    var preview = document.createElement('div');
    preview.className = 'attr-composed-preview';
    preview.id = containerId + '-preview';
    preview.textContent = '';
    container.appendChild(preview);

    // Initial preview
    updatePreview(container, attributesConfig, prefix);
}

/**
 * Read current selections and update the composed preview text.
 */
function updatePreview(container, attributesConfig, prefix) {
    var selections = {};
    var groupOrder = ['physical', 'personality', 'style'];
    for (var g = 0; g < groupOrder.length; g++) {
        var attrs = attributesConfig[groupOrder[g]];
        if (!attrs) continue;
        for (var i = 0; i < attrs.length; i++) {
            var checked = container.querySelector('input[name="' + prefix + attrs[i].key + '"]:checked');
            if (checked && checked.value) {
                selections[attrs[i].key] = checked.value;
            }
        }
    }

    // Compose description
    var parts = [];
    var physicalParts = [];
    if (selections.hair_color) {
        var hair = selections.hair_color.toLowerCase();
        if (selections.hair_length) {
            physicalParts.push(selections.hair_length.toLowerCase() + ' ' + hair + ' hair');
        } else {
            physicalParts.push(hair + ' hair');
        }
    }
    if (selections.eye_color) physicalParts.push(selections.eye_color.toLowerCase() + ' eyes');
    if (selections.skin_tone) physicalParts.push(selections.skin_tone.toLowerCase() + ' skin');
    if (selections.height) physicalParts.push(selections.height.toLowerCase());
    if (selections.body_type) physicalParts.push(selections.body_type.toLowerCase() + ' build');
    if (selections.bust_size) physicalParts.push(selections.bust_size + ' cup');
    if (physicalParts.length > 0) parts.push(physicalParts.join(', '));

    var personalityParts = [];
    if (selections.temperament) personalityParts.push(selections.temperament.toLowerCase());
    if (selections.energy) personalityParts.push(selections.energy.toLowerCase());
    if (selections.archetype) personalityParts.push(selections.archetype.toLowerCase());
    if (personalityParts.length > 0) parts.push(personalityParts.join(' and '));

    var styleParts = [];
    if (selections.clothing_style) styleParts.push(selections.clothing_style.toLowerCase() + ' style');
    if (selections.aesthetic_vibe) styleParts.push(selections.aesthetic_vibe.toLowerCase() + ' vibe');
    if (styleParts.length > 0) parts.push(styleParts.join(', '));

    var preview = document.getElementById(container.id + '-preview');
    if (preview) {
        if (parts.length > 0) {
            preview.textContent = parts.join('. ') + '.';
        } else {
            preview.textContent = 'Select attributes to compose a description...';
        }
    }
}

/**
 * Get current attribute selections from a container as a dict.
 *
 * @param {string} containerId
 * @param {string} fieldPrefix
 * @returns {Object} e.g. { "hair_color": "Blonde", "body_type": "Athletic" }
 */
function getAttributeSelections(containerId, fieldPrefix) {
    var container = document.getElementById(containerId);
    if (!container) return {};
    var prefix = fieldPrefix || 'attr_';
    var selections = {};
    var radios = container.querySelectorAll('input[type="radio"]:checked');
    for (var i = 0; i < radios.length; i++) {
        if (radios[i].value && radios[i].name.indexOf(prefix) === 0) {
            var key = radios[i].name.substring(prefix.length);
            selections[key] = radios[i].value;
        }
    }
    return selections;
}

/**
 * Disable or enable all attribute selectors in a container.
 */
function setAttributeSelectorsDisabled(containerId, disabled) {
    var container = document.getElementById(containerId);
    if (!container) return;
    var labels = container.querySelectorAll('.attr-pill-label');
    for (var i = 0; i < labels.length; i++) {
        if (disabled) {
            labels[i].classList.add('disabled');
        } else {
            labels[i].classList.remove('disabled');
        }
    }
}
