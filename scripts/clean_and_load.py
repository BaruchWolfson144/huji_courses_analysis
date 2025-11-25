#clean & load
import sqlite3
import json
import os
import pandas as pd
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JSON_FILE = os.path.join(BASE_DIR, "data", "raw_courses.json")
DB = os.path.join(BASE_DIR, "data", "huji_shnaton.db")

def clean_and_load(json_file=JSON_FILE, db=DB):
    """
    Clean raw course data from a JSON file and load it into an SQLite database.

    This function reads the raw scraped courses from a JSON file, performs
    cleaning and parsing of key fields (semester, language, faculty, points),
    and saves both the raw and cleaned data into SQL tables.

    Parameters
    ----------
    json_file : str, optional
        Path to the JSON file containing the raw scraped courses.
        Defaults to the module-level constant `JSON_FILE`.
    db : str, optional
        Path to the SQLite database file where tables will be created.
        Defaults to the module-level constant `DB`.

    Returns
    -------
    None
        The function writes data directly to the SQLite database and returns nothing.

    Side Effects
    ------------
    - Creates two tables in the database:
        1. `raw_courses`: stores all courses as they were scraped.
        2. `cleaned_courses`: stores cleaned and parsed course data.
    - Cleans the following fields:
        - `Semester`: converts textual representation to standardized codes ('A', 'B', 'Y', 'C').
        - `Language`: normalizes to 'He', 'En', or 'He&En', or keeps original language for language courses.
        - `Points`: extracts numeric credit value.
        - `Faculty`: extracts main faculty name without sub-faculty details.
    """

    with open(json_file, "r", encoding="utf-8") as f:
        courses = json.load(f)

    conn = sqlite3.connect(db)
    cur = conn.cursor()
    cur.execute("DROP TABLE IF EXISTS raw_courses")
    cur.execute(""" CREATE TABLE raw_courses (
                            ID INTEGER PRIMARY KEY,
                            Name_HE TEXT,
                            Name_EN TEXT,
                            Faculty TEXT,
                            Semester TEXT,
                            Language TEXT,
                            Points REAL,
                            Exam_Type TEXT
                )
                """)

    for course in courses:
        cur.execute("INSERT INTO raw_courses VALUES (?,?,?,?,?,?,?,?)",
        (course["ID"],
        course["Name_HE"],
        course["Name_EN"],
        course["Faculty"],
        course["Semester"],
        course["Language"],
        course["Points"],
        course["Exam_Type"]
        )
        )

    conn.commit()


    # clean data and make clean_courses table 

    #clean funcs:
    
    def parse_Language (raw):
        """ 
        Parses language text from raw Shnaton field. 
        Returns: 'He', 'En' or 'He&En' (for regular courses),
        or (for language courses) the Hebrew name of the language, or None.
        """
        language = ''
        if 'עברית' in raw:
            language += 'He'
        if 'אנגלית' in raw:
            language += 'En'
        if language=='HeEn' or language=='EnHe':
            language = 'He&En'
        if (language == '') and ('נלמד ב' in raw):
            language = raw.replace("נלמד ב", "").strip()
        if language == '':
            language = None
        return language

    def parse_semester(raw):
        """
        Parses semester text from raw Shnaton field.
        Returns: 'A', 'B', 'Y' (for anual courses), 'C' (for summer semester) or None.
        """
        Semester = ''
        if 'סמסטר א' in raw:
            Semester += 'A'
        if 'סמסטר ב' in raw:
            Semester += 'B'
        if 'שנתי' in raw:
            Semester += 'Y'
        if 'קיץ' in raw:
            Semester += 'C'
        if Semester == '':
            return None
        return Semester

    def parse_points(raw):
        """
        Parses points text from raw Shnaton field.
        Returns: float value or None.
        """
        parts = raw.strip().split()
        for part in parts:
            try:
                return float(part)
            except ValueError:
                continue
        return None

    def parse_exam(raw):
        pass

    def parse_faculty(raw):
        """
        Parses faculty text from raw Shnaton field.
        Returns: name of the main faculty of the course without the sub faculty.
        """
        if ":" in raw:
            return raw.split(":",1)[0].strip()
        return raw

    # new clean courses table
    cur.execute("DROP TABLE IF EXISTS cleaned_courses")
    cur.execute(""" CREATE TABLE cleaned_courses (
        ID INTEGER PRIMARY KEY,
        Name_HE TEXT,
        Name_EN TEXT,
        Faculty TEXT,
        Semester TEXT,     
        Language TEXT,
        Points REAL,
        Exam_Type TEXT
        )
    """)

    cur.execute("SELECT * FROM raw_courses")
    rows = cur.fetchall()
    for row in rows:
        ID, Name_HE, Name_EN, Faculty, Semester,language,Points,Exam_Type  = row

        Semester = parse_semester(Semester)
        if Semester is None:
                logging.warning(f"for course number {ID} ({Name_HE[::-1]}) Semester not found")
        language = parse_Language(language)
        if language is None:
                logging.warning(f"for course number {ID} ({Name_HE[::-1]}) language not found")
        Points = parse_points(Points)
        if Points is None:
                logging.warning(f"for course number {ID} ({Name_HE[::-1]}) credits points not found")
        Faculty = parse_faculty(Faculty)
        # Exam_Type = parse_exam(Exam_Type)   

        cur.execute("INSERT INTO cleaned_courses VALUES (?,?,?,?,?,?,?,?)",
        (ID,Name_HE,Name_EN,Faculty,Semester,language,Points,Exam_Type))
        # Semester('A', 'B', 'C', 'Y')
        # language('He', 'En')

    conn.commit()   

    #cur.execute("SELECT * FROM cleaned_courses")
    #table_items = cur.fetchall()
    df = pd.read_sql_query("SELECT * FROM cleaned_courses", conn)
    conn.close()
