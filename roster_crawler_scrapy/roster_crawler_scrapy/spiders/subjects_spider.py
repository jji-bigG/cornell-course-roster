import scrapy
from bs4 import BeautifulSoup


class SubjectsSpider(scrapy.Spider):
    name = "subjects_spider"
    start_urls = []

    def start_requests(self):
        base_url = "https://classes.cornell.edu/browse/roster/"
        semesters = [
            f"{term}{year}" for year in range(14, 25) for term in ["FA", "SU", "SP"]
        ]

        for semester in semesters:
            url = f"{base_url}{semester}/subject"
            yield scrapy.Request(url, self.parse_subjects, meta={"semester": semester})

    def parse_subjects(self, response):
        semester = response.meta["semester"]
        soup = BeautifulSoup(response.text, "lxml")
        subject_links = soup.select("a.subject")

        for link in subject_links:
            subject_name = link.get_text()
            subject_url = response.urljoin(link["href"])
            yield scrapy.Request(
                subject_url,
                self.parse_subject_overview,
                meta={"semester": semester, "subject_name": subject_name},
            )

    def parse_subject_overview(self, response):
        semester = response.meta["semester"]
        subject_name = response.meta["subject_name"]

        roster = SubjectRoster(response.text)
        roster.buildSections()

        for section in roster.sections:
            for course in section:
                course.update({"semester": semester, "subject_name": subject_name})
                yield course


class SubjectRoster:
    def __init__(self, html: str) -> None:
        self.soup = BeautifulSoup(html, "lxml")
        self.courses = self.parse_courses()
        self.sections = []

    def parse_courses(self) -> list:
        return self.soup.find_all("div", class_="node", role="region")

    def buildSections(self):
        for course in self.courses:
            section = self.parse_sections_from_course(course)
            if section:
                self.sections.append(section)

    def parse_sections_from_course(self, course):
        sections = []
        name = self.find_course_from_node(course).strip()
        for c in course.find("div", class_="sections").find_all(
            "ul", class_=["section", "active-tab-details"]
        ):
            sections.append(
                {
                    "name": name,
                    "type": self.find_type_from_class(c).strip(),
                    "section_number": self.find_section_number_from_class(c).strip(),
                    "location": self.find_location_from_class(c).strip(),
                    "days": self.find_days_from_class(c).strip(),
                    "time": self.find_time_from_class(c).strip(),
                    "dates": self.find_dates_from_class(c).strip(),
                    "instructor": self.find_prof_from_class(c).strip(),
                }
            )
        return sections

    def find_course_from_node(self, course):
        return course.find("div", class_="title-subjectcode").contents[0]

    def find_type_from_class(self, course):
        return (
            course.find("em", class_="tooltip-iws")["data-content"]
            if course.find("em", class_="tooltip-iws")
            else "None"
        )

    def find_section_number_from_class(self, course):
        sec = course.find("li", class_="class-numbers")
        if sec and sec.find("p") and sec.find("p").find("strong", class_="tooltip-iws"):
            return sec.find("p").find("strong", class_="tooltip-iws")["data-content"]
        return "None"

    def find_prof_from_class(self, course):
        instructor = course.find("li", class_="instructors")
        if instructor and instructor.find("span", class_="tooltip-iws"):
            return instructor.find("span", class_="tooltip-iws")["data-content"]
        return "None"

    def find_dates_from_class(self, course):
        date = course.find("li", class_="section-alt section-alt-details date-range")
        return date.contents[0].strip() if date else "None"

    def find_time_from_class(self, course):
        time = course.find("time", class_="time")
        return time.contents[0].strip('"') if time else "None"

    def find_days_from_class(self, course):
        days = course.find("li", class_="meeting-pattern")
        if (
            days
            and days.find("span", class_="pattern-only")
            and days.find("span", "pattern-only").find("span", class_="tooltip-iws")
        ):
            return days.find("span", "pattern-only").find("span", class_="tooltip-iws")[
                "data-content"
            ]
        return "None"

    def find_location_from_class(self, course):
        location = course.find("a", class_="facility-search")
        return location.contents[0] if location and location.contents else "None"
