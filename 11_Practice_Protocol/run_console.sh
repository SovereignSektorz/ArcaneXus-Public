#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail
cd "$(dirname "$0")"
echo "ArcaneXus Practice Protocol Console"
echo "Local-only URL: http://127.0.0.1:1131/"
echo "This service records lifecycle events only; it does not execute actions."
exec python3 protocol_server.py --host 127.0.0.1 --port 1131
