import scrapy
import os
import json
from urllib.parse import urljoin
from scrapy.utils.project import get_project_settings


class CourseDetailsSpider(scrapy.Spider):
    name = "course_details"
    start_urls = []  # This will be populated with URLs from a file or other source

    def __init__(self, *args, **kwargs):
        super(CourseDetailsSpider, self).__init__(*args, **kwargs)
        self.semester = kwargs.get("semester", "FA21")
        self.load_course_names()

    def load_course_names(self):
        # Load course names from a file or other source
        with open("courses.json") as f:
            courses = json.load(f)
        for course_name in courses:
            subject = course_name.split()[0].strip()
            name_code = course_name.split()[1].strip()
            url = f"https://classes.cornell.edu/browse/roster/{self.semester}/class/{subject}/{name_code}"
            self.start_urls.append(url)

    def parse(self, response):
        course_details = {
            "url": response.url,
            "title": self.get_title(response),
            "description": self.get_description(response),
            "prerequisites": self.get_prerequisites(response),
            "when_offered": self.get_when_offered(response),
            "combined_with": self.get_combined_with(response),
            "distribution": self.get_distribution(response),
            "credits": self.get_credits(response),
            "outcomes": self.get_outcomes(response),
        }
        yield course_details

    def get_description(self, response):
        fr = response.css("p.catalog-descr::text").get()
        return fr.strip() if fr else "None"

    def get_prerequisites(self, response):
        fr = response.css("span.catalog-prereq").get()
        if fr:
            prompt_text = response.css("span.catalog-prereq span::text").get()
            return fr.removeprefix(prompt_text).strip()
        return "None"

    def get_when_offered(self, response):
        fr = response.css("span.catalog-when-offered").get()
        if fr:
            prompt_text = response.css("span.catalog-when-offered span::text").get()
            return fr.removeprefix(prompt_text).strip()
        return "None"

    def get_combined_with(self, response):
        fr_p_heading = response.css("p.heading")
        if fr_p_heading:
            fr_em = fr_p_heading.css("em")
            if fr_em:
                fr_a_list = [a.css("a::text").get() for a in fr_em[-1].css("a")]
                return ", ".join(fr_a_list)
        return "None"

    def get_distribution(self, response):
        fr = response.css("span.catalog-distr").get()
        if fr:
            prompt_text = response.css(
                "span.catalog-distr span.catalog-prompt::text"
            ).get()
            return fr.removeprefix(prompt_text).strip()
        return "None"

    def get_title(self, response):
        fr_div = response.css("div.title-coursedescr a::text").get()
        return fr_div if fr_div else "None"

    def get_credits(self, response):
        fr = response.css("li.credit-info")
        if fr:
            fr_credit_val = fr.css("span.credit-val::text").get()
            return fr_credit_val if fr_credit_val else "None"
        return "None"

    def get_outcomes(self, response):
        fr = response.css("li.catalog-outcome")
        if fr:
            return [li.css("::text").get() for li in fr]
        return "None"
