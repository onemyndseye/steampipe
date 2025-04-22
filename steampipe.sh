#!/bin/bash

# --- User Configuration ---
STEAM_CLIPS_DIR="/path/to/clips"
PRIVACY="unlisted"
SYNC_DELAY=30
PROC_DELAY=30
PREFIX="[STEAMPIPE] "
DISCORD_WEBHOOK="https://discord.com/api/webhooks/your_webhook_here"




# --- End User Configuration ---


INSTALL_DIR="$HOME/.local/share/steampipe"
REPO_URL="https://github.com/onemyndseye/steampipe.git"
VENV_DIR="$INSTALL_DIR/.venv"


# --- First-time Setup ---
if [ ! -d "$INSTALL_DIR/.git" ]; then
  echo "[install] Cloning Steampipe repo into $INSTALL_DIR..."
  git clone "$REPO_URL" "$INSTALL_DIR"
fi

# --- Update repo (optional — remove these two lines if you want to pin to a version) ---
cd "$INSTALL_DIR" || exit 1
git pull origin main

# --- Virtual Environment Setup ---
if [ ! -d "$VENV_DIR" ]; then
  echo "[setup] Creating virtual environment in $VENV_DIR..."
  python3 -m venv "$VENV_DIR"
fi

source "$VENV_DIR/bin/activate"

# --- Install Python Dependencies ---
echo "[setup] Installing Python dependencies from requirements.txt..."
pip install --upgrade pip
pip install -r requirements.txt

# --- Launch Steampipe ---
echo "[launch] Running Steampipe..."
python3 -m steampipe \
  --watch "$STEAM_CLIPS_DIR" \
  --upload \
  --privacy "$PRIVACY" \
  --discord "$DISCORD_WEBHOOK" \
  --sync-delay "$SYNC_DELAY" \
  --proc-delay "$PROC_DELAY" \
  --prefix "$PREFIX"
