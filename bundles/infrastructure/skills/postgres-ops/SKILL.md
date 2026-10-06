---
name: postgres-ops
description: Operate a production Postgres database — backup strategy, point-in-time recovery, restore drills, connection pooling for serverless, and a disaster-recovery runbook. Use when asked to set up Postgres backups, plan disaster recovery, configure connection pooling, restore a database, or harden Postgres for production. Covers managed (RDS / Prisma Postgres) and self-managed instances.
disable-model-invocation: true
argument-hint: "[backup | restore | pooling | dr]"
compatibility: Requires psql / pg_dump / pg_restore for self-managed instances; provider CLI for managed.
allowed-tools: Bash(psql *) Bash(pg_dump *) Bash(pg_restore *) Bash(pg_basebackup *) Bash(createdb *) Bash(dropdb *)
metadata:
  version: "2.2.3"
  tags: "postgres, backup, disaster-recovery, pooling, database, infrastructure"
  author: Ship Shit Dev
when_to_use: "postgres backups, database backup strategy, point in time recovery, PITR, restore the database, connection pooling, PgBouncer, disaster recovery, DR runbook, harden postgres"
---

# Postgres Ops

Keep a production Postgres safe to lose and fast to serve: backups you have actually
restored, recovery you have actually tested, and pooling that survives serverless
connection storms. Restore and recovery operations can overwrite data — they run
behind explicit confirmation, against the right target.

## Contract

Inputs:

- A Postgres instance (managed or self-managed); mode `backup` / `restore` /
  `pooling` / `dr`.

Outputs:

- A backup/PITR plan or verification, a restore result, a pooling configuration, or a
  DR runbook.

Creates/Modifies:

- `restore` writes to a database. Never to production without explicit, named
  confirmation of the target. `backup`/`pooling`/`dr` produce config and plans.

External Side Effects:

- Reads DB metadata; `restore` mutates a database. Treat connection strings and dumps
  as secrets — never print credentials.

Confirmation Required:

- Before any restore, and again if the target is production.
- Before changing live pooling config that can drop connections.

Delegates To:

- `aws-infrastructure` for the storage/IAM around backups on AWS.
- `monitoring-setup` to alert on replication lag, connection saturation, and slow
  queries.

## Backup (`backup`)

Match the method to the hosting:

- **Managed (RDS, Prisma Postgres, etc.)** — enable automated snapshots + PITR in the
  provider; set retention to the business's tolerance. Verify it is on rather than
  assuming; snapshots you never checked are not a backup.
- **Self-managed** — logical backups for portability, physical + WAL for PITR:

  ```bash
  pg_dump --format=custom --file=db-$(date +%F).dump "$DATABASE_URL"   # logical
  # physical base backup + WAL archiving enables point-in-time recovery
  pg_basebackup -D /backup/base -Ftar -z -X stream
  ```

Two rules that decide whether a backup is real: store it **off the database host**
(a snapshot on the same disk dies with the disk), and set a retention that covers the
time to *notice* a problem, not just to react.

## Point-in-time recovery

PITR needs continuous WAL archiving (`archive_mode = on`, `archive_command` shipping
WAL off-host) on top of a base backup. Define and write down two numbers:

- **RPO** (how much data you can lose) → drives backup/WAL frequency.
- **RTO** (how long recovery may take) → drives whether a warm standby is needed.

Recovery replays WAL from a base backup up to a target time. The only proof it works
is a drill (below).

## Restore & verify (`restore`)

A backup is unproven until restored. Restore into a **scratch** database, never over
production, and verify:

```bash
scratch_db="restore_check_$(date +%s)"
trap 'dropdb --if-exists "$scratch_db"' EXIT
createdb "$scratch_db"
pg_restore --dbname="$scratch_db" --clean --if-exists db-YYYY-MM-DD.dump
psql "$scratch_db" -c "SELECT count(*) FROM <critical_table>;"   # sanity-check row counts
dropdb "$scratch_db"
trap - EXIT
```

Only restore to production on an explicit, named request, after confirming the target
connection string is the intended one. Schedule a **periodic restore drill** — an
untested backup is a guess.

## Connection pooling (`pooling`)

Serverless (Vercel functions) + Postgres = connection exhaustion: each concurrent
invocation opens a connection, and Postgres has a hard `max_connections`. Put a pooler
in front:

- **PgBouncer** (or the provider's pooler) in **transaction** mode for serverless.
- Point Prisma at the **pooled** port for the app; use the **direct** connection only
  for migrations (`directUrl` in Prisma).
- Size the pool to the DB's `max_connections` minus headroom for admin/migrations —
  not higher, or the pooler just moves the exhaustion.

## Disaster recovery (`dr`)

Produce a runbook someone can follow at 3am without this context:

1. **Detect** — the alert that fires (from `monitoring-setup`): replication lag,
   connection saturation, disk full, instance down.
2. **Assess** — data loss (last good backup/WAL) vs availability (standby present?).
3. **Recover** — promote a standby, or restore latest base + replay WAL to just before
   the incident.
4. **Verify** — row counts on critical tables, app reconnects, no partial writes.
5. **Post-mortem** — what to change so it does not recur (retention, alert threshold,
   standby).

State the current RPO/RTO honestly, and name the gap between them and the target.

## Anti-Patterns

- **Backups on the same host/disk as the database** — they die together. Off-host or
  it is not a backup.
- **Never restoring** — an untested backup is a guess; drill it on a schedule.
- **Restoring over production to "check"** — always a scratch database first.
- **No pooler in front of serverless** — connection storms exhaust `max_connections`
  and take the app down under load.
- **Printing connection strings or dump contents** — they are secrets.
