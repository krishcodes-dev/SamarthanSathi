#!/bin/bash
# Run backend WITHOUT auto-reload (Nuclear Fix)
# This guarantees stability by ignoring file changes completely.

# Ensure we are in backend dir
cd "$(dirname "$0")"

# Activate venv if exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

echo "🚀 Starting backend (Manual Reload Mode - Stable)..."
# Logic: No --reload flag. 
# Restart this script manually if you change python code.
uvicorn app.main:app --host 0.0.0.0 --port 8000 --log-level info
