#!/usr/bin/env bash
set -euo pipefail

BOT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_BIN="${PYTHON_BIN:-python3}"

# Optional runtime configuration (override via environment variables)
URLS_FILE="${URLS_FILE:-$BOT_ROOT/examples/sample_urls_sahibinden.txt}"
CRAWL_MODE="${CRAWL_MODE:-safe_run}"
CRAWL_CONFIG="${CRAWL_CONFIG:-}"
CRAWL_LIMIT="${CRAWL_LIMIT:-}"
REPORT_PATH="${REPORT_PATH:-$BOT_ROOT/reports/crawl_report_$(date +%Y%m%d_%H%M%S).json}"
RUN_CRAWL="${RUN_CRAWL:-1}"
RUN_WARMUP="${RUN_WARMUP:-1}"
RUN_HEALTHCHECK="${RUN_HEALTHCHECK:-1}"

# Email notification (optional). Set EMAIL_NOTIFY=1 and SMTP_* env vars.
EMAIL_NOTIFY="${EMAIL_NOTIFY:-0}"
SMTP_HOST="${SMTP_HOST:-}"
SMTP_PORT="${SMTP_PORT:-587}"
SMTP_USER="${SMTP_USER:-}"
SMTP_PASS="${SMTP_PASS:-}"
SMTP_TO="${SMTP_TO:-}"
SMTP_FROM="${SMTP_FROM:-${SMTP_USER}}"
EMAIL_SUBJECT_PREFIX="${EMAIL_SUBJECT_PREFIX:-[Bot VPS]}"

info() { echo -e "\n[setup] $*"; }

send_email() {
  local subject="$1"
  local body="$2"

  if [[ "$EMAIL_NOTIFY" != "1" ]]; then
    return 0
  fi

  if [[ -z "$SMTP_HOST" || -z "$SMTP_TO" || -z "$SMTP_FROM" ]]; then
    echo "[notify] Email not configured (SMTP_HOST/SMTP_TO/SMTP_FROM missing)."
    return 0
  fi

  "$BOT_ROOT/.venv/bin/python" - <<'PY'
import os
import smtplib
import ssl
from email.message import EmailMessage

subject = os.environ["SUBJECT"]
body = os.environ["BODY"]
smtp_host = os.environ["SMTP_HOST"]
smtp_port = int(os.environ.get("SMTP_PORT", "587"))
smtp_user = os.environ.get("SMTP_USER")
smtp_pass = os.environ.get("SMTP_PASS")
smtp_to = os.environ["SMTP_TO"]
smtp_from = os.environ["SMTP_FROM"]

msg = EmailMessage()
msg["Subject"] = subject
msg["From"] = smtp_from
msg["To"] = smtp_to
msg.set_content(body)

context = ssl.create_default_context()
with smtplib.SMTP(smtp_host, smtp_port, timeout=30) as server:
    server.starttls(context=context)
    if smtp_user and smtp_pass:
        server.login(smtp_user, smtp_pass)
    server.send_message(msg)
PY
}

on_error() {
  local exit_code="$1"
  local msg="Setup failed with exit code ${exit_code} on $(hostname) at $(date)."
  send_email "${EMAIL_SUBJECT_PREFIX} Setup failed" "$msg"
  exit "$exit_code"
}

trap 'on_error $?' ERR INT TERM

info "Checking Python version (>=3.11 required)"
"$PYTHON_BIN" - <<'PY'
import sys
major, minor = sys.version_info[:2]
if (major, minor) < (3, 11):
    raise SystemExit(f"Python {major}.{minor} detected. Please install Python 3.11+ and re-run.")
print(f"Python {major}.{minor} OK")
PY

info "Installing OS packages (Playwright deps + XFCE + XRDP + Xvfb)"
sudo apt-get update -y
sudo apt-get install -y \
  ca-certificates curl gnupg \
  python3-venv \
  xrdp xfce4 xfce4-goodies \
  dbus-x11 xauth x11-xserver-utils \
  xvfb

info "Enabling XRDP"
echo "xfce4-session" > "$HOME/.xsession"
sudo systemctl enable --now xrdp

info "Creating venv and installing project dependencies"
cd "$BOT_ROOT"
if [[ ! -d ".venv" ]]; then
  "$PYTHON_BIN" -m venv .venv
fi
"$BOT_ROOT/.venv/bin/pip" install -e "$BOT_ROOT"

info "Installing Playwright system dependencies (chromium)"
"$BOT_ROOT/.venv/bin/python" -m playwright install-deps chromium

info "Installing Playwright Chromium browser"
"$BOT_ROOT/.venv/bin/python" -m playwright install chromium

info "Verifying Playwright browser install"
"$BOT_ROOT/.venv/bin/python" -m playwright install --check

run_with_display() {
  local script="$1"
  if [[ -n "${DISPLAY:-}" ]]; then
    "$BOT_ROOT/.venv/bin/python" "$script"
  else
    echo "[setup] No DISPLAY detected. Using Xvfb (no visible UI)."
    xvfb-run -a "$BOT_ROOT/.venv/bin/python" "$script"
  fi
}

if [[ "$RUN_WARMUP" == "1" ]]; then
  info "Starting Playwright warm-up (manual CAPTCHA may be required)"
  run_with_display "$BOT_ROOT/save_playwright_storage.py"
fi

if [[ "$RUN_HEALTHCHECK" == "1" ]]; then
  info "Running Playwright storage health check"
  set +e
  run_with_display "$BOT_ROOT/test_playwright_reuse.py"
  health_status=$?
  set -e

  if [[ "$health_status" -ne 0 ]]; then
    send_email "${EMAIL_SUBJECT_PREFIX} Health check failed" \
      "Health check failed with exit code ${health_status} on $(hostname) at $(date)."
    echo "[setup] Health check failed (exit ${health_status}). Not starting crawl."
    exit "$health_status"
  fi
fi

if [[ "$RUN_CRAWL" == "1" ]]; then
  if [[ ! -f "$URLS_FILE" ]]; then
    echo "[setup] URL file not found: $URLS_FILE"
    send_email "${EMAIL_SUBJECT_PREFIX} Crawl aborted" "URL file not found: $URLS_FILE"
    exit 1
  fi

  mkdir -p "$(dirname "$REPORT_PATH")"

  info "Starting crawl"
  crawl_cmd=("$BOT_ROOT/.venv/bin/python" -m src.cli.main crawl "$URLS_FILE" --mode "$CRAWL_MODE")
  if [[ -n "$CRAWL_CONFIG" ]]; then
    crawl_cmd+=(--config "$CRAWL_CONFIG")
  fi
  if [[ -n "$CRAWL_LIMIT" ]]; then
    crawl_cmd+=(--limit "$CRAWL_LIMIT")
  fi
  if [[ -n "$REPORT_PATH" ]]; then
    crawl_cmd+=(--report "$REPORT_PATH")
  fi

  set +e
  "${crawl_cmd[@]}"
  crawl_status=$?
  set -e

  if [[ "$crawl_status" -ne 0 ]]; then
    send_email "${EMAIL_SUBJECT_PREFIX} Crawl failed" \
      "Crawl failed with exit code ${crawl_status} on $(hostname) at $(date).\nReport: $REPORT_PATH"
    exit "$crawl_status"
  fi
fi

info "All steps completed successfully."
