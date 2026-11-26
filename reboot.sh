#!/bin/bash
set -euo pipefail

sleep 1
cd /home/pludunn/plubot
git pull
git add --all
git commit -m "auto commit" --allow-empty
git push --force
nohup uv run main.py &
sleep 3

