""" """

import argparse
from datetime import datetime
import logging

from logger import setup_logging
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

    # Request for todays file
    start_date_string = end_date_string = None
    if args.today:
        start_date_string = end_date_string = datetime.today().strftime("%Y-%m-%d")
    # Request for historical files
    elif args.historical:
        if len(args.historical) == 1:  # Single date
            start_date_string = end_date_string = args.historical[0]
        elif len(args.historical) == 2:  # Date range
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
        start_date_obj = datetime.strptime(start_date_string, "%Y-%m-%d")
        end_date_obj = datetime.strptime(end_date_string, "%Y-%m-%d")
    except ValueError:
        parser.error("Incorrect/invalid date format, should be YYYY-MM-DD")

    # Validate date sequence
    if start_date_obj > end_date_obj:
        parser.error(
            "--historical start date must be earlier or equal to end date in YYYY-MM-DD format."
        )

    # Download files
    download_files_within_range(start_date_string, end_date_string)

    # Finish
    logging.info("Download pipeline completed.")


if __name__ == "__main__":
    setup_logging()
    start_download_pipeline()


# --- IGNORE ---
# Example Usage
# python sgx_scrap.py --today
# python sgx_scrap.py --historical 2025-01-09
# python sgx_scrap.py --historical 2025-01-09 2025-01-12
