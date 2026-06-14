import json
import os
import logging
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from sqlalchemy import func

from backend.models import Issue, Grievance, EscalationAudit, EscalationReason, SeverityLevel
from backend.trend_analyzer import trend_analyzer
from backend.adaptive_weights import adaptive_weights

logger = logging.getLogger(__name__)

class CivicIntelligenceEngine:
    """
    Orchestrates daily refinement of the civic intelligence system.
    analyzes trends, optimizes weights, and calculates the daily index.
    """
    # Resolve absolute path to data directory relative to this file
    _BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
    _ROOT_DIR = os.path.dirname(_BACKEND_DIR)
    SNAPSHOT_DIR = os.path.join(_ROOT_DIR, "data", "dailySnapshots")

    def __init__(self):
        os.makedirs(self.SNAPSHOT_DIR, exist_ok=True)

    def refine_daily(self, db: Session) -> Dict[str, Any]:
        """
        Runs the daily refinement process.
        Returns the generated snapshot data.
        """
        logger.info("Starting Daily Civic Intelligence Refinement...")

        now = datetime.now(timezone.utc)
        last_24h = now - timedelta(hours=24)

        # 1. Fetch Data
        recent_issues = db.query(Issue).filter(Issue.created_at >= last_24h).all()

        # 2. Trend Analysis
        trend_stats = trend_analyzer.analyze(recent_issues)

        # 3. Adaptive Weight Optimization
        weight_adjustments = self._optimize_weights(db, last_24h)

        # 4. Duplicate Pattern Learning
        radius_adjustments = self._optimize_duplicate_detection(trend_stats)

        # 5. Civic Intelligence Index
        index_data = self._calculate_index(db, last_24h, trend_stats)

        # 6. Generate Snapshot
        snapshot = {
            "date": now.isoformat(),
            "timestamp": now.timestamp(),
            "stats": {
                "total_issues_24h": len(recent_issues),
                "top_keywords": trend_stats["top_keywords"][:10],
                "category_spikes": trend_stats["category_distribution"],
                "geographic_clusters": len(trend_stats["geographic_clusters"])
            },
            "civic_intelligence_index": index_data,
            "adaptive_actions": {
                "weight_adjustments": weight_adjustments,
                "radius_adjustments": radius_adjustments
            },
            "system_state": {
                "current_weights_version": "v1", # Placeholder
            }
        }

        # 7. Save Snapshot
        filename = f"{now.strftime('%Y-%m-%d')}.json"
        filepath = os.path.join(self.SNAPSHOT_DIR, filename)
        try:
            with open(filepath, 'w') as f:
                json.dump(snapshot, f, indent=2)
            logger.info(f"Daily snapshot saved to {filepath}")
        except Exception as e:
            logger.error(f"Failed to save snapshot: {e}")

        return snapshot

    def _optimize_weights(self, db: Session, since: datetime) -> List[str]:
        """
        Analyzes escalation audits to adjust severity weights.
        """
        adjustments = []

        # Find manual severity upgrades in the last 24h
        upgrades = db.query(EscalationAudit).join(Grievance).filter(
            EscalationAudit.timestamp >= since,
            EscalationAudit.reason == EscalationReason.SEVERITY_UPGRADE
        ).all()

        if not upgrades:
            return ["No manual severity upgrades detected."]

        # Group by category
        category_upgrades = {}
        for audit in upgrades:
            # Check target severity (not explicitly stored in audit, but we can infer or use current)
            # Assuming if upgraded, it implies it was underestimated.
            # We need the category.
            cat = audit.grievance.category
            category_upgrades[cat] = category_upgrades.get(cat, 0) + 1

        # Apply adjustments
        current_weights = adaptive_weights.get_weights()
        severity_keywords = current_weights.get("severity_keywords", {})

        updated = False

        for category, count in category_upgrades.items():
            # If a category is frequently upgraded (> 3 times), treat its name as a high severity keyword
            if count >= 3:
                target_level = "high" # Default target for upgrades

                # Check if already in list
                if category.lower() not in severity_keywords.get(target_level, []):
                    # Add category name to high severity keywords
                    if target_level not in severity_keywords:
                        severity_keywords[target_level] = []

                    severity_keywords[target_level].append(category.lower())
                    adjustments.append(f"Added '{category.lower()}' to {target_level} severity keywords due to {count} upgrades.")
                    updated = True

        if updated:
            adaptive_weights.update_weights({"severity_keywords": severity_keywords})

        return adjustments

    def _optimize_duplicate_detection(self, trend_stats: Dict[str, Any]) -> List[str]:
        """
        Adjusts duplicate detection radius based on clustering density.
        """
        adjustments = []
        clusters = trend_stats.get("geographic_clusters", [])

        # Count "dense" clusters (more than 1 issue implies potential duplicate or hotspot)
        dense_clusters = [c for c in clusters if c["size"] > 1]

        current_radius = adaptive_weights.get_duplicate_search_radius()
        new_radius = current_radius

        # Logic:
        # If we see many dense clusters, it means people are reporting same things and they are NOT being blocked/linked.
        # This implies our radius might be too small to catch them as duplicates during submission.
        # So we should INCREASE radius.

        if len(dense_clusters) > 5:
            new_radius = min(current_radius + 5.0, 100.0) # Cap at 100m
            if new_radius > current_radius:
                adjustments.append(f"Increased duplicate search radius from {current_radius}m to {new_radius}m due to high clustering.")
        elif len(dense_clusters) == 0 and current_radius > 30.0:
            # If no clusters found, maybe we can tighten it back down (optional)
            new_radius = max(current_radius - 1.0, 30.0)
            if new_radius < current_radius:
                adjustments.append(f"Decreased duplicate search radius from {current_radius}m to {new_radius}m due to sparse data.")

        if new_radius != current_radius:
            adaptive_weights.update_weights({"duplicate_search_radius": new_radius})

        return adjustments

    def _calculate_index(self, db: Session, since: datetime, trend_stats: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculates the daily Civic Intelligence Index.
        """
        # 1. Activity Score (Normalization base: 100 issues/day = 100 points)
        total_issues = trend_stats.get("total_issues", 0)
        activity_score = min((total_issues / 50.0) * 100, 100) # 50 issues is "full" activity for MVP

        # 2. Resolution Rate (last 24h)
        # Count resolved issues in last 24h
        resolved_count = db.query(Issue).filter(
            Issue.resolved_at >= since
        ).count()

        resolution_rate = 0
        if total_issues > 0:
            # Note: This is simplified. Ideally should compare resolved vs total open pool,
            # but for daily "velocity", resolved/new is a proxy.
            resolution_rate = min((resolved_count / total_issues) * 100, 100)

        # 3. Severity Accuracy
        # If many upgrades, accuracy is low.
        upgrades_count = db.query(EscalationAudit).filter(
            EscalationAudit.timestamp >= since,
            EscalationAudit.reason == EscalationReason.SEVERITY_UPGRADE
        ).count()

        accuracy_score = 100
        if total_issues > 0:
            error_rate = (upgrades_count / total_issues)
            accuracy_score = max(0, 100 - (error_rate * 100)) # e.g. 10% error -> 90 score

        # Weighted Average
        # Activity: 20%, Resolution: 40%, Accuracy: 40%
        index_value = (activity_score * 0.2) + (resolution_rate * 0.4) + (accuracy_score * 0.4)

        return {
            "score": round(index_value, 1),
            "components": {
                "activity": round(activity_score, 1),
                "resolution_velocity": round(resolution_rate, 1),
                "ai_accuracy": round(accuracy_score, 1)
            },
            "top_emerging_concern": trend_stats["top_keywords"][0][0] if trend_stats["top_keywords"] else "None",
            "highest_severity_region": "Ward 1" # Placeholder, implies geo-analysis mapped to wards
        }

civic_intelligence_engine = CivicIntelligenceEngine()
