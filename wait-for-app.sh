#!/bin/sh
# wait-for-app.sh

set -e

host="$1"
shift
cmd="$@"

until curl -f "http://$host/health"; do
  >&2 echo "App is unavailable - sleeping"
  sleep 1
done

>&2 echo "App is up - executing command"
exec $cmd
