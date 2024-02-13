# Reddit Image Scraper

## Overview
This script scrapes data from the Reddit tech subreddit, including post titles, authors, timestamps. It then processes the scraped data and stores it in a database.

## Usage
1. Run the `main.py` script.
2. The scraped data will be processed and stored in the database.

## Requirements
- Python 3.x
- Selenium
- Pandas
- BeautifulSoup

## Installation
1. Install Python 3.x from [python.org](https://www.python.org/downloads/).
2. Install all the required Python packages using pip:
   ```bash
   pip install -r requirements.txt

3. Install geckodriver for Firefox. You can download it from the geckodriver releases page and add it to your system's PATH.

## Configuration
Ensure you have a compatible version of geckodriver installed for Firefox. Adjust the executable_path parameter in the scrape function if necessary.
Customize the number of posts to scrape and other parameters as needed.

## Files
main.py: Main script to run the data scraping and processing.
README.md: This file providing instructions and information about the project.

## Credits
Jade: Initial scraping functionality.
Wendy & Lorenzo: Data processing and database storage functionality.
