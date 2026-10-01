#!/usr/bin/env bash
# Usage: ./deploy.sh deploy@<vm ip>
# Pulls the latest main on the server and restarts the stack.
set -euo pipefail

HOST=${1:?usage: ./deploy.sh user@host}
REPO=https://github.com/romaniuum/leadflow.git

ssh "$HOST" bash -s <<EOF
set -euo pipefail
[ -d leadflow ] || git clone $REPO leadflow
cd leadflow
git pull --ff-only
if [ ! -f .env ]; then
  echo "no .env on the server, create it from .env.example first"
  exit 1
fi
docker compose up -d --build
docker compose ps
EOF
