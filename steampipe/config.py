from pathlib import Path

def get_config_path(filename):
    return Path.home() / ".config" / "steampipe" / filename

CLIP_DIR = Path.home() / ".local" / "share" / "Steam" / "userdata" / "1476367180" / "gamerecordings" / "clips"
CREDENTIALS_FILE = get_config_path("credentials.json")
TOKEN_FILE = get_config_path("token.pickle")
