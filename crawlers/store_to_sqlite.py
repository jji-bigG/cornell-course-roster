import os
import requests
import sqlite3
from bs4 import BeautifulSoup
from crawler import SubjectRoster  # Assuming you have this module as mentioned

# Initialize the database
def init_db(db_path='courses.db', schema_path='schema.sql'):
    conn = sqlite3.connect(db_path)
    with open(schema_path, 'r') as f:
        conn.executescript(f.read())
    return conn

# Create a new SQLite database (or connect to an existing one)
conn = init_db()
c = conn.cursor()

def subjectIDs(url, semester):
    if os.path.exists(f'{semester}/subjectIDs.html'):
        with open(f'{semester}/subjectIDs.html', 'r') as f:
            html = f.read()
    else:
        html = requests.get(url).text
        os.makedirs(f'{semester}', exist_ok=True)
        with open(f'{semester}/subjectIDs.html', 'w') as f:
            f.write(html)

    bsParser = BeautifulSoup(html, "lxml")

    ids = []
    for item in bsParser.find_all(name="ul", class_="subject-group"):
        ids.append(item.find('li').find('a').contents[0])
    return ids

def insert_subjects(semester, subjects):
    for subject in subjects:
        c.execute('INSERT INTO subjects (semester, subject_code) VALUES (?, ?)', (semester, subject))
    conn.commit()

def generateSQLForSemestersSubject(semester: str, subject: str):
    print(f'Working on {semester} {subject}')
    
    # Check if the HTML file for the subject already exists, if not, fetch it
    if os.path.exists(f'{semester}/{subject}.html'):
        with open(f'{semester}/{subject}.html', 'r') as f:
            reqText = f.read()
    else:
        reqText = requests.get(
            f"https://classes.cornell.edu/browse/roster/{semester}/subject/{subject}").text
        os.makedirs(semester, exist_ok=True)
        with open(f'{semester}/{subject}.html', 'a+') as f:
            f.write(reqText)

    # Parse the HTML and build sections
    roster = SubjectRoster(reqText)
    roster.buildSections()

    if not roster.sections:
        return

    # Insert each course section into the SQLite database
    for c in roster.sections:
        for course in c:
            course_data = (
                semester,
                subject,
                course['name'],
                course['type'],
                course['section number'],
                course['location'],
                course['days'],
                course['time'],
                course['dates'],
                course['instructor']
            )
            c.execute('''
            INSERT INTO courses (semester, subject, name, type, section_number, location, days, time, dates, instructor)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', course_data)
    conn.commit()

# Main process to go through all semesters and subjects
url = "https://classes.cornell.edu/browse/roster/"
for i in range(14, 24):
    semesters = []
    semesters.append("FA" + str(i))
    semesters.append("SU" + str(i))
    semesters.append("SP" + str(i))
    for semester in semesters:
        try:
            subjects = subjectIDs(url + semester, semester)
        except Exception as e:
            print(f"\nRequesting the subject codes for {semester} failed: {e}\n")
            continue

        if subjects:
            insert_subjects(semester, subjects)
            for subject in subjects:
                generateSQLForSemestersSubject(semester, subject)

# Close the database connection
conn.close()
