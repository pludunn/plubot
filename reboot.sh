#!/bin/bash
set -euo pipefail

cd /home/pludunn/plubot
git pull
nohup uv run main.py &
