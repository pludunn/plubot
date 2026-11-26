#!/bin/bash
set -euo pipefail

cd /home/pludunn/plubot
nohup uv run main.py &
