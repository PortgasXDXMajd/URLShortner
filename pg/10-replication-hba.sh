#!/usr/bin/env bash
set -e
cat >> "$PGDATA/pg_hba.conf" <<'HBA'
host    replication     replicator      0.0.0.0/0      scram-sha-256
host    all             all             0.0.0.0/0      scram-sha-256
HBA
