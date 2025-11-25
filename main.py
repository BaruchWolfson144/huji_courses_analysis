"""
Main runner for Hebrew University courses project.

This script orchestrates the workflow:
1. Scrape courses from Shnaton website.
2. Clean and load data into SQLite database.
3. Optionally: print summary/logs.

Usage:
    python main.py scrape   # only scrape and save JSON
    python main.py clean    # only clean JSON into DB
    python main.py all      # scrape + clean
"""

import argparse
import logging
from scripts.scrape_courses import scraper
from scripts.clean_and_load import clean_and_load

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def main():
    parser = argparse.ArgumentParser(description="Hebrew University Courses ETL")
    parser.add_argument("action", choices=["scrape", "clean", "all"], 
                        help="Action to perform: scrape JSON, clean DB, or both")
    parser.add_argument("--start", type=int, default=0, help="Starting course ID")
    parser.add_argument("--end", type=int, default=100000, help="Ending course ID (exclusive)")
    args = parser.parse_args()

    if args.action in ["scrape", "all"]:
        logging.info("Starting scraping process...")
        scraper(start=args.start, end=args.end)
        logging.info("Scraping finished.")

    if args.action in ["clean", "all"]:
        logging.info("Starting cleaning & loading process...")
        clean_and_load() 
        logging.info("Cleaning & loading finished.")


if __name__ == "__main__":
    main()
