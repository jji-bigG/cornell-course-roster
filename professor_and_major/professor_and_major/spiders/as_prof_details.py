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

        # Extract paragraphs under each h1 to h5 tag
        content = {}
        headers = response.css("h1, h2, h3, h4, h5")
        for header in headers:
            header_text = header.css("::text").get().strip()
            if header_text:
                content[header_text] = []
                for element in header.xpath("following-sibling::*"):
                    if element.root.tag in {"h1", "h2", "h3", "h4", "h5"}:
                        break
                    elif element.root.tag == "p":
                        content[header_text].append(element.css("::text").get())
                    elif element.root.tag == "ul":
                        for li in element.css("li"):
                            link = li.css("a::attr(href)").get()
                            text = li.css("::text").get().strip()
                            if link:
                                content[header_text].append(f"{text} ({link.strip()})")
                            else:
                                content[header_text].append(text)

        # remove the duplicated content from the first and second and so on h3 tags
        prev_key = None
        for key in content:
            if prev_key:
                content[prev_key] = list(set(content[prev_key]) - set(content[key]))
            prev_key = key

        # Extract "In the news" items
        news_items = []
        for item in response.css('h2:contains("In the news") + ul li a'):
            news_text = item.css("::text").get()
            news_href = item.css("::attr(href)").get()
            news_items.append({"text": news_text, "href": response.urljoin(news_href)})

        # Extract sidebar attributes
        sidebar_image_url = response.css("div.sidebar img::attr(src)").get()

        # Extract location, email, and phone
        contact_info = response.css("div.person__contact").get()
        email = response.css("div.person__contact a::text").get()
        location, phone = None, None

        if contact_info:
            parts = contact_info.split("<br>")
            for i, part in enumerate(parts):
                if "mailto:" in part:
                    if i > 0:
                        location = parts[i - 1].split(">")[1].strip()
                    if i < len(parts) - 1:
                        phone = parts[i + 1].strip()

        education_section = response.xpath(
            "//h3[contains(text(),'Education')]/following-sibling::ul[1]/li"
        )
        education = [li.css("::text").get() for li in education_section]
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
            "location": location.strip() if location else None,
            "email": email.strip() if email else None,
            "phone": phone.strip() if phone else None,
            "education": [edu.strip() for edu in education] if education else None,
            "departments_programs": (
                [dp.strip() for dp in departments_programs]
                if departments_programs
                else None
            ),
            "links": [link.strip() for link in links] if links else None,
            "content": content if content else None,
            "news_items": news_items if news_items else None,
        }
