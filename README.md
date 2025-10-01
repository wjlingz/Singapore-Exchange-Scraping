# SGX Data Scraping Project
Project description: SGX publishes derivative data daily at the website: https://www.sgx.com/research-education/derivatives  
This project will download the following files daily from the above website.
1.	WEBPXTICK_DT-*.zip
2.	TickData_structure.dat
3.	TC_*.txt
4.	TC_structure.dat

# Usage
The file can be executed in command line interface.   
#### CLI options  
```
  --today	: a flag, indicating users only want file’s matching today’s date	  
  --historical [date]: mutually exclusive argument with “today”, requires 1~2 date(s). Provide 1 date to download files for that date only, or 2 dates to download files for the entire date range (inclusive). Date format should be “YYYY-MM-DD”  
```
#### Example usage: 	
```
  python sgx_scrap.py –today	
  python sgx_scrap.py --historical 2025-01-09	
  python sgx_scrap.py --historical 2025-01-09 2025-01-12
```
# Project Structure

-	sgx_scrap.py  
-	util.py  
-	logger.py  
    -	downloads  
        - [date1]  
        - [date2]
            -	[date2]_WEBXTICK_DT.zip  
            - [date2]_....  
-	logs  
    -	[date]_[time].log  

# Validation
Input validation is done together with argparse such as date format and date logic, handling it before it touches util function. 
Inside util function, the requested files are checked for their existence, and whether the date of the file matches what is requested. 
# Download 
The index needs to be calculated to match a specific date. All 4 files on the same date are considered a unit, meaning all four succeed or fail together.  Downloads are done via simple HTML request.
# Failure
The program can encounter errors in several situations:
1.	File requested does not exist
2.	File dates do not match the requested date, according to the index logic calculation
3.	Cannot reach the server / request timed out
4.	Any other unexpected / uncaught exception
# Recovery
The program can stop in two ways:
1.	A download of a specific date can have maximum 3 numbers of retry. There is a waiting time between each retry and it gets longer with more retries. After exceeding 3 tries, it moves on to next date in line.
2.	A circuit breaker would stop all consecutive pipelines if it detected 10 consecutive failures in a row. (Meaning if three date failed all 3 attempts, the next failure will stop the program)
The retry attempt for a single date (failure 1.) is automatic, whereas the recovery for other method will store the failed date in the log file, pending for manual recovery.
# Logging
Only information with logging level more than or equal to INFO will be output to STDOUT, and information with any logging level will be stored in the log files. The log files are created for each pipeline run, as long as each run is executed at the same exact time. The failed dates can be found in the last line in this log for manual redownload.
# Additional Info
1.	The main concern is the logic of calculating the index required for a specific date. Normally, SGX does not have data for weekend, therefore the index will not be incremented by Saturday and Sunday. However, it is found that some weekends will have the data and will therefore mess up the index of future dates. So far, this problem has not happened since 2025-01-01, but if it happens, it will require adding an offset to push the index forward. The function to calculate the offset is provided but not used in current version.
2.	Date matching and several other logics rely on the naming convention from SGX side, it will require changes in this program to accommodate, should the naming convention change. However, I doubt it will happen frequently, if it even happens.
3.	Log files currently do not delete themselves, so the size will become larger as time goes on. Auto / Manual deletion will be needed in the future.
4.	Log files could be improved by including more information on the pipeline run, such as a summary etc. 
5.	Depending on the frequency of the download failure, it might be better to write a script that triggers redownload based on the list of failed dates from the logs. Currently, the trigger is manually entered using logs information.
6.	Current error/exception handling only handle what I can think of, there might be other types of exception that should be handled differently instead of being handled under the same behaviors.
7.	It is possible to download older files, disregarding the 5 days limit on the website.
8.	The function to calculate index offset is particularly useful when downloading old files, because there are more weekend exceptions in older files.
 
