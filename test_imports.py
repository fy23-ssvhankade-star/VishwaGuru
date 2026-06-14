import sys
import os
import asyncio

# Add repo root to sys.path
sys.path.insert(0, os.getcwd())

async def test():
    try:
        from backend.unified_detection_service import UnifiedDetectionService
        service = UnifiedDetectionService()
        print("Service initialized")
        # This triggers the import
        available = await service._check_local_available()
        print(f"Local available: {available}")
    except ImportError as e:
        print(f"ImportError: {e}")
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    asyncio.run(test())
