import scrapy
import json

from scrapy.http import Response


class AsProfessorsDetailSpider(scrapy.Spider):
    name = "as_professors_detail"

    def start_requests(self):
        with open("as-prof-list.json") as f:
            profs = json.load(f)
        for prof in profs:
            yield scrapy.Request(
                url=prof["link"],
                callback=self.parse,
                meta={
                    "name": prof.get("name"),
                    "title": prof.get("title"),
                    "departments": prof.get("departments"),
                    "image_url": prof.get("image_url"),
                },
            )

    def parse(self, response: Response):
        # Extract additional details from the professor's page
        name = response.meta["name"]
        title = response.meta["title"]
        departments = response.meta["departments"]
        image_url = response.meta["image_url"]

        # Extract paragraphs under each h3 tag
        content = {}
        for section in response.css("div.content h3"):
            header = section.css("::text").get()
            paragraphs = section.xpath("following-sibling::p").css("::text").getall()
            content[header] = paragraphs

        # Extract sidebar attributes
        sidebar_image_url = response.css("div.sidebar img::attr(src)").get()
        email = response.css("div.person__contact a::text").get()
        phone = response.css("div.person__contact::text").re_first(r"\d{3}/\d{3}-\d{4}")
        education = response.css('div.sidebar h3:contains("Education") + p::text').get()
        departments_programs = response.css(
            'div.sidebar h3:contains("Departments and programs") + ul li::text'
        ).getall()
        links = response.css(
            'div.sidebar h3:contains("Links") + ul li a::attr(href)'
        ).getall()

        yield {
            "name": name.strip() if name else None,
            "title": title.strip() if title else None,
            "departments": departments.strip() if departments else None,
            "image_url": image_url.strip() if image_url else None,
            "sidebar_image_url": (
                sidebar_image_url.strip() if sidebar_image_url else None
            ),
            "email": email.strip() if email else None,
            "phone": phone.strip() if phone else None,
            "education": education.strip() if education else None,
            "departments_programs": (
                [dp.strip() for dp in departments_programs]
                if departments_programs
                else None
            ),
            "links": [link.strip() for link in links] if links else None,
            "content": content if content else None,
        }
