-- PostgreSQL 15+ reporting queries for synthetic data/network_incidents.csv.
-- Run after sql/01_incident_schema.sql and a one-time CSV import into incident_events.
-- These three SELECT statements mirror scripts/network_incident_analysis.py.
-- They are read-only and do not modify the incident table.

-- Equivalent to results/incident_category_summary.csv.
SELECT
    issue_category,
    COUNT(*) AS incident_count,
    ROUND(AVG(resolution_time_minutes), 2) AS avg_resolution_time_minutes
FROM incident_events
GROUP BY issue_category
ORDER BY incident_count DESC, issue_category;

-- Equivalent to results/severity_summary.csv.
SELECT
    severity,
    COUNT(*) AS incident_count,
    ROUND(AVG(resolution_time_minutes), 2) AS avg_resolution_time_minutes
FROM incident_events
GROUP BY severity
ORDER BY severity;

-- Equivalent to results/resolution_time_summary.csv.
SELECT
    issue_category,
    severity,
    COUNT(*) AS incident_count,
    ROUND(AVG(resolution_time_minutes), 2) AS avg_resolution_time_minutes
FROM incident_events
GROUP BY issue_category, severity
ORDER BY issue_category, severity;
