# Data Model: Image Retry & Polish

## Existing Entities (no changes needed)

### Image (already exists in app/models.py)

| Field | Type | Description |
|-------|------|-------------|
| prompt | str | The image generation prompt |
| status | ImageStatus | PENDING, GENERATING, COMPLETE, FAILED |
| url | str or None | Path to the generated image file |
| error | str or None | Error message if generation failed |

### ImageStatus (already exists in app/models.py)

```
PENDING → GENERATING → COMPLETE
                     → FAILED → GENERATING (retry) → COMPLETE
                                                    → FAILED
```

**No model changes required.** The existing `Image` and `ImageStatus` models already support all the states needed for retry and regeneration. The retry flow simply resets `status` back to `PENDING`/`GENERATING` and clears `error`.

## State Transitions

```
                    ┌──────────────────────┐
                    │                      │
                    v                      │
PENDING ──> GENERATING ──> COMPLETE        │
                │              │           │
                v              v           │
              FAILED    [regenerate] ──────┘
                │
                v
           [retry] ───────────────────────┘
```

### Retry Flow
1. Image is in FAILED state
2. User clicks "Retry"
3. POST to retry endpoint resets status to PENDING, clears error
4. Background task starts → status becomes GENERATING
5. On success → COMPLETE with new URL
6. On failure → FAILED again (user can retry again)

### Regenerate Flow
1. Image is in COMPLETE state
2. User clicks "Regenerate"
3. POST to retry endpoint resets status to PENDING, clears url
4. Same flow as retry from here
