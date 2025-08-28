#!/bin/bash
DIR="$(cd "$("dirname" "$0")" && pwd)"
if [ ! -f "$DIR/.venv/bin/activate" ]; then echo "Virtual env missing"; exit 1; fi
. "$DIR/.venv/bin/activate"
export APP_ENV=${APP_ENV:-production}
echo "Starting Portfolio App (version $(cat "$DIR/VERSION" 2>/dev/null || echo unknown))"
exec streamlit run "$DIR/app.py"
