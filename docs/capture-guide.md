# Screen Capture Guide — Pulse Portfolio Clip

Target: **30–60 seconds**. Shows the live status page updating, a fault being caught by the
monitor, and recovery. Suitable for embedding on a portfolio site.

---

## Prerequisites

Everything running before you hit record:

```bash
# Terminal 1 — full stack
docker compose up

# Terminal 2 — dbt build (run once after stack is up and data is flowing)
cd transform
dbt build --profiles-dir .

# Terminal 3 — monitor tail (keep this visible)
docker logs pulse-monitor --follow
```

Wait until `docker logs pulse-monitor` shows at least one `HEALTHY` line before recording.
The status page at `http://localhost:5173` should show green HEALTHY pill and a
"Last event" value under 10 s.

Browser: open `http://localhost:5173` full-screen or in a clean window.
Hide browser chrome if possible (F11 / presentation mode).

---

## Frame-by-frame script

### Frame 1 — "It's live" (0–12 s)

**Goal:** show the tiles actively updating.

1. Open `http://localhost:5173`.
2. Watch the "Last event" tile — it resets to a low number every 5 s as new events arrive.
3. Point out (in voiceover or a caption): "Events arriving every 0.5–2 seconds. Status page polls every 5 s."
4. Let it run for ~10 s so the viewer sees at least two update cycles.

What should be visible:
- Pulsing cyan dot (live indicator)
- HEALTHY pill (green)
- "Last event" ticking up then resetting
- "Rows today" incrementing across refreshes

---

### Frame 2 — "The fault" (12–30 s)

**Goal:** stop the generator and show the platform detect it.

In Terminal 2 (while still screen-capturing):

```bash
docker stop pulse-generator
```

Then switch back to `http://localhost:5173` and watch:

- **At ~5 s after stop:** "Last event" climbs past its usual value
- **At ~10 s:** status pill may flip to DEGRADED (amber) if the 5-minute freshness
  threshold is configured — or watch Terminal 3 where the monitor logs the check
- **In Terminal 3:** within 60 s the monitor prints a state-transition alert:

```
[2026-06-21 17:30:03 UTC] [WARN] PULSE DEGRADED
  Freshness : 312s
  Rows today: 6
  Tests     : 23/23 passing
  >> Data stale — last event 5m ago (warn threshold: 5m)
```

**Tip:** if 5 minutes is too long to wait for the clip, use the monitor log as the
fault evidence rather than waiting for the status page pill to change. Cut between
the live tiles and the terminal.

---

### Frame 3 — "Recovery" (30–45 s)

**Goal:** show the platform heal itself when the generator restarts.

```bash
docker start pulse-generator
```

Switch back to `http://localhost:5173`:
- "Last event" drops back to a low number within 5 s
- Status pill returns to HEALTHY (green) once the monitor's next check passes

In Terminal 3, the monitor logs the recovery:

```
[2026-06-21 17:35:03 UTC] [OK] PULSE HEALTHY
  Freshness : 2s
  Rows today: ...
  Tests     : 23/23 passing
```

---

### Optional Frame 4 — "The CI gate" (45–55 s)

If you want to show the CI story, cut to a browser tab open on GitHub Actions showing
the green `dbt CI` workflow run. Or, in the terminal:

```bash
cd transform
dbt build --profiles-dir .
```

The final line `Done. PASS=27 WARN=0 ERROR=0` on screen is a clean closing shot.

---

## Recording tips

**Tool:** OBS Studio (free) or Windows Game Bar (Win + G) for a quick local recording.

**Layout:**
- Status page browser window: left 60% of screen
- Monitor terminal (`docker logs --follow`): right 40%
- This lets the viewer see both the visual tiles and the textual alerts simultaneously

**Resolution:** 1920×1080 minimum. Record at 60fps if your machine allows — the tile
updates look smoother.

**Captions (optional but recommended):**
Add three text overlays timed to the frames:
- 0 s: `"Synthetic UK retail orders — 0.5–2s intervals"`
- 12 s: `"Stopping the generator..."`
- 30 s: `"Restarting — platform self-heals"`

**Export:**
- `.mp4` (H.264, ~10 MB) — full version for portfolio page
- `.gif` (first 15 s, 800px wide, 10fps) — embed in README and case study

**Where to link it:**
- `README.md` — add an `<img>` tag pointing to the `.gif` in `docs/`
- `docs/case-study.md` — embed the `.gif` after the "what you can see running" section
- Your portfolio site — link to the `.mp4` as an unlisted video or host on GitHub releases

---

## What to narrate / caption for an HR audience

If you add a voiceover or captions, use this language:

> "This is a live data pipeline I built from scratch. Every dot on that screen is a real
> order event arriving every second or two. The platform automatically checks each one —
> if a price is negative, or an order ID is missing, it blocks that record before it
> ever reaches a report. Here I'm stopping the data feed to show what happens: the
> platform detects the problem within seconds and raises an alert. When the feed comes
> back, it recovers on its own. No manual intervention."

That narration covers: live data, automated quality checks, fault detection, alerting,
and self-healing — all in under 30 seconds.
