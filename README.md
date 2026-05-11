# Network Incident Data Analysis

## Overview
This repository contains a data analytics project inspired by real-world network operations and incident troubleshooting experience. The project analyzes simulated firewall, VPN, and network incident logs to identify issue categories, severity trends, recurring patterns, and operational insights.

## Objective
The objective of this project is to demonstrate how data science and analytics can be applied to network operations data. The analysis focuses on identifying frequent incident types, understanding severity distribution, detecting repeated issues, and creating insights that can support faster troubleshooting and better operational decision-making.

## Tools & Technologies
- Python
- Pandas
- NumPy
- Matplotlib
- Jupyter Notebook
- CSV Data Analysis
- Network Logs
- Incident Analysis
- Firewall and VPN Troubleshooting

## Business Problem
Network operations teams handle many types of incidents including VPN failures, firewall blocks, latency issues, packet loss, authentication failures, and application connectivity problems. Without structured analysis, it becomes difficult to identify recurring causes and high-impact issue categories.

This project converts incident records into a structured dataset and performs exploratory data analysis to summarize key trends.

## Dataset
The dataset is a simulated network incident log created for portfolio demonstration. It includes the following fields:

- Incident ID
- Date
- Device Type
- Issue Category
- Severity
- Resolution Time
- Status
- Root Cause
- Region
- Assigned Team

## Methodology
1. Loaded network incident log data using Pandas.
2. Cleaned and validated incident records.
3. Analyzed incident frequency by issue category.
4. Compared severity distribution across network issue types.
5. Calculated average resolution time by category.
6. Identified repeated root causes and operational bottlenecks.
7. Exported summary results for reporting.

## Key Insights
- VPN and firewall-related issues were among the most frequent incident categories.
- High-severity incidents had longer average resolution times.
- Authentication, configuration, and policy-related issues appeared as repeated root causes.
- Structured analysis can help network teams prioritize automation, monitoring, and preventive maintenance.

## Repository Structure
```text
network-incident-data-analysis/
├── README.md
├── requirements.txt
├── .gitignore
├── data/
│   └── network_incidents.csv
├── notebooks/
│   └── network_incident_analysis.ipynb
├── scripts/
│   └── network_incident_analysis.py
├── results/
│   ├── incident_category_summary.csv
│   ├── severity_summary.csv
│   └── resolution_time_summary.csv
├── images/
│   └── README.md
└── docs/
    ├── project_summary.md
    └── github_upload_checklist.md
```

## Resume Bullet Point
Analyzed simulated firewall, VPN, and network incident logs using Python and Pandas to identify recurring issue categories, severity patterns, resolution time trends, and operational insights for network troubleshooting.

## Future Improvements
- Add real-time log streaming using Kafka.
- Build an incident dashboard using Power BI or Streamlit.
- Apply anomaly detection on network events.
- Use machine learning to predict incident severity.
