/**
 * Ambient audio module — plays background audio based on scene content keywords.
 * Usage: initAmbiance({ sceneContent: '...', bedtimeMode: false })
 */

var AMBIANCE_CATEGORIES = [
    { name: 'forest', file: '/static/audio/forest.mp3', keywords: ['forest', 'trees', 'woods', 'woodland', 'jungle'] },
    { name: 'ocean', file: '/static/audio/ocean.mp3', keywords: ['ocean', 'sea', 'beach', 'waves', 'shore', 'lake', 'river', 'water'] },
    { name: 'dragon', file: '/static/audio/dragon.mp3', keywords: ['dragon', 'fire', 'flame', 'lava', 'volcano', 'inferno'] },
    { name: 'magic', file: '/static/audio/magic.mp3', keywords: ['magic', 'spell', 'wizard', 'witch', 'enchant', 'fairy', 'wand', 'potion'] },
    { name: 'space', file: '/static/audio/space.mp3', keywords: ['space', 'spaceship', 'galaxy', 'planet', 'star', 'rocket', 'alien', 'cosmic'] },
    { name: 'city', file: '/static/audio/city.mp3', keywords: ['city', 'town', 'market', 'street', 'tavern', 'inn', 'castle', 'kingdom'] },
    { name: 'storm', file: '/static/audio/storm.mp3', keywords: ['storm', 'thunder', 'lightning', 'rain', 'wind'] }
];

var MUTE_KEY = 'ambiance_muted';

function matchCategory(content) {
    var lower = content.toLowerCase();
    for (var i = 0; i < AMBIANCE_CATEGORIES.length; i++) {
        var cat = AMBIANCE_CATEGORIES[i];
        for (var k = 0; k < cat.keywords.length; k++) {
            if (lower.indexOf(cat.keywords[k]) !== -1) {
                return cat;
            }
        }
    }
    return null;
}

function initAmbiance(config) {
    var sceneContent = config.sceneContent || '';
    var bedtimeMode = config.bedtimeMode || false;

    var category = matchCategory(sceneContent);
    if (!category) return null;

    // Read mute state from localStorage
    var stored = localStorage.getItem(MUTE_KEY);
    var muted;
    if (bedtimeMode && stored === null) {
        // Bedtime mode defaults to muted (unless user explicitly unmuted)
        muted = true;
    } else {
        muted = stored === 'true';
    }

    // Create audio element
    var audio = new Audio(category.file);
    audio.loop = true;
    audio.volume = 0.15;

    // Create mute toggle button
    var btn = document.createElement('button');
    btn.className = 'ambiance-toggle';
    btn.type = 'button';
    btn.setAttribute('aria-label', 'Toggle ambient audio');
    btn.id = 'ambiance-toggle';

    function updateIcon() {
        btn.textContent = muted ? '\u{1F507}' : '\u{1F50A}';
    }
    updateIcon();

    function setMuted(val) {
        muted = val;
        localStorage.setItem(MUTE_KEY, String(muted));
        updateIcon();
        if (muted) {
            audio.pause();
        } else {
            var promise = audio.play();
            if (promise && promise.catch) {
                promise.catch(function() {
                    // Autoplay blocked — stay muted
                    muted = true;
                    localStorage.setItem(MUTE_KEY, 'true');
                    updateIcon();
                });
            }
        }
    }

    btn.addEventListener('click', function() {
        setMuted(!muted);
    });

    document.body.appendChild(btn);

    // Attempt autoplay if not muted
    if (!muted) {
        var promise = audio.play();
        if (promise && promise.catch) {
            promise.catch(function() {
                // Autoplay blocked — fall back to muted state
                muted = true;
                localStorage.setItem(MUTE_KEY, 'true');
                updateIcon();
            });
        }
    }

    return { audio: audio, button: btn, category: category.name };
}
