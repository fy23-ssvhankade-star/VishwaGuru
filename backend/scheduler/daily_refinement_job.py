import sys
import os
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Ensure project root is in sys.path
# This script is at backend/scheduler/daily_refinement_job.py
# Root is ../../
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(script_dir))
sys.path.append(project_root)

# Now we can import from backend
try:
    from backend.database import SessionLocal
    from backend.civic_intelligence import civic_intelligence_engine
except ImportError as e:
    logger.error(f"Failed to import backend modules: {e}")
    sys.exit(1)

def run_job():
    """Runs the daily refinement job."""
    logger.info("Starting Daily Civic Intelligence Refinement Job")

    db = SessionLocal()
    try:
        snapshot = civic_intelligence_engine.refine_daily(db)

        index_score = snapshot.get("civic_intelligence_index", {}).get("score", "N/A")
        adjustments = snapshot.get("adaptive_actions", {})

        logger.info(f"Daily Refinement Completed Successfully.")
        logger.info(f"Civic Intelligence Index: {index_score}")
        logger.info(f"Weight Adjustments: {len(adjustments.get('weight_adjustments', []))}")
        logger.info(f"Radius Adjustments: {len(adjustments.get('radius_adjustments', []))}")

    except Exception as e:
        logger.error(f"Daily Refinement Job Failed: {e}", exc_info=True)
    finally:
        db.close()

if __name__ == "__main__":
    run_job()
