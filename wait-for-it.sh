#!/usr/bin/env bash
# wait-for-it.sh
# Используйте этот скрипт для ожидания доступности указанного TCP-хоста и порта.
# Источник: https://github.com/vishnubob/wait-for-it
# MIT License

set -e

TIMEOUT=15
QUIET=0

echoerr() {
  if [ "$QUIET" -ne 1 ]; then echo "$@" 1>&2; fi
}

usage() {
  echo "Usage: $0 host:port [-t timeout] [-- command args]"
  exit 1
}

wait_for() {
  local start_ts=$(date +%s)
  while :
  do
    if nc -z "$HOST" "$PORT" >/dev/null 2>&1; then
      break
    fi
    local now_ts=$(date +%s)
    if [ $((now_ts - start_ts)) -ge $TIMEOUT ]; then
      echoerr "Operation timed out after waiting $TIMEOUT seconds for $HOST:$PORT"
      exit 1
    fi
    sleep 1
  done
}

if [ "$#" -lt 1 ]; then
  usage
fi

HOST=$(echo "$1" | cut -d':' -f1)
PORT=$(echo "$1" | cut -d':' -f2)
shift

while [ $# -gt 0 ]; do
  case "$1" in
    -t|--timeout)
      TIMEOUT="$2"
      shift 2
      ;;
    --)
      shift
      break
      ;;
    *)
      break
      ;;
  esac
done

wait_for
exec "$@"
