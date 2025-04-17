import os


class Config:
    CLIPS_DIR = os.path.expanduser(
        "~/.local/share/Steam/userdata/1476367180/gamerecordings/clips"
    )

    APP_ID_DB = {
        "553850": "HELLDIVERS™ 2",
        # Add more mappings as needed
    }
