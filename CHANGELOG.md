# Changelog

### Added
  - Implemented Steam App List **caching system** (`steamappid.json`).
  - Caches Steam game titles at startup.
  - Automatically refreshes cache every **7 days**. Delete or use --force-refresh to rebuild
  - New CLI flag `--force-refresh` allows manual cache reset.   
  - Improved CLI options (`--force-refresh`) for better control.
  - Added robust error handling for Steam API failures and cache corruption.
  - Added --discord-desc and --discord-name to customize discord notifys
### Changed
  - `get_game_title(app_id)` now reads from local cache instead of fetching every call.
  - Steampipe now runs in cron friendly, single pass mode.
  - Discord thumbnail and Youtube thumbnail should match Steams generated thumbnail.

---



## [0.0.9-dev] - 2025-04-25

### Changed
- Moved to a cron-friendly config.   Steampipe will now interate through the given clips
  directory and act on new clips and then exit clean.  Run once from CLI or setup CRON
  job to handle scheduling.
- `--watch` renamed to `--clips`.
- Removed `--sync-delay` and `--proc-delay` options (no longer needed).
- `watch_clips()` function renamed to `find_clips()`.
- Updated README to reflect new flow and CLI usage.
- Improved Discord notification formatting with embedded thumbnails and styled messages.
- Minor internal code cleanups for path handling and mark



## [0.0.8-dev] - 2025-04-23

### Changed
- dropped ffmpeg in favor of gpac/mp4box to squash 4sec bug forever.




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
