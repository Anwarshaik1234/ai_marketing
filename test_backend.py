#!/usr/bin/env python
import sys
import os

# Add the backend directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

try:
    from app.main import app
    print("Backend import: OK")
except Exception as e:
    print(f"Backend import ERROR: {e}")
    import traceback
    traceback.print_exc()
