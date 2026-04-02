"""
run_dashboard.py — Launch the Quantiv Dash server.

Usage:
    python scripts/run_dashboard.py [--port PORT] [--debug]
"""

import sys
import os
import argparse

# Add project root to path so dashboard imports work
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def main():
    parser = argparse.ArgumentParser(description="Launch Quantiv Dashboard")
    parser.add_argument("--port", type=int, default=8050)
    parser.add_argument("--debug", action="store_true", default=True)
    parser.add_argument("--host", default="127.0.0.1")
    args = parser.parse_args()

    from dashboard.app import app
    print(f"Starting Quantiv Dashboard at http://{args.host}:{args.port}")
    app.run(debug=args.debug, port=args.port, host=args.host)


if __name__ == "__main__":
    main()
