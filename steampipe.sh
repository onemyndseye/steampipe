#!/bin/bash

# --- User Configuration ---
STEAM_CLIPS_DIR="/path/to/clips"
PRIVACY="unlisted"
PREFIX="[STEAMPIPE] "
DISCORD_WEBHOOK="https://discord.com/api/webhooks/your_webhook_here"
DISCORD_NAME="Steampipe: My Clips"

# --- End User Configuration ---

do_update() {

# Check if update is needed
echo "[update] Checking for updates..."
git fetch


# Check if update is needed
NEED_UPDATE=$(git status |grep "branch is behind")
if [ -n "$NEED_UPDATE" ]; then
  # Needs update
  git pull origin main
  UPDATED=true
fi
}

do_install() {

echo "[install] Cloning Steampipe repo into $INSTALL_DIR..."
mkdir -p $INSTALL_DIR || exit 1

git clone "$REPO_URL" "$INSTALL_DIR"

echo "[install] Creating virtual environment in $VENV_DIR..."
python3 -m venv "$VENV_DIR"
}



# ---  Init  ---
INSTALL_DIR="$HOME/.local/share/steampipe"
REPO_URL="https://github.com/onemyndseye/steampipe.git"
VENV_DIR="$INSTALL_DIR/.venv"


if [ ! -d "$INSTALL_DIR/.git" ]; then
  do_install
  UPDATED=true
else
  cd "$INSTALL_DIR" || exit 1
  # Check for updates
  do_update
fi


# --- Virtual Environment Setup ---
source "$VENV_DIR/bin/activate"

if [ "$UPDATED" = true ]; then
  echo "[setup] Installing dependencies from requirements.txt..."
  pip install --upgrade pip
  pip install --upgrade -r requirements.txt
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
