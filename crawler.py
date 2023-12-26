# given a course subject filtered page,
# crawl and pull down the list of course numbers, names, location, professors...

import requests
from bs4 import BeautifulSoup


class SubjectRoster:
    soup: BeautifulSoup = None
    courses = []
    sections = []  # a parsed list of the list of lectures + discussions available

    # pass down the entire html string of the subject filtered page
    def __init__(self, html: str) -> None:
        self.soup = BeautifulSoup(html, "html.parser")
        self.parseCourses()
        self.sections = []

    def parseCourses(self) -> list:
        self.courses = self.soup.find_all(
            "div", class_="node", role="region")
        return self.courses

    def findCourseFromNode(self, course: BeautifulSoup) -> str:
        return course.find("div", class_="title-subjectcode").contents[0]

    def findTypeFromClass(self, course: BeautifulSoup) -> str:
        if course.find('em', attrs={"class": "tooltip-iws"}):
            return course.find('em', attrs={"class": "tooltip-iws"})['data-content']
        else:
            return "None"

    def findSectionNumberFromClass(self, course: BeautifulSoup) -> str:
        if course.find('li', class_="class-numbers") and course.find('li', class_="class-numbers").find('p') and course.find('li', class_="class-numbers").find('p').find('strong', class_="tooltip-iws"):
            return course.find('li', class_="class-numbers").find('p').find('strong', class_="tooltip-iws")['data-content']
        else:
            return "None"

    def findProfFromClass(self, course: BeautifulSoup) -> str:
        if course.find("li", class_="instructors") and course.find("li", class_="instructors").find('span', class_="tooltip-iws"):
            return course.find("li", class_="instructors").find('span', class_="tooltip-iws")['data-content']
        else:
            return "None"

    def findDatesFromClass(self, course: BeautifulSoup) -> str:
        if course.find(
                'li', class_="section-alt section-alt-details date-range"):
            return course.find(
                'li', class_="section-alt section-alt-details date-range").contents[0].strip()

        # start = rawDates.split('-')[0].strip()
        # end = rawDates.split('-')[1].split(',')[0].strip()
        # year = rawDates.split(',')[1].strip()

        else:
            return "None"

    def findTimeFromClass(self, course: BeautifulSoup) -> str:
        if (course.find('time', class_='time') is not None):
            return course.find('time', class_='time').contents[0].strip("\"")
        else:
            return "None"

    def findDaysFromClass(self, course: BeautifulSoup) -> str:
        if course.find('li', class_="meeting-pattern") and course.find('li', class_="meeting-pattern").find('span', class_="pattern-only") and course.find('li', class_="meeting-pattern").find('span', class_="pattern-only").find('span', class_="tooltip-iws"):
            return course.find('li', class_="meeting-pattern").find('span', class_="pattern-only").find('span', class_="tooltip-iws")['data-content']
        else:
            return "None"

    def findLocationFromClass(self, course: BeautifulSoup) -> str:
        if (course.find('a', class_="facility-search") is not None):
            return course.find('a', class_="facility-search").contents[0]
        else:
            return "NONE"

    def parseSectionsFromCourse(self, course: BeautifulSoup) -> list:
        # relevant information for each section
        # { name, type (DIS 216), days, dates, time, location, sec_number, instructor }
        sections = []

        name = self.findCourseFromNode(course).strip()
        for c in course.find('div', class_='sections').find_all('ul', class_=["section", "active-tab-details"]):
            # print(name, self.findSectionNumberFromClass(c))
            sections.append({
                "name": name,
                "type": self.findTypeFromClass(c).strip(),
                'section number': self.findSectionNumberFromClass(c).strip(),
                "location": self.findLocationFromClass(c).strip(),
                'days': self.findDaysFromClass(c).strip(),
                'time': self.findTimeFromClass(c).strip(),
                'dates': self.findDatesFromClass(c).strip(),
                'instructor': self.findProfFromClass(c).strip()
            })

        return sections

    def buildSections(self):
        for c in self.courses:
            section = self.parseSectionsFromCourse(c)
            if (not section):
                continue
            self.sections.append(section)


# with open('FA14/AAS.html', 'r+') as f:
#     roster = SubjectRoster(f.read())
#     roster.buildSections()
#     print(len(roster.courses))
#     print(roster.sections)
