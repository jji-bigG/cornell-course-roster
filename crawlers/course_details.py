# crawl out the course details for each course by reading the the dataset
# we can just write the main class and then the main function at the bottom is diff
# we don't need to store the specific sections under this course, but the general info
import requests
from bs4 import BeautifulSoup
import os


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
        return self.soup.find("p", class_="catalog-descr").text.strip()

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
                print(fr_a_list)
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


def main():
    semester = "FA21"
    course_name = "CS 2110"
    course = CourseDetails(semester, course_name)
    print(course.get_title())


if __name__ == "__main__":
    main()
