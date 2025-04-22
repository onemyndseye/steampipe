#!/bin/bash



DIR=/home/onemyndseye/.local/share/Steam/userdata/1476367180/gamerecordings/clips
DISCORD=https://discord.com/api/webhooks/1364065772967690331/eXt_OOZjgJjP1rb8AOKr_sIzIZmeGcfsLnJyPy8ndqOrTpO4jCHaHfCsUdY3TkhEOsCD

python3 -m steampipe --watch $DIR --upload --privacy unlisted --discord "$DISCORD"


