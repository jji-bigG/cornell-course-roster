import os
import requests
import sqlite3
from bs4 import BeautifulSoup
from course_details import iterate_from_latest_to_oldest
from roster_crawler import (
    SubjectRoster,
)  # Assuming you have this module as mentioned


# os.chdir(os.path.dirname(os.path.abspath(__file__)))
current_dir = os.path.dirname(os.path.abspath(__file__))


# Initialize the database
def init_db(
    db_path="roster_reviews.sqlite.db",
    schema_path=os.path.join(current_dir, "schema.sql"),
):
    conn = sqlite3.connect(db_path)
    with open(schema_path, "r") as f:
        conn.executescript(f.read())
    conn.commit()
    return conn


# Create a new SQLite database (or connect to an existing one)
conn = init_db()
cursor = conn.cursor()


def subjectIDs(url, semester):
    if os.path.exists(f"{semester}/subjectIDs.html"):
        with open(f"{semester}/subjectIDs.html", "r") as f:
            html = f.read()
    else:
        html = requests.get(url).text
        os.makedirs(f"{semester}", exist_ok=True)
        with open(f"{semester}/subjectIDs.html", "w") as f:
            f.write(html)

    bsParser = BeautifulSoup(html, "lxml")

    ids = []
    for item in bsParser.find_all(name="ul", class_="subject-group"):
        ids.append(item.find("li").find("a").contents[0])
    return ids


def insert_subjects(semester, subjects):
    for subject in subjects:
        cursor.execute(
            "INSERT INTO subjects (semester, subject_code) VALUES (?, ?)",
            (semester, subject),
        )
    conn.commit()


def generateSQLForSemestersSubject(semester: str, subject: str):
    print(f"Working on {semester} {subject}")

    # Check if the HTML file for the subject already exists, if not, fetch it
    if os.path.exists(f"{semester}/{subject}.html"):
        with open(f"{semester}/{subject}.html", "r") as f:
            reqText = f.read()
    else:
        reqText = requests.get(
            f"https://classes.cornell.edu/browse/roster/{semester}/subject/{subject}"
        ).text
        os.makedirs(semester, exist_ok=True)
        with open(f"{semester}/{subject}.html", "w+") as f:
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
                course["name"],
                course["type"],
                course["section_number"],
                course["location"],
                course["days"],
                course["time"],
                course["dates"],
                course["instructor"],
            )
            # delete the previous records for the same course
            cursor.execute(
                """
            DELETE FROM courses
            WHERE semester = ? AND subject = ? AND name = ? AND type = ? AND section_number = ? AND location = ? AND days = ? AND time = ? AND dates = ? AND instructor = ?""",
                course_data,
            )

            cursor.execute(
                """
            INSERT INTO courses (semester, subject, name, type, section_number, location, days, time, dates, instructor)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                course_data,
            )
    conn.commit()


# Main process to go through all semesters and subjects
def main():
    url = "https://classes.cornell.edu/browse/roster/"
    for i in reversed(range(14, 25)):
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


if __name__ == "__main__":
    main()
    iterate_from_latest_to_oldest(cursor)

# Close the database connection
conn.close()
