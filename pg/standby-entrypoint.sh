#!/usr/bin/env bash
set -euo pipefail
PGDATA=/var/lib/postgresql/data

if [ ! -s "$PGDATA/PG_VERSION" ]; then
  echo "cloning from $PRIMARY_HOST as slot $SLOT_NAME ..."
  until pg_isready -h "$PRIMARY_HOST" -U replicator -q; do sleep 1; done
  rm -rf "$PGDATA"/*
  PGPASSWORD=replpass pg_basebackup \
      -h "$PRIMARY_HOST" -U replicator -D "$PGDATA" \
      -Fp -Xs -P -R -C -S "$SLOT_NAME"
  # label this standby so the primary can name it in synchronous_standby_names
  echo "primary_conninfo = 'host=$PRIMARY_HOST user=replicator password=replpass application_name=$SLOT_NAME'" \
      >> "$PGDATA/postgresql.auto.conf"
  chmod 0700 "$PGDATA"
fi
# forward compose `command` (e.g. postgres -c max_connections=...); default to plain postgres
if [ "$#" -eq 0 ]; then set -- postgres; fi
exec docker-entrypoint.sh "$@"