#!/usr/bin/env python
"""Entry point for running Paper Hunter Streamlit application."""

import os
import subprocess
import sys


def main():
    """Run the Streamlit application."""
    # Ensure we're in the project root
    project_root = os.path.dirname(os.path.abspath(__file__))
    os.chdir(project_root)

    # Run streamlit with the app
    streamlit_cmd = [
        sys.executable,
        "-m",
        "streamlit",
        "run",
        "src/ui/app.py",
        "--logger.level=error",
    ]

    subprocess.run(streamlit_cmd)


if __name__ == "__main__":
    main()
