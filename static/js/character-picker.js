/**
 * Character Picker — Multi-select roster character picker for story start form.
 */

var _pickerContainer = null;

function updatePickerCount() {
    if (!_pickerContainer) return;
    var checked = _pickerContainer.querySelectorAll('input[type="checkbox"]:checked').length;
    var countEl = _pickerContainer.querySelector('.character-picker-count');
    if (countEl) {
        countEl.textContent = checked > 0 ? checked + ' selected' : '';
    }
    // Update hidden fields
    _syncHiddenFields();
}

function _syncHiddenFields() {
    if (!_pickerContainer) return;
    // Remove existing hidden roster_character_ids fields
    var form = _pickerContainer.closest('form');
    if (!form) return;
    form.querySelectorAll('input[name="roster_character_ids"]').forEach(function(el) {
        el.remove();
    });
    // Add new hidden fields for each checked character
    var checked = _pickerContainer.querySelectorAll('input[type="checkbox"]:checked');
    checked.forEach(function(cb) {
        var hidden = document.createElement('input');
        hidden.type = 'hidden';
        hidden.name = 'roster_character_ids';
        hidden.value = cb.value;
        form.appendChild(hidden);
    });
}

function initCharacterPicker(characters, preselectedIds) {
    _pickerContainer = document.getElementById('character-picker');
    if (!_pickerContainer) return;

    preselectedIds = preselectedIds || [];

    if (!characters || characters.length === 0) {
        _pickerContainer.innerHTML = '<p class="character-picker-empty">No saved characters. <a href="' +
            _pickerContainer.dataset.charactersUrl + '">Create one</a></p>';
        return;
    }

    var html = '<div class="character-picker-count"></div>';
    html += '<div class="character-picker-list">';

    characters.forEach(function(char) {
        var isChecked = preselectedIds.indexOf(char.character_id) !== -1;
        var truncDesc = char.description.length > 60 ? char.description.substring(0, 60) + '...' : char.description;
        html += '<label class="character-picker-item">';
        html += '<input type="checkbox" value="' + char.character_id + '"';
        html += ' data-character-name="' + char.name.replace(/"/g, '&quot;') + '"';
        if (isChecked) html += ' checked';
        html += '>';
        if (char.photo_urls && char.photo_urls.length > 0) {
            html += '<img class="character-picker-thumb" src="' + char.photo_urls[0] + '" alt="">';
        }
        html += '<span class="character-picker-info">';
        html += '<span class="character-picker-name">' + char.name + '</span>';
        html += '<span class="character-picker-desc">' + truncDesc + '</span>';
        html += '</span>';
        html += '</label>';
    });

    html += '</div>';
    _pickerContainer.innerHTML = html;

    // Attach change listeners
    _pickerContainer.querySelectorAll('input[type="checkbox"]').forEach(function(cb) {
        cb.addEventListener('change', updatePickerCount);
    });

    // Initial sync
    updatePickerCount();
}
