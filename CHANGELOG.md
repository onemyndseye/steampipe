# Changelog


# Changelog

## [0.0.4-dev] - 2025-04-17

### 🔒 Stability & Hardening
- Added robust `wait_for_final_chunks()` logic to avoid premature remux
- Now waits for `.m4s` fragments to fully write before processing
- Validates the **first chunk referenced in `session.mpd`** exists before remuxing

### Logic Improvements
- Improved session readiness checks using `.m4s` count and total size + idle timer
- Smart fallback if metadata or game title cannot be resolved

### Bugfixes
- Fixed silent failures from partial remuxes due to early folder access
- Corrected timing race conditions during Steam background clip saving
- Cleaned up threading behavior around `watchdog` event dispatch


---


## [v0.0.3-dev] - 2025-04-17

### 🚀 Added
- Full Steam clip **remuxing** support using `ffmpeg` from `.mpd` and `.m4s` fragments
- Automatic **metadata extraction** from Steam JSON (`timeline_*.json`)
- Pulls **game title** via Steam API (`GetAppList`)
- Support for **YouTube uploads** via OAuth2 + YouTube Data API v3
- `--privacy` flag to control visibility (`unlisted`, `public`, `private`)
- **Dry run mode** to simulate output and upload safely
- Support for **real-time folder watching** using Watchdog
- Queue-based clip processor with single-worker thread (handles multiple clips reliably)

### 🛠️ Fixed
- Avoids premature remuxing by checking `.m4s` **chunk file stability**
- Prevents empty/0-second uploads
- Metadata properly sanitized for filesystem-safe output paths

### ⚠️ Known Issues
- Only processes the most recent chunk folder (no backfill/resume)
