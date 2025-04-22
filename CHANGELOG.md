# Changelog


## [0.0.7-dev] - 2025-04-20

### Added
- `--discord <URL>` CLI argument for sending upload notifications to Discord
- Discord messages with game title and YouTube link
- YouTube link printed in CLI log after successful upload

### Changed
- `upload_video()` now returns the actual YouTube video ID
- `processor.upload()` now wraps YouTube ID as a proper short URL (`youtu.be/<id>`)



## [0.0.6-dev] - 2025-04-19

### Changed
- Replaced real-time `watchdog` logic with polling loop
- Added CLI args `--sync-delay` and `--proc-delay`
- All clips are now processed only if `.steampiped` marker file is missing
- Removed complex timing/race heuristics
- Greatly improved stability for large or delayed clips

### Added
- `.steampiped` marker written on successful upload (or simulated in dry-run)

### Removed
- No longer uses filesystem event detection (watchdog)


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
