#!/usr/bin/env bash
# Human-in-the-loop reproduction loop.
#
# Copy this file, edit the steps between the markers, and run it. The agent runs
# the script; the person follows the prompts in their own terminal.
#
#   step "<instruction>"        show an instruction, wait for Enter
#   capture VAR "<question>"    ask a question, store the answer in VAR
#   report                      print every captured VAR as a KEY=VALUE line
#
# The agent parses the report. Capture observations only. Never ask for a
# password or token: leave signing in to the person as a `step`, and redact
# anything sensitive before showing the output to anyone.

set -euo pipefail

captured_keys=()

step() {
  printf '\n>>> %s\n' "$1"
  read -r -p "    [Enter when done] " _
}

capture() {
  local var="$1" question="$2" answer
  printf '\n>>> %s\n' "$question"
  read -r -p "    > " answer
  printf -v "$var" '%s' "$answer"
  captured_keys+=("$var")
}

report() {
  local key
  printf '\n--- Captured ---\n'
  for key in "${captured_keys[@]}"; do
    printf '%s=%s\n' "$key" "${!key}"
  done
}

# --- edit below ---------------------------------------------------------

step "Open the app at http://localhost:3000 and sign in."
capture ERRORED "Click the Export button. Did it throw an error? (y/n)"
capture ERROR_MSG "Paste the error message, or 'none':"

# --- edit above ---------------------------------------------------------

report
