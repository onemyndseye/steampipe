#!/bin/bash

# --- User Configuration ---
STEAM_CLIPS_DIR="/path/to/clips"
PRIVACY="unlisted"
PREFIX="[STEAMPIPE] "
DISCORD_WEBHOOK="https://discord.com/api/webhooks/your_webhook_here"
DISCORD_NAME="Steampipe"



# --- End User Configuration ---
INSTALL_DIR="$HOME/.local/share/steampipe"
REPO_URL="https://github.com/onemyndseye/steampipe.git"
VENV_DIR="$INSTALL_DIR/.venv"



# --- First-time Setup ---
if [ ! -d "$INSTALL_DIR/.git" ]; then
  echo "[install] Cloning Steampipe repo into $INSTALL_DIR..."
  git clone "$REPO_URL" "$INSTALL_DIR"
fi

cd "$INSTALL_DIR" || exit 1

# --- Pull and detect update ---
echo "[update] Checking for updates..."
UPDATE_OUTPUT=$(git pull origin main)
if [[ "$UPDATE_OUTPUT" == *"Already up to date."* ]]; then
  UPDATED=false
  echo "[update] Repo is up to date."
else
  UPDATED=true
  echo "[update] Repo has changed."
fi

# --- Virtual Environment Setup ---
if [ ! -d "$VENV_DIR" ]; then
  echo "[setup] Creating virtual environment in $VENV_DIR..."
  python3 -m venv "$VENV_DIR"
  UPDATED=true
fi

source "$VENV_DIR/bin/activate"

# --- Install requirements only if needed ---
if [ "$UPDATED" = true ]; then
  echo "[setup] Installing dependencies from requirements.txt..."
  pip install --upgrade pip
  pip install -r requirements.txt
fi

# --- Launch Steampipe ---
echo "[launch] Running Steampipe..."
python3 -m steampipe \
  --clips "$STEAM_CLIPS_DIR" \
  --upload \
  --privacy "$PRIVACY" \
  --discord "$DISCORD_WEBHOOK" \
  --discord-name "$DISCORD_NAME" \
  --prefix "$PREFIX" \
  "$@"
