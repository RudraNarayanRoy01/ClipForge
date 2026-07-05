import sys
try:
    from src.main import app
    print("SUCCESS")
except Exception as e:
    import traceback
    traceback.print_exc()
    sys.exit(1)
