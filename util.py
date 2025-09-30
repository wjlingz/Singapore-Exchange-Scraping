"""
Util files for various helper functions and utilities.

1. Calculate Key Index for Date
2. URL generation
3. Check file existence and date match
4. Download files from SGX server
5. Download files within date range
6. Other failure handling
"""

from time import sleep
from datetime import datetime, timedelta
from pathlib import Path
import logging

import re
import requests


def estimate_date_index(date_string):
    """Get the index of the given date.
    Used in URL generation for the requested date.
    Uses index 5849 for 2025-01-06 (Monday) as the base index.

    Args:
        date (str): The date in "YYYY-MM-DD" format.

    Returns:
        int: The index of the date.
    """

    # 2025-01-06 starts on key index 5849, Monday
    initial_date = datetime.strptime("2025-01-06", "%Y-%m-%d")
    initial_index = 5849

    target_date = datetime.strptime(date_string, "%Y-%m-%d")
    days_difference = (target_date - initial_date).days
    weekends = 2 * (days_difference // 7)
    date_index = initial_index + days_difference - weekends

    return date_index


def calculate_date_index_offset(date_string):
    """* Note, this function is not used in the current implementation. Useful in future enhancements. *

    Calculate the date index offset for a given date.
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
    response = requests.get(url, timeout=10)
    file_name_content = response.headers.get("Content-Disposition", "")
    date_from_file_name = re.search(r"(\d{8})", file_name_content)
    date_obj_from_file_name = datetime.strptime(date_from_file_name.group(1), "%Y%m%d")
    offset = (date_obj - date_obj_from_file_name).days

    logging.info(
        f"""
        Target Date: {date_obj}, Estimated Index: {estimated_index}, \n\
        Actual Date: {date_obj_from_file_name}, Actual Index: {estimated_index + offset}, \n\
        Offset: {offset}
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
        url = f"https://links.sgx.com/1.0.0/derivatives-historical/\
            {estimate_date_index(date_string)}/{file}"
        urls.append(url)

    logging.debug(
        f"Using index {estimate_date_index(date_string)} for date {date_string}"
    )
    return urls


def check_existence(responses):
    """Check if all responses are successful (status code 200), and if the files exist.

    Args:
        responses (list): List of response objects from requests.

    Returns:
        bool: True if all responses are successful, False otherwise.
    """
    for response in responses:
        if response.status_code != 200:
            logging.error(
                f"Received status code {response.status_code} for URL {response.url}"
            )
            return False
        if "CustomErrorPage" in response.url:
            logging.error(f"File not found with URL {response.url}")
            return False
    return True


def check_date_match(date_string, responses):
    """Check if the date in the file names from responses matches the requested date.

    Args:
        date_string (str): The requested date in "YYYY-MM-DD" format.
        responses (list): List of response objects from requests.

    Returns:
        bool: True if all file dates match the requested date, False otherwise.
    """
    requested_date_formatted = date_string.replace("-", "")
    for response in responses:
        file_name_content = response.headers.get("Content-Disposition", "")

        if "structure" in file_name_content:
            continue  # Skip data_structure files, they dont have date in file name

        file_date = re.search(r"(\d{8})", file_name_content).group(1)
        if file_date != requested_date_formatted:
            logging.error(
                f"The date in the file name {file_date} does not match the requested date {date_string}."
            )
            return False
    return True


def download_files(date_string):
    """
    Download all 4 types of files from SGX server for a specific date.
    All four files are a unit and should be downloaded or be failed together.

    Args:
        date_string (str): The date in "YYYY-MM-DD" format.

    Returns:
        int: 1 if download is successful, 0 otherwise.
    """
    logging.info(
        f"Downloading files for date {date_string} ({datetime.strptime(date_string, '%Y-%m-%d').strftime('%A')})..."
    )
    # Create folder with date_string as name
    folder = Path(f"downloads/{date_string}")
    folder.mkdir(parents=True, exist_ok=True)

    urls = url_generation(date_string)

    try:
        responses = [requests.get(url, timeout=10) for url in urls]
    except requests.exceptions.RequestException as e:
        logging.error(
            f"Failed to download files for date {date_string}. Exception: {e}"
        )
        return 0

    # Check if all responses are successful
    if not check_existence(responses):
        logging.error(f"One or more files do not exist for date {date_string}.")
        return 0

    # Check if the date in the file names match the requested date
    if not check_date_match(date_string, responses):
        logging.error(f"Date mismatch for files from date {date_string}.")
        return 0

    logging.debug(f"Files with correct date has been found: {date_string}")

    for response in responses:
        file_name = response.url.split("/")[-1]
        file_path = f"{folder}/{date_string}_{file_name}"
        with open(file_path, "wb") as f:
            f.write(response.content)
        logging.debug(f"Downloaded {date_string}_{file_name}")

    logging.info(f"All files downloaded for date {date_string}")
    return 1


def download_files_within_range(start_date, end_date):
    """
    Download files from SGX server for a range of dates.

    Args:
        start_date (str): The start date in "YYYY-MM-DD" format.
        end_date (str): The end date in "YYYY-MM-DD" format.

    Returns:
        None
    """
    start_date_obj = datetime.strptime(start_date, "%Y-%m-%d")
    end_date_obj = datetime.strptime(end_date, "%Y-%m-%d")

    # Initialization and start the download process
    CIRCUIT_BREAKER_THRESHOLD = 10  # Triggered if there are 10 consecutive failures
    circuit_breaker_count = 0
    MAX_CURRENT_DATE_RETRIES = 3  # Max retries for the same date
    current_date_fails = 0
    dates_for_manual_retries = []

    current_date = start_date_obj
    while current_date <= end_date_obj:

        # Circuit breaker to avoid overwhelming the server with requests
        if circuit_breaker_count >= CIRCUIT_BREAKER_THRESHOLD:
            logging.error(
                f"{circuit_breaker_count} consecutive fails detect, circuit breaker triggered. Stopping further downloads."
            )
            failed_date_range = f"{current_date.strftime('%Y-%m-%d')} ~ {end_date}"
            dates_for_manual_retries.append(failed_date_range)
            break

        # Skip weekends
        if current_date.weekday() >= 5:  # 5 = Saturday, 6 = Sunday
            logging.info(f"Skipping weekend date: {current_date.strftime('%Y-%m-%d')}")
            current_date += timedelta(days=1)
            continue

        # Initialize date_string and setup for failed retries
        date_string = current_date.strftime("%Y-%m-%d")
        success_flag = 0

        # Record if current download is successful or failed.
        try:
            success_flag = download_files(date_string)
        except Exception as e:
            logging.error(
                f"Unexpected Exception occurred while downloading files for date {date_string}: {e}"
            )
            success_flag = 0

        # Circuit breaker logic & retry mechanism
        if success_flag == 0:
            current_date_fails += 1
            circuit_breaker_count += 1
            logging.error(
                f"Failed to download files for date {date_string}. Attempt {current_date_fails} of {MAX_CURRENT_DATE_RETRIES}."
            )
            if current_date_fails < MAX_CURRENT_DATE_RETRIES:
                logging.info(f"Retrying download for date {date_string}...")
                # Wait before retrying (optional)
                sleep(2**current_date_fails)
                continue  # Retry the same date
            else:
                dates_for_manual_retries.append(current_date.strftime("%Y-%m-%d"))
                logging.error(
                    f"Max retries reached for date {date_string}. Moving to next date."
                )
        # Reset circuit breaker count on success
        else:
            circuit_breaker_count = 0

        # Proceed next step if not stopped before this.
        current_date += timedelta(days=1)
        current_date_fails = 0  # Reset fails for next date

    # Summary of failed downloads
    if dates_for_manual_retries != []:
        logging.warning(
            f"Some dates failed to download and may require manual retries: {dates_for_manual_retries}"
        )


# DATE = "2025-09-30"  # Wednesday
# print(url_generation(DATE))
# download_files(DATE)
# print(estimate_date_index("2025-01-09"))
# calculate_date_index_offset("2025-09-22")
# download_files_within_range("2025-09-19", "2025-09-23")

# Test retries logic by adding explicit exception raise in download_files function in different places
# download_files_within_range("2025-09-19", "2025-09-25")


# Consider
# Include global variable OFFSET, and documentation on how to update it when there are changes in SGX server behavior


# Concern
# 1. dont know what kind of exception could happen
# 2. 4 files are a unit, should be downloaded or be failed together
# 3. weekends and public holidays, no files available, but sometime could have files
# 4. could add more information as a summary, such as total files downloaded, total size, total time taken
# 5. log file are becoming bigger over time, need to optimize it
# 6. date match checking relies on the file name format, if SGX change the format, need to update the regex
