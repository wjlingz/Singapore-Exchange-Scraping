"""
Util files for various helper functions and utilities.
1. Calculate Key Index for Date
2. Logging setup
3. Scheduling Setup
"""

from datetime import datetime, timedelta
from pathlib import Path

import re
import requests


def estimate_date_index(date_string):
    """Get the index of the given date. Used in URL generation for the requested date.
    Args:
        date (str): The date in "YYYY-MM-DD" format.

    Returns:
        int: The index of the date.
    """

    # 2020-01-01 starts on key index 4538
    # 2025-01-01 starts on key index 5845, Wednesday
    # 2025-01-06 starts on key index 5850, Monday
    initial_date = datetime.strptime("2025-01-06", "%Y-%m-%d")
    initial_index = 5849

    target_date = datetime.strptime(date_string, "%Y-%m-%d")
    days_difference = (target_date - initial_date).days
    weekends = 2 * (days_difference // 7)
    date_index = initial_index + days_difference - weekends

    return date_index


def calculate_date_index_offset(date_string):
    """Calculate the date index offset for a given date.
    Normally, the date index is increment by 1 for each weekday, and skip to next weekday after weekend.
    However, there are exceptions where weekends also increment the index by 1~2.
    So actual index need to be calculated by checking the actual file name returned by SGX server.

    1. Estimate the date index using a simple formula.
    2. Fetch the file name from SGX server using the estimated index.
    3. Extract the actual date from the file name.
    4. Calculate the offset between the estimated date and actual date.

    The actual date index = estimated date index + offset

    Args:
        date (str): The date in "YYYY-MM-DD" format.

    Returns:
        int: The offset of the date index.
    """

    date_obj = datetime.strptime(date_string, "%Y-%m-%d")
    estimated_index = estimate_date_index(date_string)

    url = f"https://links.sgx.com/1.0.0/derivatives-historical/{estimated_index}/TC.txt"
    response = requests.get(url)
    file_name_content = response.headers.get("Content-Disposition", "")
    date_from_file_name = re.search(r"(\d{8})", file_name_content)
    date_obj_from_file_name = datetime.strptime(date_from_file_name.group(1), "%Y%m%d")
    offset = (date_obj - date_obj_from_file_name).days

    print(
        f"""
        Target Date: {date_obj}, Estimated Index: {estimated_index}, \n\
        Actual Date: {date_obj_from_file_name}, Offset: {offset}, Actual Index: {estimated_index + offset}
        """
    )


def url_generation(date_string):
    """Generate a list of URLs for downloading files for a specific date.

    Args:
        date_string (str): The date in "YYYY-MM-DD" format.

    Returns:
        list: A list of URLs for the specified date.
    """

    urls = []
    files_to_download = [
        "WEBPXTICK_DT.zip",
        "TickData_structure.dat",
        "TC.txt",
        "TC_structure.dat",
    ]

    for file in files_to_download:
        url = f"https://links.sgx.com/1.0.0/derivatives-historical/{estimate_date_index(date_string)}/{file}"
        urls.append(url)

    print(f"Using index {estimate_date_index(date_string)} for date {date_string}")
    return urls


def download_files(date_string):
    """
    Download all 4 types of files from SGX server for a specific date.

    Args:
        date_string (str): The date in "YYYY-MM-DD" format.
    """
    print(
        f"Downloading files for date {date_string} ({datetime.strptime(date_string, '%Y-%m-%d').strftime('%A')})..."
    )
    # Create folder with date_string as name
    folder = Path(f"downloads/{date_string}")
    folder.mkdir(parents=True, exist_ok=True)

    urls = url_generation(date_string)

    # Verify the date from the file name matches the requested date
    response = requests.get(urls[0])
    file_name_content = response.headers.get("Content-Disposition", "")
    file_date = re.search(r"(\d{8})", file_name_content).group(1)

    if file_date != date_string.replace("-", ""):
        print(
            f"Error: The date in the file name {file_date} does not match the requested date {date_string}."
        )
        return

    for url in urls:
        response = requests.get(url)
        file_name = url.split("/")[-1]
        file_path = f"{folder}/{file_date}_{file_name}"
        with open(file_path, "wb") as f:
            f.write(response.content)
        print(f"Downloaded {file_date}_{file_name}")

    print(f"All files downloaded for date {date_string}")


def download_files_within_range(start_date, end_date):
    """
    Download files from SGX server for a range of dates.

    Args:
        start_date (str): The start date in "YYYY-MM-DD" format.
        end_date (str): The end date in "YYYY-MM-DD" format.
    """
    start_date_obj = datetime.strptime(start_date, "%Y-%m-%d")
    end_date_obj = datetime.strptime(end_date, "%Y-%m-%d")

    if start_date_obj > end_date_obj:
        print("Error: Start date must be before or equal to end date.")
        return

    current_date = start_date_obj
    while current_date <= end_date_obj:
        date_string = current_date.strftime("%Y-%m-%d")
        download_files(date_string)
        current_date += timedelta(days=1)


# DATE = "2025-09-23"  # Wednesday
# print(url_generation(DATE))
# download_files(DATE)
# print(estimate_date_index("2025-01-09"))
# calculate_date_index_offset("2025-09-22")
# download_files_within_range("2025-09-22", "2025-09-24")

# TODO: Add logging
# TODO: Add retry mechanism for failed downloads
# TODO: Handle no file found
