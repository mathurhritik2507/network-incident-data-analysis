"""
Network Incident Data Analysis

This script analyzes simulated firewall, VPN, and network incident logs.
It creates summary tables for issue categories, severity levels, and resolution times.
"""

from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "network_incidents.csv"
RESULTS_DIR = ROOT / "results"
IMAGES_DIR = ROOT / "images"

RESULTS_DIR.mkdir(exist_ok=True)
IMAGES_DIR.mkdir(exist_ok=True)

def main():
    df = pd.read_csv(DATA_PATH)
    df["date"] = pd.to_datetime(df["date"])

    print("Dataset shape:", df.shape)
    print("\nFirst five records:")
    print(df.head())

    category_summary = (
        df.groupby("issue_category")
        .agg(
            incident_count=("incident_id", "count"),
            avg_resolution_time_minutes=("resolution_time_minutes", "mean"),
        )
        .round(2)
        .reset_index()
        .sort_values("incident_count", ascending=False)
    )
    category_summary.to_csv(RESULTS_DIR / "incident_category_summary.csv", index=False)

    severity_summary = (
        df.groupby("severity")
        .agg(
            incident_count=("incident_id", "count"),
            avg_resolution_time_minutes=("resolution_time_minutes", "mean"),
        )
        .round(2)
        .reset_index()
    )
    severity_summary.to_csv(RESULTS_DIR / "severity_summary.csv", index=False)

    resolution_summary = (
        df.groupby(["issue_category", "severity"])
        .agg(
            incident_count=("incident_id", "count"),
            avg_resolution_time_minutes=("resolution_time_minutes", "mean"),
        )
        .round(2)
        .reset_index()
    )
    resolution_summary.to_csv(RESULTS_DIR / "resolution_time_summary.csv", index=False)

    plt.figure(figsize=(10, 5))
    category_summary.plot(x="issue_category", y="incident_count", kind="bar", legend=False)
    plt.title("Incident Count by Issue Category")
    plt.xlabel("Issue Category")
    plt.ylabel("Incident Count")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.savefig(IMAGES_DIR / "incident_count_by_category.png")

    plt.figure(figsize=(8, 5))
    severity_summary.plot(x="severity", y="avg_resolution_time_minutes", kind="bar", legend=False)
    plt.title("Average Resolution Time by Severity")
    plt.xlabel("Severity")
    plt.ylabel("Average Resolution Time Minutes")
    plt.tight_layout()
    plt.savefig(IMAGES_DIR / "avg_resolution_time_by_severity.png")

    print("\nCategory Summary:")
    print(category_summary)

    print("\nSeverity Summary:")
    print(severity_summary)

if __name__ == "__main__":
    main()
