#!/usr/bin/env python3
"""
Simple migration script for Syria GPT.

This script provides a convenient interface to the migration utility.
Run without arguments to see available commands.
"""

import sys
import os
from pathlib import Path

# Add current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

if __name__ == "__main__":
    try:
        from utils.migration_utility import main
        main()
    except ImportError as e:
        print(f"Failed to import migration utility: {e}")
        print("Make sure you have all required dependencies installed.")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        sys.exit(1)