# Steampipe

Steampipe is a automation tool that remuxes and uploads Steam gameplay clips to YouTube.  
It monitors your Steam recording folder, converts new clips to `.mp4`, and sends them directly to your channel.


## Features

- ✅ Syncs clips directory directly to Youtube
- ✅ Remux `.m4s` + `.mpd` chunks using `gpac/MP4Box`
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

## Alt insallation
```bash
wget -O steampipe.sh https://raw.githubusercontent.com/onemyndseye/steampipe/main/steampipe.sh
chmod +x steampipe.sh
./steampipe.sh

```




## Usage

```bash
steampipe --clips /path/to/clips --upload --privacy unlisted
```

### Options

| Option         | Description                                   |
|----------------|-----------------------------------------------|
| `--clips DIR'  | Location for new clips                        |
| `--upload`     | Upload to YouTube                             |
| `--dry-run`    | Show actions without doing them               |
| `--privacy`    | `public`, `unlisted`, or `private`            |
| `--prefix`     | Add prefix to uploaded video title            |

## Configuration

- Steam clips must be recorded via **Steam’s built-in background recorder**
- Place your YouTube `credentials.json` file here:  
  `~/.config/steampipe/credentials.json`

## License

MIT © [onemyndseye](https://github.com/onemyndseye)
