-- Read-only PostgreSQL view parity check for simulated incidents.
-- Run after schema creation and CSV import with psql -v ON_ERROR_STOP=1.
DO $$
BEGIN
    IF EXISTS (
        WITH expected AS (
            SELECT "date"::date AS incident_date, issue_category, severity,
                   COUNT(*) AS incident_count,
                   ROUND(AVG(resolution_time_minutes), 2) AS avg_resolution_time_minutes
            FROM incident_events
            GROUP BY "date"::date, issue_category, severity
        ), differences AS (
            (SELECT * FROM expected EXCEPT ALL
             SELECT incident_date, issue_category, severity, incident_count,
                    avg_resolution_time_minutes FROM incident_daily_summary)
            UNION ALL
            (SELECT incident_date, issue_category, severity, incident_count,
                    avg_resolution_time_minutes FROM incident_daily_summary
             EXCEPT ALL SELECT * FROM expected)
        )
        SELECT 1 FROM differences
    ) THEN
        RAISE EXCEPTION 'Daily view differs from base event aggregation';
    END IF;
    RAISE NOTICE 'Daily view group parity passed';
END
$$;
