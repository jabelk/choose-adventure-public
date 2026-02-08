/**
 * TTS Player — Read Aloud narration controller.
 *
 * Usage: initTTSPlayer({ sceneId, urlPrefix, ttsUrl, autoplay })
 */

(function() {
    'use strict';

    var audio = null;
    var state = 'idle'; // idle | loading | playing
    var debounceTimer = null;

    function initTTSPlayer(opts) {
        var sceneId = opts.sceneId;
        var urlPrefix = opts.urlPrefix || '';
        var ttsUrl = opts.ttsUrl; // full URL to fetch audio
        var autoplay = opts.autoplay === true || opts.autoplay === 'true';

        var btn = document.getElementById('tts-play-btn');
        if (!btn) return;

        var voiceSelect = document.getElementById('tts-voice-select');
        var autoplayToggle = document.getElementById('tts-autoplay-toggle');

        btn.addEventListener('click', function() {
            handlePlayStop(btn, ttsUrl, urlPrefix, voiceSelect);
        });

        // Voice selector change handler
        if (voiceSelect) {
            voiceSelect.addEventListener('change', function() {
                // Persist preference
                fetch(urlPrefix + '/tts/preferences', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ voice: voiceSelect.value })
                });
                // If currently playing, stop and replay with new voice
                if (state === 'playing') {
                    stopAudio(btn);
                    setTimeout(function() {
                        handlePlayStop(btn, ttsUrl, urlPrefix, voiceSelect);
                    }, 100);
                }
            });
        }

        // Auto-play toggle handler
        if (autoplayToggle) {
            autoplayToggle.addEventListener('change', function() {
                var isOn = autoplayToggle.checked;
                fetch(urlPrefix + '/tts/preferences', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ autoplay: isOn })
                });
            });
        }

        // Stop audio when navigating away
        window.addEventListener('beforeunload', function() {
            if (audio) {
                audio.pause();
                audio = null;
            }
        });

        // Stop audio when choice forms are submitted
        document.querySelectorAll('.choice-form').forEach(function(form) {
            form.addEventListener('submit', function() {
                if (audio) {
                    audio.pause();
                    audio = null;
                    setState(btn, 'idle');
                }
            });
        });

        // Auto-play on load if enabled
        if (autoplay) {
            setTimeout(function() {
                handlePlayStop(btn, ttsUrl, urlPrefix, voiceSelect);
            }, 500);
        }
    }

    function handlePlayStop(btn, ttsUrl, urlPrefix, voiceSelect) {
        // Debounce rapid taps
        if (debounceTimer) return;
        debounceTimer = setTimeout(function() { debounceTimer = null; }, 300);

        if (state === 'playing' || state === 'loading') {
            stopAudio(btn);
            return;
        }

        // Build URL with voice param
        var url = ttsUrl;
        if (voiceSelect && voiceSelect.value) {
            url += (url.indexOf('?') === -1 ? '?' : '&') + 'voice=' + encodeURIComponent(voiceSelect.value);
        }

        setState(btn, 'loading');

        fetch(url)
            .then(function(response) {
                if (!response.ok) {
                    throw new Error('TTS request failed: ' + response.status);
                }
                return response.blob();
            })
            .then(function(blob) {
                if (state !== 'loading') return; // user cancelled during load

                var objectUrl = URL.createObjectURL(blob);
                audio = new Audio(objectUrl);

                audio.addEventListener('ended', function() {
                    URL.revokeObjectURL(objectUrl);
                    audio = null;
                    setState(btn, 'idle');
                    clearHighlight();
                });

                audio.addEventListener('error', function() {
                    URL.revokeObjectURL(objectUrl);
                    audio = null;
                    setState(btn, 'idle');
                    showError(btn);
                    clearHighlight();
                });

                audio.play().then(function() {
                    setState(btn, 'playing');
                    startHighlight(audio);
                }).catch(function() {
                    URL.revokeObjectURL(objectUrl);
                    audio = null;
                    setState(btn, 'idle');
                });
            })
            .catch(function(err) {
                setState(btn, 'idle');
                showError(btn);
            });
    }

    function stopAudio(btn) {
        if (audio) {
            audio.pause();
            audio.currentTime = 0;
            audio = null;
        }
        setState(btn, 'idle');
        clearHighlight();
    }

    function setState(btn, newState) {
        state = newState;
        btn.classList.remove('tts-idle', 'tts-loading', 'tts-playing');
        btn.classList.add('tts-' + newState);

        if (newState === 'idle') {
            btn.setAttribute('aria-label', 'Read aloud');
            btn.innerHTML = '<span class="tts-icon">&#x1F50A;</span>';
        } else if (newState === 'loading') {
            btn.setAttribute('aria-label', 'Loading audio...');
            btn.innerHTML = '<span class="tts-icon tts-spinner">&#x23F3;</span>';
        } else if (newState === 'playing') {
            btn.setAttribute('aria-label', 'Stop reading');
            btn.innerHTML = '<span class="tts-icon">&#x23F9;</span>';
        }
    }

    function showError(btn) {
        var original = btn.innerHTML;
        btn.innerHTML = '<span class="tts-icon tts-error">&#x26A0;</span>';
        setTimeout(function() {
            if (state === 'idle') {
                btn.innerHTML = '<span class="tts-icon">&#x1F50A;</span>';
            }
        }, 2000);
    }

    // --- Sentence Highlighting ---

    var highlightTimer = null;
    var sentences = [];
    var currentSentenceIndex = -1;

    function startHighlight(audioElement) {
        sentences = document.querySelectorAll('.tts-sentence');
        if (!sentences.length) return;

        currentSentenceIndex = 0;
        highlightSentence(0);

        // Estimate timing: ~150 WPM, calculate ms per sentence
        var durations = [];
        var totalWords = 0;
        sentences.forEach(function(s) {
            var words = s.textContent.trim().split(/\s+/).length;
            totalWords += words;
            durations.push(words);
        });

        if (totalWords === 0) return;

        // Use audio duration when available, otherwise estimate
        var waitForDuration = function() {
            var audioDuration = audioElement.duration;
            if (!audioDuration || isNaN(audioDuration)) {
                // Wait for metadata
                audioElement.addEventListener('loadedmetadata', function() {
                    scheduleHighlights(audioElement, durations, totalWords);
                });
                return;
            }
            scheduleHighlights(audioElement, durations, totalWords);
        };
        waitForDuration();
    }

    function scheduleHighlights(audioElement, durations, totalWords) {
        var audioDuration = audioElement.duration;
        if (!audioDuration || isNaN(audioDuration)) {
            audioDuration = totalWords / 2.5; // fallback: 150 WPM = 2.5 WPS
        }

        var msPerWord = (audioDuration * 1000) / totalWords;
        var elapsed = 0;

        for (var i = 1; i < durations.length; i++) {
            elapsed += durations[i - 1] * msPerWord;
            (function(index, delay) {
                var timer = setTimeout(function() {
                    if (state === 'playing') {
                        highlightSentence(index);
                    }
                }, delay);
                // Store timer for cleanup
                if (!highlightTimer) highlightTimer = [];
                if (Array.isArray(highlightTimer)) highlightTimer.push(timer);
            })(i, elapsed);
        }
    }

    function highlightSentence(index) {
        sentences.forEach(function(s, i) {
            s.classList.toggle('tts-highlight', i === index);
        });

        // Auto-scroll highlighted sentence into view
        if (sentences[index]) {
            sentences[index].scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
    }

    function clearHighlight() {
        if (Array.isArray(highlightTimer)) {
            highlightTimer.forEach(function(t) { clearTimeout(t); });
        }
        highlightTimer = null;
        currentSentenceIndex = -1;

        document.querySelectorAll('.tts-sentence.tts-highlight').forEach(function(s) {
            s.classList.remove('tts-highlight');
        });
    }

    // Expose to global scope
    window.initTTSPlayer = initTTSPlayer;
})();
