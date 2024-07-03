# crawl out the course details for each course by reading the the dataset
# we can just write the main class and then the main function at the bottom is diff
# we don't need to store the specific sections under this course, but the general info
from functools import cmp_to_key
import requests
from bs4 import BeautifulSoup
import os
import sqlite3


class CourseDetails:
    def __init__(self, semester: str, course_name: str):
        self.semester = semester
        self.course_name = course_name
        self.subject = course_name.split()[0].strip()
        self.name_code = course_name.split()[1].strip()

        self.url = f"https://classes.cornell.edu/browse/roster/{semester}/class/{self.subject}/{self.name_code}"
        self.reqText = self.get_html()
        self.soup = BeautifulSoup(self.reqText, "lxml")

    def get_html(self):
        if os.path.exists(f"{self.semester}/details/{self.course_name}.html"):
            with open(f"{self.semester}/{self.name_code}.html", "r") as f:
                reqText = f.read()
        else:
            reqText = requests.get(self.url).text
            os.makedirs(self.semester + "/details", exist_ok=True)
            with open(f"{self.semester}/details/{self.name_code}.html", "w+") as f:
                f.write(reqText)
        return reqText

    def get_description(self):
        fr = self.soup.find("p", class_="catalog-descr")
        if fr:
            return fr.text.strip()
        else:
            return "None"

    def get_prerequisites(self):
        fr = self.soup.find("span", class_="catalog-prereq")
        if fr:
            prompt_text = fr.find("span").text
            return fr.text.removeprefix(prompt_text).strip()
        else:
            return "None"

    def get_when_offered(self):
        fr = self.soup.find("span", class_="catalog-when-offered")
        if fr:
            prompt_text = fr.find("span").text
            return fr.text.removeprefix(prompt_text).strip()
        else:
            return "None"

    def get_combined_with(self):
        fr_p_heading = self.soup.find("p", class_="heading")
        if fr_p_heading:
            fr_em = fr_p_heading.find_all("em")
            # print(fr_em[-1])
            if fr_em:
                fr_a_list = [a.text for a in fr_em[-1].find_all("a")]
                # print(fr_a_list)
                return ", ".join(fr_a_list)
            else:
                return "None"
        else:
            return "None"

    def get_distribution(self):
        fr = self.soup.find("span", class_="catalog-distr")
        if fr:
            prompt_text = fr.find("span", class_="catalog-prompt").text
            # print(prompt_text)
            return fr.text.removeprefix(prompt_text).strip()
        else:
            return "None"

    def get_title(self):
        fr_div = self.soup.find("div", class_="title-coursedescr")
        if fr_div:
            return fr_div.find("a").text
        else:
            return "None"

    def get_credits(self):
        fr = self.soup.find("li", class_="credit-info")
        # print(fr)
        if fr:
            fr_credit_val = fr.find("span", class_="credit-val")
            if fr_credit_val:
                return fr_credit_val.text
            else:
                return "None"
        else:
            return "None"

    def get_outcomes(self):
        fr = self.soup.findAll("li", class_="catalog-outcome")
        if fr:
            return [li.text for li in fr]
        else:
            return "None"

    def fetch(self):
        return {
            "title": self.get_title(),
            "description": self.get_description(),
            "prerequisites": self.get_prerequisites(),
            "when_offered": self.get_when_offered(),
            "combined_with": self.get_combined_with(),
            "distribution": self.get_distribution(),
            "credits": self.get_credits(),
            "outcomes": self.get_outcomes(),
        }


def main():
    semester = "FA21"
    course_name = "CS 2110"
    course = CourseDetails(semester, course_name)
    print(course.get_outcomes())


def iterate_from_latest_to_oldest(cursor):
    # given the cursor to our database, let's grab the course details for that course and store it in the database
    # if that course has multiple offerings in the db, we go for the latest of the course

    # first, we select the unique course id's and their corresponding semester (choosing the latest semester) from the database
    cursor.execute("select distinct name, course_id from courses")
    courses = cursor.fetchall()

    # for each course, we get the latest semester by fetching all the semesters for which that course is available
    def compare_semester(s1, s2):
        year1 = int(s1[2:])
        year2 = int(s2[2:])

        if year1 == year2:
            # Compare between the FA > SU > SP
            order = {"FA": 3, "SU": 2, "SP": 1}
            return order[s2[:2]] - order[s1[:2]]
        else:
            return year2 - year1

    seen_courses = set()
    for course in courses:
        if course[0] not in seen_courses:
            cursor.execute(
                "select semester from courses where name = ?",
                (course[0],),
            )
            semesters = cursor.fetchall()
            # sort the semesters using the rank_semester function
            semesters = [s[0] for s in semesters]  # Convert to a list of strings
            sorted_semesters = sorted(semesters, key=cmp_to_key(compare_semester))
            latest_semester = sorted_semesters[0]  # The latest semester
            # print(f"latest semester for course {course[0]} is ", latest_semester)
            # now make the fetch for the course details
            course_details = CourseDetails(latest_semester, course[0])
            details = course_details.fetch()
            # print(details)
            # write this to the sql database under the table course_details
            cursor.execute(
                """
            INSERT INTO course_descriptions (course_id, title, description, prerequisites, when_offered, combined_with, distribution, credits, outcomes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    course[1],
                    details["title"],
                    details["description"],
                    details["prerequisites"],
                    details["when_offered"],
                    details["combined_with"],
                    details["distribution"],
                    details["credits"],
                    str(details["outcomes"]),
                ),
            )
            conn.commit()
            seen_courses.add(course[0])
            print(f"Stored course details for {course[0]} in the database")


current_dir = os.path.dirname(os.path.abspath(__file__))


if __name__ == "__main__":
    # Create a new SQLite database (or connect to an existing one)
    conn = sqlite3.connect("roster_reviews.sqlite.db")
    cursor = conn.cursor()
    iterate_from_latest_to_oldest(cursor)

    conn.close()
