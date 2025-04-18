# steampipe/appid_cache.py

import json
import os
import time

CACHE_FILENAME = os.path.expanduser("~/.cache/steampipe_appid_cache.json")
CACHE_TTL = 60 * 60 * 24 * 7  # 1 week

def load_cache():
    if not os.path.exists(CACHE_FILENAME):
        return {}
    try:
        with open(CACHE_FILENAME, "r") as f:
            return json.load(f)
    except Exception:
        return {}

def save_cache(cache):
    os.makedirs(os.path.dirname(CACHE_FILENAME), exist_ok=True)
    with open(CACHE_FILENAME, "w") as f:
        json.dump(cache, f, indent=2)

def get_title(app_id, resolver_func):
    """Get game title from cache or resolve with fallback function."""
    cache = load_cache()

    entry = cache.get(app_id)
    if entry and (time.time() - entry["timestamp"] < CACHE_TTL):
        return entry["title"]

    # Fallback
    title = resolver_func(app_id)

    # Store result
    cache[app_id] = {
        "title": title,
        "timestamp": time.time()
    }
    save_cache(cache)
    return title
