#!/usr/bin/env bash
set -euo pipefail

# Bootstrap a fresh Ubuntu VPS for this project.
# Usage (run on VPS):
#   bash bootstrap_vps.sh
#
# Optional env vars:
#   BOT_USER=youruser (default: current user)
#   BOT_DIR=/home/youruser/Bot (default: /home/$BOT_USER/Bot)
#   REPO_URL=https://github.com/s-dev-beep/bot.git (default)
#   DOCKER_IMAGE=mechul/real-estate-crawler:latest (default)
#   DOCKER_USER=mechul (for private Docker Hub image)
#   DOCKER_TOKEN=your_access_token (for private Docker Hub image)

BOT_USER="${BOT_USER:-$(whoami)}"
BOT_DIR="${BOT_DIR:-/home/${BOT_USER}/Bot}"
REPO_URL="${REPO_URL:-https://github.com/s-dev-beep/bot.git}"
DOCKER_IMAGE="${DOCKER_IMAGE:-mechul/real-estate-crawler:latest}"
DOCKER_USER="${DOCKER_USER:-}"
DOCKER_TOKEN="${DOCKER_TOKEN:-}"

sudo apt update
sudo apt install -y ca-certificates curl gnupg lsb-release git

# Docker install
sudo install -m 0755 -d /etc/apt/keyrings
if [[ ! -f /etc/apt/keyrings/docker.gpg ]]; then
  curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
fi
if [[ ! -f /etc/apt/sources.list.d/docker.list ]]; then
  echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo $VERSION_CODENAME) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
fi
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Docker permissions
sudo usermod -aG docker "${BOT_USER}"

# Project dirs
sudo mkdir -p "${BOT_DIR}" "${BOT_DIR}/config" "${BOT_DIR}/data" "${BOT_DIR}/logs" "${BOT_DIR}/cookies"
sudo chown -R "${BOT_USER}:${BOT_USER}" "${BOT_DIR}"

# Clone or update repo
if [[ ! -d "${BOT_DIR}/.git" ]]; then
  sudo -u "${BOT_USER}" git clone "${REPO_URL}" "${BOT_DIR}"
else
  sudo -u "${BOT_USER}" git -C "${BOT_DIR}" pull --ff-only
fi

# Ensure env file exists
if [[ -f "${BOT_DIR}/.env.example" && ! -f "${BOT_DIR}/.env" ]]; then
  sudo -u "${BOT_USER}" cp "${BOT_DIR}/.env.example" "${BOT_DIR}/.env"
  echo "Created ${BOT_DIR}/.env from .env.example (edit required)"
fi

# Docker Hub authentication (if credentials provided)
if [[ -n "${DOCKER_USER}" && -n "${DOCKER_TOKEN}" ]]; then
  echo "Logging in to Docker Hub..."
  echo "${DOCKER_TOKEN}" | sudo -u "${BOT_USER}" docker login -u "${DOCKER_USER}" --password-stdin
fi

# Pull image
sudo -u "${BOT_USER}" docker pull "${DOCKER_IMAGE}"

echo "Bootstrap complete. Log out/in or run: newgrp docker"
