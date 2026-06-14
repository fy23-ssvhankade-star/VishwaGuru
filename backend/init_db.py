import sys
import os
from pathlib import Path

# Add project root to path
current_file = Path(__file__).resolve()
backend_dir = current_file.parent
repo_root = backend_dir.parent
sys.path.insert(0, str(repo_root))

from sqlalchemy import text
import logging
from backend.database import engine, Base
from backend.models import *

logger = logging.getLogger(__name__)

def init_db():
    print("Creating tables...")
    Base.metadata.create_all(bind=engine)
    print("Tables created.")

def migrate_db():
    """
    Perform database migrations.
    Optimized: Uses CREATE INDEX IF NOT EXISTS and handles transactional safety for PostgreSQL.
    """
    try:
        # Use a new connection for each major step to avoid transaction aborts on PostgreSQL
        def run_migration_step(query_text, description):
            try:
                with engine.begin() as conn:
                    conn.execute(text(query_text))
                logger.info(f"Migration: {description}")
            except Exception as e:
                # Column/Index might already exist, ignore error but log it at debug level
                logger.debug(f"Migration step skipped ({description}): {e}")

        # Column additions (PostgreSQL doesn't support IF NOT EXISTS for columns in all versions,
        # so we rely on try/except with engine.begin() for isolation)
        run_migration_step("ALTER TABLE issues ADD COLUMN upvotes INTEGER DEFAULT 0", "Added upvotes to issues")
        run_migration_step("ALTER TABLE issues ADD COLUMN latitude FLOAT", "Added latitude to issues")
        run_migration_step("ALTER TABLE issues ADD COLUMN longitude FLOAT", "Added longitude to issues")
        run_migration_step("ALTER TABLE issues ADD COLUMN location VARCHAR", "Added location to issues")
        run_migration_step("ALTER TABLE issues ADD COLUMN action_plan TEXT", "Added action_plan to issues")
        run_migration_step("ALTER TABLE issues ADD COLUMN integrity_hash VARCHAR", "Added integrity_hash to issues")

        run_migration_step("ALTER TABLE grievances ADD COLUMN latitude FLOAT", "Added latitude to grievances")
        run_migration_step("ALTER TABLE grievances ADD COLUMN longitude FLOAT", "Added longitude to grievances")
        run_migration_step("ALTER TABLE grievances ADD COLUMN address VARCHAR", "Added address to grievances")
        run_migration_step("ALTER TABLE grievances ADD COLUMN issue_id INTEGER", "Added issue_id to grievances")

        # Index additions (Using IF NOT EXISTS for better compatibility and performance)
        run_migration_step("CREATE INDEX IF NOT EXISTS ix_issues_upvotes ON issues (upvotes)", "Index on issues.upvotes")
        run_migration_step("CREATE INDEX IF NOT EXISTS ix_issues_created_at ON issues (created_at)", "Index on issues.created_at")
        run_migration_step("CREATE INDEX IF NOT EXISTS ix_issues_status ON issues (status)", "Index on issues.status")
        run_migration_step("CREATE INDEX IF NOT EXISTS ix_issues_latitude ON issues (latitude)", "Index on issues.latitude")
        run_migration_step("CREATE INDEX IF NOT EXISTS ix_issues_longitude ON issues (longitude)", "Index on issues.longitude")
        run_migration_step("CREATE INDEX IF NOT EXISTS ix_issues_status_lat_lon ON issues (status, latitude, longitude)", "Composite index on issues (status, lat, lon)")
        run_migration_step("CREATE INDEX IF NOT EXISTS ix_issues_user_email ON issues (user_email)", "Index on issues.user_email")
        run_migration_step("CREATE INDEX IF NOT EXISTS ix_issues_category_status ON issues (category, status)", "Composite index on issues (category, status)")

        run_migration_step("CREATE INDEX IF NOT EXISTS ix_grievances_latitude ON grievances (latitude)", "Index on grievances.latitude")
        run_migration_step("CREATE INDEX IF NOT EXISTS ix_grievances_longitude ON grievances (longitude)", "Index on grievances.longitude")
        run_migration_step("CREATE INDEX IF NOT EXISTS ix_grievances_status_lat_lon ON grievances (status, latitude, longitude)", "Composite index on grievances (status, lat, lon)")
        run_migration_step("CREATE INDEX IF NOT EXISTS ix_grievances_status_jurisdiction ON grievances (status, current_jurisdiction_id)", "Composite index on grievances (status, jurisdiction)")
        run_migration_step("CREATE INDEX IF NOT EXISTS ix_grievances_issue_id ON grievances (issue_id)", "Index on grievances.issue_id")
        run_migration_step("CREATE INDEX IF NOT EXISTS ix_grievances_assigned_authority ON grievances (assigned_authority)", "Index on grievances.assigned_authority")
        run_migration_step("CREATE INDEX IF NOT EXISTS ix_grievances_category_status ON grievances (category, status)", "Composite index on grievances (category, status)")

        logger.info("Database migration check completed.")
    except Exception as e:
        logger.error(f"Database migration error: {e}")

if __name__ == "__main__":
    init_db()
    migrate_db()
