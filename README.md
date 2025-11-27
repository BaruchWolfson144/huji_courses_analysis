# Hebrew University Courses Analysis

**Project type:** Web Scraping + ETL + Data Analysis  
**Language:** Python 3.12  
**Libraries:** requests, BeautifulSoup, pandas, sqlite3, matplotlib, logging  

---

## **Overview**

This project scrapes course data from the [Hebrew University Shnaton website](https://shnaton.huji.ac.il), cleans and stores it in a SQLite database, and provides basic analysis of course metadata such as credit points, semesters, languages, and faculties.  

The workflow is divided into three main steps:
1. **Scraping:** Brute-force iteration over course IDs to fetch course details (title, faculty, semester, language, points, exam type).  
2. **Cleaning & Loading:** Standardizes fields, handles missing data, and loads clean data into a database.  
3. **Analysis:** Generates summary statistics and plots (credit distribution, semester distribution, language distribution, faculty distribution).  

---

## **Project Structure**
```
courses_analysis/
├─ scripts/
│ ├─ scrape_courses.py # scraper function
│ └─ clean_and_load.py # cleaning & loading functions
├─ data/
│ ├─ huji_shnaton.db # SQLite database
│ └─ raw_courses_2026.json # raw JSON from scraper (here data from 2026 for example)
├─ analysis/
│ └─ 01_basic_statistic.ipynb # Jupyter notebook for analysis
├─ venv/ # virtual environment
├─ main.py # main runner script
└─ README.md # project description
```

---

## **How to Run**

Activate virtual environment:
```bash
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

pip install -r requirements.txt

# Only scrape courses and save JSON
python main.py scrape --start 0 --end 10000

# Only clean JSON and load to SQLite
python main.py clean

# Run full ETL: scrape + clean
python main.py all
```
---


## **Highlights:**

Robust Scraping: Handles missing fields and logs errors.

ETL Pipeline: Modular functions for scraping, cleaning, and loading.

Data Analysis: Histograms, bar plots, and summary statistics for course points, semesters, languages, and faculties.

Portfolio Ready: Clean structure, logging, and professional README.