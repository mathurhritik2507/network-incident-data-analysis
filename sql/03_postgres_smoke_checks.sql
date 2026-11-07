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
