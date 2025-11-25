#scraper for https://shnaton.huji.ac.il

import requests
import time
from bs4 import BeautifulSoup
import json
import os
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


POST_URL = "https://shnaton.huji.ac.il/index.php/default/NextForm/2026/0" #"https://shnaton.huji.ac.il/index.php"

HEADERS = {
"user-agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36"   
}

import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_FILE = os.path.join(BASE_DIR, "data", "raw_courses.json")

START = 0
END = 100000

def scraper(post_url=POST_URL, headers=HEADERS, output=OUTPUT_FILE, start=START, end=END):
    """
    Scrape course data from the Hebrew University Shnaton website using brute-force
    iteration over possible course numbers.

    This function sends POST requests with varying course IDs, parses the returned
    HTML using BeautifulSoup, extracts course metadata (title, faculty, semester,
    language, points, exam type), and saves all successfully retrieved courses to
    a JSON file.

    Parameters
    ----------
    post_url : str, optional
        URL endpoint that receives POST requests for course lookup.
        Defaults to the module-level constant `POST_URL`.
    headers : dict, optional
        HTTP headers (typically User-Agent) sent with each request.
        Defaults to the module-level constant `HEADERS`.
    output : str or pathlib.Path, optional
        File path where the scraped course list will be written as JSON.
        Defaults to `OUTPUT_FILE`.
    start : int, optional
        First course number to attempt fetching. Defaults to `START`.
    end : int, optional
        Last course number (non-inclusive) to attempt. Defaults to `END`.

    Returns
    -------
list of dict
    A list of dictionaries, each containing course details.
    The function also writes this list to the specified JSON file.

    Notes
    -----
    - The Shnaton website does not provide an official API or index of course IDs.
      Therefore this function uses sequential brute-force requests.
    - A rate-limit delay of ~0.3 seconds is applied between requests to avoid
      overloading the server.
    - Only course numbers for which a Hebrew title is found are included in the
      output (in general, this is the most stable field on the site besides the ID).

    Side Effects
    ------------
    Writes a JSON file with the following structure:
        [
            {
                "ID": <int>,
                "Name_HE": <str>,
                "Name_EN": <str>,
                "Faculty": <str>,
                "Semester": <str>,
                "Language": <str>,
                "Points": <text>,
                "Exam_Type": <str>
            },
            ...
        ]

    """
    all_courses = []
    payload_data = {
                "year": "2026",
                "faculty": "",
                "hug": "", 
                "maslul": "0",
                "peula": "Simple",
                "starting": "1",
                "system": "1",
                "option": "2",
                "word": "",
                "course" : "", #number_course
                "toar": "",
                "shana": "", 
                "coursetype": "",
                "shiur": "", 
                "language": "" 
        }

    logging.info(f"Starting scrape {end} courses ...")
    for number_course in range(start, end):
        if ((number_course%500==0) and (number_course!=0)):
            logging.info(f"Done scraping {number_course} courses..")
            time.sleep(0.3)

            
        payload_data["course"] = str(number_course)
        try:
            response = requests.post(
                        post_url, 
                        headers=headers, 
                        data=payload_data 
                    )
            if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    course_name_he = soup.find('div', class_='data-course-title').text.strip() if soup.find('div', class_='data-course-title') else ''
                    course_name_en = soup.find('div', class_='data-course-title-en').text.strip() if soup.find('div', class_='data-course-title-en') else ''
                    course_school = soup.find('div', class_='data-school').text.strip() if soup.find('div', class_='data-school') else ''
                    course_semester = soup.find('div', class_='additional-data-semester').text.strip() if soup.find('div', class_='additional-data-semester') else ''
                    course_language = soup.find('div', class_='additional-data-language').text.strip() if soup.find('div', class_='additional-data-language') else ''
                    course_points = soup.find('div', class_='additional-data-student-points').text.strip() if soup.find('div', class_='additional-data-student-points') else ''
                    course_test = soup.find('div', class_='additional-data-test').text.strip() if soup.find('div', class_='additional-data-test') else ''
                    if (course_name_he!=""):
                        course_details = {
                            "ID": number_course,
                            "Name_HE": course_name_he,
                            "Name_EN": course_name_en,
                            "Faculty": course_school,
                            "Semester": course_semester,
                            "Language": course_language,
                            "Points": course_points,
                            "Exam_Type": course_test
                        }

                        all_courses.append(course_details)

        except requests.exceptions.RequestException as err:
            logging.error(err)
    logging.info("Done scrape...")
    with open(output, "w", encoding="utf-8") as f:
        json.dump(all_courses, f, ensure_ascii=False, indent=2)
    return all_courses




