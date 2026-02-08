/**
 * Voice Input Module
 *
 * Handles speech-to-text for the story prompt textarea.
 * Path A: Browser-native SpeechRecognition (Chrome, Safari, Edge)
 * Path B: MediaRecorder + server-side Whisper transcription (Firefox fallback)
 */

var MAX_RECORDING_SECONDS = 60;
var SILENCE_TIMEOUT_MS = 10000;

/**
 * Initialize voice input for a given textarea.
 * @param {string} textareaId - ID of the textarea to fill with transcribed text
 * @param {string} urlPrefix - Tier URL prefix (e.g., "/kids")
 */
function initVoiceInput(textareaId, urlPrefix) {
    var textarea = document.getElementById(textareaId);
    var micBtn = document.getElementById('voice-mic-btn');
    var errorSpan = document.getElementById('voice-error');

    if (!textarea || !micBtn) return;

    var SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    var hasBrowserSpeech = !!SpeechRecognition;
    var state = 'idle'; // idle | recording | processing
    var recognition = null;
    var mediaRecorder = null;
    var audioChunks = [];
    var maxTimer = null;
    var silenceTimer = null;
    var serverAvailable = false;

    function setState(newState) {
        state = newState;
        micBtn.classList.remove('mic-idle', 'mic-recording', 'mic-processing');
        if (newState === 'idle') {
            micBtn.classList.add('mic-idle');
            micBtn.setAttribute('aria-label', 'Voice input');
        } else if (newState === 'recording') {
            micBtn.classList.add('mic-recording');
            micBtn.setAttribute('aria-label', 'Stop recording');
        } else if (newState === 'processing') {
            micBtn.classList.add('mic-processing');
            micBtn.setAttribute('aria-label', 'Processing audio');
        }
    }

    function showError(msg) {
        if (errorSpan) {
            errorSpan.textContent = msg;
            errorSpan.style.display = msg ? 'block' : 'none';
        }
    }

    function clearError() {
        showError('');
    }

    function appendText(text) {
        if (!text || !text.trim()) return;
        var current = textarea.value;
        if (current && !current.endsWith(' ') && !current.endsWith('\n')) {
            textarea.value = current + ' ' + text.trim();
        } else {
            textarea.value = current + text.trim();
        }
    }

    function clearTimers() {
        if (maxTimer) { clearTimeout(maxTimer); maxTimer = null; }
        if (silenceTimer) { clearTimeout(silenceTimer); silenceTimer = null; }
    }

    // --- Browser-native SpeechRecognition (US1) ---

    function startBrowserRecognition() {
        clearError();
        recognition = new SpeechRecognition();
        recognition.lang = 'en-US';
        recognition.interimResults = true;
        recognition.continuous = false;

        var finalTranscript = '';

        recognition.onresult = function(event) {
            // Reset silence timer on any result
            if (silenceTimer) { clearTimeout(silenceTimer); }
            silenceTimer = setTimeout(function() {
                if (state === 'recording') {
                    recognition.stop();
                }
            }, SILENCE_TIMEOUT_MS);

            var interim = '';
            for (var i = event.resultIndex; i < event.results.length; i++) {
                if (event.results[i].isFinal) {
                    finalTranscript += event.results[i][0].transcript;
                } else {
                    interim += event.results[i][0].transcript;
                }
            }
        };

        recognition.onend = function() {
            clearTimers();
            if (finalTranscript) {
                appendText(finalTranscript);
            }
            setState('idle');
        };

        recognition.onerror = function(event) {
            clearTimers();
            setState('idle');
            if (event.error === 'not-allowed') {
                showError('Microphone access is needed. Please allow microphone permission and try again.');
            } else if (event.error === 'no-speech') {
                // Silent timeout — no error to show
            } else if (event.error === 'network') {
                showError('Speech recognition requires an internet connection.');
            } else if (event.error === 'audio-capture') {
                showError('No microphone found. Please connect a microphone and try again.');
            } else if (event.error === 'aborted') {
                // User stopped — no error
            } else {
                showError('Voice input error: ' + event.error);
            }
        };

        recognition.start();
        setState('recording');

        // Max recording timer
        maxTimer = setTimeout(function() {
            if (state === 'recording' && recognition) {
                recognition.stop();
            }
        }, MAX_RECORDING_SECONDS * 1000);

        // Initial silence timer
        silenceTimer = setTimeout(function() {
            if (state === 'recording' && recognition) {
                recognition.stop();
            }
        }, SILENCE_TIMEOUT_MS);
    }

    function stopBrowserRecognition() {
        if (recognition) {
            recognition.stop();
            recognition = null;
        }
        clearTimers();
    }

    // --- MediaRecorder + server fallback (US2) ---

    function startMediaRecording() {
        clearError();
        audioChunks = [];

        navigator.mediaDevices.getUserMedia({ audio: true }).then(function(stream) {
            // Detect best MIME type
            var mimeType = 'audio/webm;codecs=opus';
            if (!MediaRecorder.isTypeSupported(mimeType)) {
                mimeType = 'audio/webm';
            }
            if (!MediaRecorder.isTypeSupported(mimeType)) {
                mimeType = 'audio/mp4';
            }
            if (!MediaRecorder.isTypeSupported(mimeType)) {
                mimeType = '';  // Let browser pick default
            }

            var options = mimeType ? { mimeType: mimeType } : {};
            mediaRecorder = new MediaRecorder(stream, options);

            mediaRecorder.ondataavailable = function(event) {
                if (event.data.size > 0) {
                    audioChunks.push(event.data);
                }
            };

            mediaRecorder.onstop = function() {
                // Stop all tracks
                stream.getTracks().forEach(function(track) { track.stop(); });
                clearTimers();

                if (audioChunks.length === 0) {
                    setState('idle');
                    return;
                }

                setState('processing');
                var blob = new Blob(audioChunks, { type: mediaRecorder.mimeType || 'audio/webm' });
                uploadAudio(blob);
            };

            mediaRecorder.start();
            setState('recording');

            // Max recording timer
            maxTimer = setTimeout(function() {
                if (state === 'recording' && mediaRecorder && mediaRecorder.state === 'recording') {
                    mediaRecorder.stop();
                }
            }, MAX_RECORDING_SECONDS * 1000);

        }).catch(function(err) {
            setState('idle');
            if (err.name === 'NotAllowedError') {
                showError('Microphone access is needed. Please allow microphone permission and try again.');
            } else if (err.name === 'NotFoundError') {
                showError('No microphone found. Please connect a microphone and try again.');
            } else {
                showError('Could not access microphone: ' + err.message);
            }
        });
    }

    function stopMediaRecording() {
        if (mediaRecorder && mediaRecorder.state === 'recording') {
            mediaRecorder.stop();
        }
        clearTimers();
    }

    function uploadAudio(blob) {
        var ext = 'webm';
        if (blob.type && blob.type.indexOf('mp4') !== -1) ext = 'mp4';
        if (blob.type && blob.type.indexOf('ogg') !== -1) ext = 'ogg';

        var formData = new FormData();
        formData.append('audio', blob, 'recording.' + ext);

        fetch(urlPrefix + '/voice/transcribe', {
            method: 'POST',
            body: formData,
        }).then(function(response) {
            if (!response.ok) {
                return response.json().then(function(data) {
                    throw new Error(data.error || 'Transcription failed');
                });
            }
            return response.json();
        }).then(function(data) {
            if (data.text) {
                appendText(data.text);
            }
            setState('idle');
        }).catch(function(err) {
            setState('idle');
            showError('Transcription failed: ' + err.message);
        });
    }

    // --- Button click handler ---

    micBtn.addEventListener('click', function() {
        if (state === 'recording') {
            // Stop
            if (hasBrowserSpeech && recognition) {
                stopBrowserRecognition();
            } else {
                stopMediaRecording();
            }
        } else if (state === 'idle') {
            clearError();
            if (hasBrowserSpeech) {
                startBrowserRecognition();
            } else if (serverAvailable) {
                startMediaRecording();
            }
        }
        // Ignore clicks during 'processing'
    });

    // --- Initialization ---

    setState('idle');

    if (hasBrowserSpeech) {
        // Browser supports SpeechRecognition — mic button is ready
        micBtn.style.display = '';
    } else {
        // Check if server-side fallback is available
        fetch(urlPrefix + '/voice/status').then(function(response) {
            return response.json();
        }).then(function(data) {
            if (data.available) {
                serverAvailable = true;
                micBtn.style.display = '';
            } else {
                micBtn.style.display = 'none';
            }
        }).catch(function() {
            micBtn.style.display = 'none';
        });
    }
}
