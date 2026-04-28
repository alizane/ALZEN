#!/bin/bash
# ALZEN — Environment Loader
# Source: source scripts/load-env.sh [base|paperclip|hermes|all]
MODE="${1:-base}"
PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
case "$MODE" in
  base)     [ -f "$PROJECT_DIR/.env" ] && set -a && source "$PROJECT_DIR/.env" && set +a ;;
  paperclip) [ -f "$PROJECT_DIR/.env.paperclip" ] && set -a && source "$PROJECT_DIR/.env.paperclip" && set +a ;;
  hermes)   [ -f "$PROJECT_DIR/.env.hermes" ] && set -a && source "$PROJECT_DIR/.env.hermes" && set +a ;;
  all)      source "$0" base; source "$0" paperclip; source "$0" hermes ;;
  *) echo "Usage: source $0 {base|paperclip|hermes|all}" ;;
esac
