# Daily Civic Intelligence Refinement Algorithm

This document explains the logic behind the "Self-Improving AI Infrastructure" implemented in VishwaGuru.

## Overview

The system runs a daily scheduled job (`backend/scheduler/daily_refinement_job.py`) that analyzes civic issues from the last 24 hours to detect trends, optimize AI models, and generate a "Civic Intelligence Index".

## Key Components

### 1. Trend Detection (`backend/trend_analyzer.py`)
- **Keywords**: Uses `scikit-learn`'s `CountVectorizer` (or a fallback tokenizer) to extract top 10 keywords from issue descriptions.
- **Categories**: Calculates distribution of issue categories.
- **Geographic Clustering**: Uses DBSCAN (Density-Based Spatial Clustering of Applications with Noise) to identify hotspots where multiple issues are reported close together (default 100m radius).

### 2. Adaptive Weight Optimization (`backend/civic_intelligence.py`)
- **Goal**: Automatically adjust severity scoring rules based on manual corrections.
- **Logic**:
    - The system checks `EscalationAudit` logs for issues where the severity was manually upgraded (e.g., from "Low" to "Critical").
    - If a specific category (e.g., "Pothole") is frequently upgraded (> 3 times in 24h), the system automatically adds the category name to the **High Severity Keywords** list in `data/modelWeights.json`.
    - This ensures future reports of "Pothole" are flagged as High Severity immediately.

### 3. Duplicate Pattern Learning (`backend/civic_intelligence.py`)
- **Goal**: Tune the spatial deduplication radius to balance between missing duplicates and false positives.
- **Logic**:
    - It analyzes the density of geographic clusters found by the Trend Analyzer.
    - **High Density**: If many clusters with >1 issue are found, it implies users are reporting the same problems but they are not being caught as duplicates during submission. The system **increases** the duplicate search radius (e.g., from 50m to 55m).
    - **Low Density**: If no clusters are found, the system slightly **decreases** the radius to be more precise.
    - The updated radius is stored in `data/modelWeights.json` and used by the submission API.

### 4. Civic Intelligence Index (`backend/civic_intelligence.py`)
A daily score (0-100) reflecting the health and efficiency of the civic response system.

**Formula:**
`Index = (Activity * 0.2) + (Resolution Rate * 0.4) + (AI Accuracy * 0.4)`

- **Activity**: Normalized score based on volume of reports (target: 50 issues/day).
- **Resolution Rate**: Percentage of issues resolved within 24 hours.
- **AI Accuracy**: 100 minus the percentage of issues that required manual severity escalation.

## Data Persistence

- **Weights**: Stored in `data/modelWeights.json`. This file is hot-loaded by the `PriorityEngine` and `Issue Router`.
- **Snapshots**: Daily analysis results are saved in `data/dailySnapshots/YYYY-MM-DD.json` for historical tracking and auditability.

## Running the Job

To run the refinement process manually:

```bash
python backend/scheduler/daily_refinement_job.py
```

To schedule it (e.g., via cron):

```bash
0 0 * * * cd /path/to/repo && python backend/scheduler/daily_refinement_job.py >> /var/log/civic_refinement.log 2>&1
```
