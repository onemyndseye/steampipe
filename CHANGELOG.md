# Changelog

## [v0.0.5-dev] - 2025-4-19
-- Moved CLIPS_DIR out of config.py to required arg of --watch (steampipe --watch /path/to/clips)



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
