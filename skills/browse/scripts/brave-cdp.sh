#!/usr/bin/env bash
# Start, inspect, or stop the per-project Brave session used by the browse skill.
# Usage: brave-cdp.sh start|status|stop|port [--project <name>] [url]
set -euo pipefail

cmd="${1:-status}"
shift || true
project=""
url=""
while [ $# -gt 0 ]; do
  case "$1" in
    --project) project="$2"; shift 2 ;;
    *) url="$1"; shift ;;
  esac
done

if [ -z "$project" ]; then
  common="$(git rev-parse --path-format=absolute --git-common-dir 2>/dev/null || true)"
  if [ -n "$common" ]; then
    project="$(basename "$(dirname "$common")")"
  else
    project="$(basename "$PWD")"
  fi
fi
project="$(printf '%s' "$project" | tr -c 'A-Za-z0-9._-' '-')"

port=$(( 9223 + $(printf '%s' "$project" | cksum | cut -d' ' -f1) % 700 ))
profile="${COMPUTER_USER_PROFILES:-$HOME/.agents/browser-profiles}/$project"
endpoint="http://127.0.0.1:$port"

alive() { curl -fsS --max-time 1 "$endpoint/json/version" >/dev/null 2>&1; }

case "$cmd" in
  port)
    echo "$port"
    ;;
  status)
    if alive; then
      echo "running project=$project endpoint=$endpoint profile=$profile"
    else
      echo "stopped project=$project endpoint=$endpoint profile=$profile"
      exit 1
    fi
    ;;
  start)
    if alive; then
      echo "running project=$project endpoint=$endpoint profile=$profile (reused)"
      exit 0
    fi
    [ "$(uname)" = "Darwin" ] || { echo "browse drives Brave on macOS only" >&2; exit 2; }
    [ -d "/Applications/Brave Browser.app" ] || { echo "Brave Browser.app not found in /Applications" >&2; exit 2; }
    mkdir -p "$profile"
    args=(--user-data-dir="$profile" --remote-debugging-port="$port"
      --remote-allow-origins="$endpoint" --no-first-run --no-default-browser-check)
    [ -n "$url" ] && args+=("$url")
    open -na "Brave Browser" --args "${args[@]}"
    for _ in $(seq 1 50); do
      alive && { echo "running project=$project endpoint=$endpoint profile=$profile"; exit 0; }
      sleep 0.2
    done
    echo "Brave did not expose $endpoint within 10s" >&2
    exit 1
    ;;
  stop)
    pids="$(pgrep -f -- "--user-data-dir=$profile" || true)"
    [ -n "$pids" ] || { echo "not running project=$project"; exit 0; }
    # Signal only the browser process that owns this profile; Brave closes its helpers.
    main="$(pgrep -f -- "Brave Browser.app/Contents/MacOS/Brave Browser .*--user-data-dir=$profile" || true)"
    target="${main:-$pids}"
    # shellcheck disable=SC2086 # the pid list is word-split on purpose
    kill $target
    echo "stopped project=$project"
    ;;
  *)
    echo "usage: brave-cdp.sh start|status|stop|port [--project <name>] [url]" >&2
    exit 2
    ;;
esac
