-- PostgreSQL 15+; portfolio demonstration using synthetic incidents only.
-- The column names and order match data/network_incidents.csv for psql \copy.
-- Timestamps in the source have no timezone; do not infer UTC.

CREATE TABLE IF NOT EXISTS incident_events (
    incident_id TEXT PRIMARY KEY,
    "date" TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    device_type TEXT NOT NULL CHECK (btrim(device_type) <> ''),
    issue_category TEXT NOT NULL CHECK (btrim(issue_category) <> ''),
    severity TEXT NOT NULL CHECK (severity IN ('Low', 'Medium', 'High', 'Critical')),
    resolution_time_minutes INTEGER NOT NULL CHECK (resolution_time_minutes >= 0),
    status TEXT NOT NULL CHECK (status IN ('Resolved', 'Closed', 'Escalated')),
    root_cause TEXT NOT NULL CHECK (btrim(root_cause) <> ''),
    region TEXT NOT NULL CHECK (btrim(region) <> ''),
    assigned_team TEXT NOT NULL CHECK (btrim(assigned_team) <> '')
);

CREATE INDEX IF NOT EXISTS idx_incident_events_date ON incident_events ("date");

-- Reporting view: one row per incident day, category, and severity.
-- Resolution time is recorded in minutes in the synthetic source.
CREATE OR REPLACE VIEW incident_daily_summary AS
SELECT
    "date"::date AS incident_date,
    issue_category,
    severity,
    COUNT(*) AS incident_count,
    ROUND(AVG(resolution_time_minutes), 2) AS avg_resolution_time_minutes
FROM incident_events
GROUP BY "date"::date, issue_category, severity;
