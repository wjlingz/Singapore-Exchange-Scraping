"""
Util files for various helper functions and utilities.
1. Calculate Key Index for Date
2. Logging setup
3. Scheduling Setup
"""

from datetime import datetime


def estimate_date_index(date_string):
    """Get the index of the given date. Used in URL generation for the requested date.
    Args:
        date (str): The date in "YYYY-MM-DD" format.

    Returns:
        int: The index of the date.
    """

    # 2020-01-01 starts on key index 4538
    # 2025-01-01 starts on key index 5846
    initial_date = datetime.strptime("2020-01-01", "%Y-%m-%d")
    initial_index = 4538

    target_date = datetime.strptime(date_string, "%Y-%m-%d")
    days_difference = (target_date - initial_date).days
    weekends = 2 * days_difference // 7
    date_index = initial_index + days_difference - weekends

    return date_index


target_date = "2025-09-25"
print(estimate_date_index(target_date))
print(
    f"{target_date} is weekday: {datetime.strptime(target_date, '%Y-%m-%d').weekday()}"
)
