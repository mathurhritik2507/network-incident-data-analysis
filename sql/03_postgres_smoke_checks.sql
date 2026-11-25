-- Read-only PostgreSQL smoke checks for the checked-in 150-row synthetic CSV.
-- Run after sql/01_incident_schema.sql and the one-time import.
-- A false value means investigate before using reporting outputs.
-- This file does not modify tables or require extensions.
WITH source_counts AS (
    SELECT COUNT(*) AS total_rows,
           COUNT(DISTINCT incident_id) AS distinct_ids,
           COALESCE(SUM(resolution_time_minutes), 0) AS total_resolution_minutes
    FROM incident_events
), daily_counts AS (
    SELECT COALESCE(SUM(incident_count), 0) AS grouped_rows
    FROM incident_daily_summary
), daily_minutes AS (
    -- Recompute exact totals from base events, avoiding rounding of view averages.
    SELECT COALESCE(SUM(resolution_time_minutes), 0) AS grouped_minutes
    FROM (
        SELECT SUM(resolution_time_minutes) AS resolution_time_minutes
        FROM incident_events
        GROUP BY "date"::date, issue_category, severity
    ) AS grouped
)
SELECT source_counts.total_rows = 150 AS expected_fixture_rows,
       source_counts.distinct_ids = source_counts.total_rows AS unique_incident_ids,
       daily_counts.grouped_rows = source_counts.total_rows AS daily_view_preserves_rows,
       daily_minutes.grouped_minutes = source_counts.total_resolution_minutes AS daily_groups_preserve_minutes
FROM source_counts CROSS JOIN daily_counts CROSS JOIN daily_minutes;

-- Fail psql with a nonzero exit status (when ON_ERROR_STOP=1) if any
-- fixture invariant is violated. The SELECT above is human-readable only.
DO $$
DECLARE
    source_rows bigint;
    unique_ids bigint;
    view_rows bigint;
    source_minutes bigint;
    grouped_minutes bigint;
BEGIN
    SELECT COUNT(*), COUNT(DISTINCT incident_id),
           COALESCE(SUM(resolution_time_minutes), 0)
      INTO source_rows, unique_ids, source_minutes
      FROM incident_events;

    SELECT COALESCE(SUM(incident_count), 0)
      INTO view_rows
      FROM incident_daily_summary;

    SELECT COALESCE(SUM(group_minutes), 0)
      INTO grouped_minutes
      FROM (
          SELECT SUM(resolution_time_minutes) AS group_minutes
          FROM incident_events
          GROUP BY "date"::date, issue_category, severity
      ) grouped;

    IF source_rows <> 150 OR unique_ids <> source_rows
       OR view_rows <> source_rows OR grouped_minutes <> source_minutes THEN
        RAISE EXCEPTION 'Synthetic fixture smoke checks failed (rows %, unique %, daily %, source minutes %, grouped minutes %)',
            source_rows, unique_ids, view_rows, source_minutes, grouped_minutes;
    END IF;
    RAISE NOTICE 'All four synthetic fixture smoke checks passed';
END
$$;
