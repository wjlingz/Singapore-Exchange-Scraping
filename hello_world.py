""" """

import argparse
import requests
import re
from datetime import datetime
from util import download_files_within_range


def start_download_pipeline():
    """
    Function to start the download pipeline.
    1. CLI argparse
    2. File name & date validation
    3. Correct URL generation
    4. Download file
    """

    # CLI argparse logic
    parser = argparse.ArgumentParser(
        description="Download files from SGX server for a specific date."
    )
    group = parser.add_mutually_exclusive_group(
        required=True
    )  # Either today or historical

    group.add_argument(
        "--today", action="store_true", help="Download today's file only"
    )
    group.add_argument(
        "--historical",
        nargs="+",
        type=str,
        help='Download historical files. Provide 1 date (single day) or 2 dates (date range)\
                        in "YYYY-MM-DD" format. Example:--historical 2025-01-09 or --historical 2025-01-09 2025-01-12',
    )
    args = parser.parse_args()

    start_date_string = end_date_string = None
    if args.today:
        start_date_string = end_date_string = datetime.today().strftime("%Y-%m-%d")
    elif args.historical:
        if len(args.historical) == 1:
            start_date_string = end_date_string = args.historical[0]
        elif len(args.historical) == 2:
            start_date_string = args.historical[0]
            end_date_string = args.historical[1]
        else:  # More than 2 dates provided
            parser.error(
                "--historical requires exactly 1 or 2 dates in YYYY-MM-DD format."
            )
    else:  # This should not happen due to mutually exclusive group
        print("Error: Please provide either --today or --historical option.")
        return

    # Validate date format
    try:
        datetime.strptime(start_date_string, "%Y-%m-%d")
        datetime.strptime(end_date_string, "%Y-%m-%d")
    except ValueError:
        print("Incorrect date format, should be YYYY-MM-DD")
        return

    # Download files
    download_files_within_range(start_date_string, end_date_string)

    # Finish
    print("Download pipeline completed.")


if __name__ == "__main__":
    start_download_pipeline()


# --- IGNORE ---
# Example Usage
# python hello_world.py --today
# python hello_world.py --historical 2025-01-09
# python hello_world.py --historical 2025-01-09 2025-01-12
