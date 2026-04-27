@'
#!/bin/bash
# Usage: source scripts/load-env.sh [paperclip|hermes|base]
ENV_TARGET=${1:-base}
set -a
[ -f .env ] && source .env
[ -f .env.$ENV_TARGET ] && source .env.$ENV_TARGET
set +a
echo "Environment loaded: $ENV_TARGET"
