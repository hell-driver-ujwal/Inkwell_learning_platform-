#!/usr/bin/env bash
# Start only this project's loopback-only development cluster.
set -euo pipefail
project_root="$(cd "$(dirname "$0")/.." && pwd)"
cluster_directory="$project_root/.postgres"
export PGHOST=127.0.0.1
export PGPORT="${PGPORT:-55439}"
if [[ ! -f "$cluster_directory/PG_VERSION" ]]; then
    initdb -D "$cluster_directory" -A trust --no-locale -E UTF8
fi
if ! pg_ctl -D "$cluster_directory" status >/dev/null 2>&1; then
    pg_ctl -D "$cluster_directory" -l "$cluster_directory/server.log" -o "-p $PGPORT -h 127.0.0.1" start
fi
if [[ "$(psql -d postgres -tAc "SELECT 1 FROM pg_database WHERE datname='inkwell'")" != "1" ]]; then
    createdb inkwell
fi
printf 'PostgreSQL ready. Export PGHOST=127.0.0.1 PGPORT=%s PGDATABASE=inkwell before Django commands.\n' "$PGPORT"
