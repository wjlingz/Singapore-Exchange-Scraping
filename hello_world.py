""" """

import argparse
import requests
import re
from datetime import datetime
from util import estimate_date_index


def start_download_pipeline():
    """
    Function to start the download pipeline.
    1. CLI argparse
    2. File name & date validation
    3. Correct URL generation
    4. Download file
    """
    url = "https://links.sgx.com/1.0.0/derivatives-historical/6037/TC.txt"
    response = requests.get(url)
    # with open('WEBPXTICK_DT.zip', 'wb') as f:
    #    f.write(response.content)
    file_name_content = response.headers.get("Content-Disposition", "")
    date_from_file_name = re.search(r"(\d{8})", file_name_content)
    date_obj_from_file_name = datetime.strptime(date_from_file_name.group(1), "%Y%m%d")
    print(date_obj_from_file_name.strftime("%Y-%m-%d"))


if __name__ == "__main__":
    start_download_pipeline()
