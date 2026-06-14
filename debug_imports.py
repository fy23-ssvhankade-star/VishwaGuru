import sys
import os

# Mock paths like Render might have
sys.path.append(os.getcwd())

try:
    from backend.adaptive_weights import adaptive_weights
    print("Imported adaptive_weights successfully")
except Exception as e:
    print(f"Failed to import adaptive_weights: {e}")

try:
    from backend.civic_intelligence import civic_intelligence_engine
    print("Imported civic_intelligence_engine successfully")
except Exception as e:
    print(f"Failed to import civic_intelligence_engine: {e}")
