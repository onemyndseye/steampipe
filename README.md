# Steampipe

Steampipe is a automation tool that remuxes and uploads Steam gameplay clips to YouTube.  
It monitors your Steam recording folder, converts new clips to `.mp4`, and sends them directly to your channel.


## Features

- ✅ Syncs clips directory directly to Youtube
- ✅ Remux `.m4s` + `.mpd` chunks using `ffmpeg`
- ✅ Game title + timestamp metadata
- ✅ Uploads to YouTube via OAuth
- ✅ Dry-run support
- ✅ Optional Discord webhook notifications via `--discord`  

## Installation

```bash
git clone https://github.com/onemyndseye/steampipe.git
cd steampipe
python3 -m  .venv && source .venv/bin/activate
pip install -e .
```

## Usage

```bash
steampipe --watch /path/to/clips --upload --privacy unlisted
```

### Options

| Option         | Description                                   |
|----------------|-----------------------------------------------|
| `--watch DIR'  | Monitor for new clips in real-time            |
| `--upload`     | Upload to YouTube                             |
| `--dry-run`    | Show actions without doing them               |
| `--privacy`    | `public`, `unlisted`, or `private`            |
| `--prefix`     | Add prefix to uploaded video title            |
| `--sync-delay` | How often to poll for changes in seconds (30) |
| `--proc-delay` | Delay in seconds before processing (30)       |

## Configuration

- Steam clips must be recorded via **Steam’s built-in background recorder**
- Place your YouTube `credentials.json` file here:  
  `~/.config/steampipe/credentials.json`

## License

MIT © [onemyndseye](https://github.com/onemyndseye)
