import sys
import os

# Add repo root to sys.path
sys.path.insert(0, os.getcwd())

try:
    import backend.main
    print("Successfully imported backend.main")
except ImportError as e:
    print(f"Failed to import backend.main: {e}")
except Exception as e:
    print(f"Exception during import: {e}")
