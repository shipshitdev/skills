---
name: incremental-fetch
description: Builds resilient data ingestion pipelines from paginated APIs using two watermarks so progress is never lost. Not for one-shot calls, websockets, or file downloads.
metadata:
  version: "2.2.2"
  tags: "data-ingestion, api, pagination"
when_to_use: "backfill older data, resume the download, pull tweets, sync from X"
---

# Incremental Fetch

Build data pipelines that never lose progress and never re-fetch existing data.

## The Two Watermarks Pattern

Track TWO cursors to support both forward and backward fetching:

| Watermark | Purpose | API Parameter |
|-----------|---------|---------------|
| `newest_id` | Fetch new data since last run | `since_id` |
| `oldest_id` | Backfill older data | `until_id` |

A single watermark only fetches forward. Two watermarks enable:

- Regular runs: fetch NEW data (since `newest_id`)
- Backfill runs: fetch OLD data (until `oldest_id`)
- No overlap, no gaps

## Critical: Data vs Watermark Saving

These are different operations with different timing:

| What | When to Save | Why |
|------|--------------|-----|
| **Data records** | After EACH page | Resilience: interrupted on page 47? Keep 46 pages |
| **Watermarks** | ONCE at end of run | Correctness: only commit progress after full success |

```
fetch page 1 → save records → fetch page 2 → save records → ... → update watermarks
```

## Workflow Decision Tree

```
First run (no watermarks)?
├── YES → Full fetch (no since_id, no until_id)
└── NO → Backfill flag set?
    ├── YES → Backfill mode (until_id = oldest_id)
    └── NO → Update mode (since_id = newest_id)
```

## Implementation Checklist

1. **Database**: Create ingestion_state table (see patterns.md)
2. **Fetch loop**: Insert records immediately after each API page
3. **Watermark tracking**: Track newest/oldest IDs seen in this run
4. **Watermark update**: Save watermarks ONCE at end of successful run
5. **Retry**: Exponential backoff with jitter
6. **Rate limits**: Wait for reset or skip and record for next run

## Pagination Types

This pattern works best with **ID-based pagination** (numeric IDs that can be compared). For other pagination types:

| Type | Adaptation |
|------|------------|
| **Cursor/token** | Store cursor string instead of ID; can't compare numerically |
| **Timestamp** | Use `last_timestamp` column; compare as dates |
| **Offset/limit** | Store page number; resume from last saved page |

See [references/patterns.md](references/patterns.md) for schemas and code examples.

## Gotchas

- **Save watermarks only after full success.** If the process crashes mid-run, unsaved watermarks mean the next run re-fetches and deduplicates from scratch — no data loss, but potentially slow. Saving watermarks mid-run causes permanent gaps.
- **Newest ID may not equal the highest numeric ID.** Some APIs return IDs that are not monotonically increasing (e.g., snowflake IDs with clock drift). Always compare using the API's own ordering guarantees, not numeric comparison.
- **Backfill mode must not overwrite the `newest_id`.** A backfill run extends history backward; it should update only `oldest_id`. Overwriting `newest_id` during backfill causes duplicate fetches on the next forward update run.
- **Rate-limit headers vary by API.** Twitter uses `x-rate-limit-reset`; others use `Retry-After`. Check the specific API's response headers before implementing wait logic.
