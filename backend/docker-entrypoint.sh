#!/bin/sh
set -e

# Run idempotent schema sync before workers boot.
# This repairs legacy Postgres databases created before
# user.email_digest_enabled / email_alerts_enabled / calendar_token existed.
# Failure here must not block boot (create_app() retries the same sync in-process),
# but success prevents the UndefinedColumn 500 on /api/auth/login and /api/auth/register.
python -c "from app import create_app, sync_database_schema; app = create_app(); ok = sync_database_schema(app); print('entrypoint db-sync ok' if ok else 'entrypoint db-sync warnings')" || echo "entrypoint db-sync skipped (in-process sync will retry)"

exec "$@"
