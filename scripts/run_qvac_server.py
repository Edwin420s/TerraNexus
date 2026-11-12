#!/usr/bin/env python3
"""
TerraNexus QVAC Local Hardware Inference Server Command (TNX-AI-001)
Runs the quantized local agronomic intelligence engine completely offline.
Compatible with OpenAI /v1/chat/completions API format.

Usage:
    python3 scripts/run_qvac_server.py [--port 8080] [--host 0.0.0.0]
    make run-qvac
"""

import sys
import os
import argparse

# Ensure backend directory is in python search path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
backend_dir = os.path.join(project_root, "backend")

if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.services.qvac_server import start_server

def main():
    parser = argparse.ArgumentParser(description="Start TerraNexus QVAC Local Hardware AI Server")
    parser.add_argument("--host", default="127.0.0.1", help="Binding host interface (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=8080, help="Listening port (default: 8080)")
    args = parser.parse_args()

    start_server(host=args.host, port=args.port)

if __name__ == "__main__":
    main()
