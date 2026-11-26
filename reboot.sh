#!/bin/bash
set -euo pipefail

cd /home/pludunn/plubot
git add --all
git commit -m "auto commit" --allow-empty
git pull
git push
nohup uv run main.py &
