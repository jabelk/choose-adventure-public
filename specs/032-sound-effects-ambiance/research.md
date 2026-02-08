# Research: Sound Effects / Ambiance

## Audio File Source

**Decision**: Generate placeholder audio files using simple tone generation, then replace with royalty-free clips later.

**Rationale**: The feature needs audio files to function, but sourcing high-quality royalty-free ambient loops is a manual curation step. For initial implementation, we generate short silent/tone placeholder MP3 files so the JS module can be fully tested. Real audio files can be swapped in at any time without code changes.

**Alternatives considered**:
- Using a web audio API to generate tones programmatically — rejected because real ambient sounds (birds, waves) can't be synthesized this way.
- Delaying implementation until audio files are sourced — rejected because the code and tests can be built independently of the audio content.

## Mute State Persistence

**Decision**: Use `localStorage` for mute preference, keyed as `ambiance_muted`.

**Rationale**: localStorage persists across page navigations within the same browser without requiring server-side state. The mute preference is presentation-only and doesn't need to be stored on the story or session model.

**Alternatives considered**:
- Cookie-based persistence — rejected because cookies add server overhead and have size limits.
- Session-scoped (no persistence) — rejected because the spec requires mute to persist across scene navigations.

## Autoplay Handling

**Decision**: Attempt autoplay, catch the promise rejection, and silently fall back to muted state.

**Rationale**: Modern browsers block autoplay with sound by default. The standard pattern is to attempt `audio.play()`, catch the rejection, and show the audio as muted until the user interacts with the page. After one user interaction (like clicking the mute toggle or any button), autoplay works for subsequent navigations.

**Alternatives considered**:
- Not attempting autoplay at all — rejected because it would require an extra click on every scene.
- Playing at zero volume first — rejected because browsers detect this as a workaround.
