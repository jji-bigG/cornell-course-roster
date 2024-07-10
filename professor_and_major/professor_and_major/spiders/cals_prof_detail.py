import scrapy
import json


class CalsProfDetailSpider(scrapy.Spider):
    name = "cals_prof_detail"
    allowed_domains = ["cals.cornell.edu"]

    # start_urls = [
    #     "https://cals.cornell.edu/laura-elisa-acuna-maldonado",
    #     "https://cals.cornell.edu/arthur-m-agnello",
    #     "https://cals.cornell.edu/diane-bailey",
    #     "https://cals.cornell.edu/chris-barrett",
    # ]

    def start_requests(self):
        with open("cals-prof-list.json") as f:
            profs = json.load(f)
        for prof in profs:
            yield scrapy.Request(url=prof["profile_url"], callback=self.parse)

    def parse(self, response):
        name = response.css("h1.field--type-name::text").get()
        if name:
            name = name.strip()

        position = response.css(
            "p.subhead.paragraph--type--faculty-department::text"
        ).get()
        if position:
            position = position.strip()

        summary = response.css(
            "div.field.field--type-text-with-summary p::text"
        ).getall()

        interests = response.css("div.field.field--type-string p::text").getall()

        edu_awards_tags = response.css("div.field.field--type-text-long")
        edu_and_awards = {}
        for tag in edu_awards_tags:
            title = tag.css("h3::text").get()
            if title:
                title = title.strip()
            content = tag.css("p::text, ul li").getall()
            if content:
                content = [c.strip() for c in content]
            edu_and_awards[title] = content

        courses_taught_elements = response.css(
            "div.clearfix.text-formatted.field--type-text-long.field--label-above div.field__item ul li"
        )
        courses_taught = [
            course.xpath("string()").get().strip() for course in courses_taught_elements
        ]

        news_items = []
        for news in response.css("div.node--type-article.node--view-mode-card-small"):
            image_url = news.css("div.field--type-image img::attr(src)").get()
            if image_url:
                image_url = response.urljoin(image_url)

            title = news.css("div.flexbox-full-width a::text").get()
            if title:
                title = title.strip()

            date = news.css("time.datetime::text").get()
            if date:
                date = date.strip()

            news_summary = news.css("div.card-copy p::text").get()
            if news_summary:
                news_summary = news_summary.strip()

            tags = news.css("ul.card-tags li.field__item::text").getall()

            news_items.append(
                {
                    "image_url": image_url,
                    "title": title,
                    "date": date,
                    "news_summary": news_summary,
                    "tags": tags,
                }
            )

        yield {
            "name": name,
            "position": position,
            "summary": summary,
            "interests": interests,
            "edu_and_awards": edu_and_awards,
            "publications": self.parse_publications(response),
            "courses_taught": courses_taught,
            "news_items": news_items,
            "contacts": self.parse_contacts(response),
        }

    def parse_publications(self, response):
        # Initialize the dictionary to store publications
        publications = {}

        # Locate the h4 tag with text "Selected Publications"
        selected_publications_h4 = response.xpath(
            '//h4[contains(text(), "Selected Publications")]'
        )

        # Check if the h4 tag was found
        if selected_publications_h4:
            # Find sibling div tags at the same level as the h4 tag
            sibling_divs = selected_publications_h4.xpath(
                'following-sibling::div[@class="panel panel-default"]'
            )

            # Iterate over each sibling div
            for div in sibling_divs:
                # Extract the panel title
                panel_title = (
                    div.xpath(
                        './/button[@class="collapsed data-gtm-openAccordion" or @class="data-gtm-openAccordion collapsed"]/text()'
                    )
                    .get()
                    .strip()
                )

                # Extract the publication list items
                publication_items = div.xpath(
                    './/div[@class="panel-body"]//ul/li'
                ).extract()

                # Clean and structure the publication items
                publications[panel_title] = []
                for item in publication_items:
                    # Extract text content
                    text = " ".join(item.xpath(".//text()").getall()).strip()

                    # Extract href if exists
                    href = item.xpath(".//a/@href").get()

                    # Create a JSON object for the publication item
                    publication_json = {"text": text, "href": href}

                    # Append the JSON object to the list for this panel
                    publications[panel_title].append(publication_json)

        return publications

    def parse_contacts(self, response):
        contact_info = {}

        # Extract contact information
        contact_section = response.css("div.bio-card")
        location_tag = contact_section.css("p::text").getall()
        contact_info["location"] = "".join(location_tag).strip()
        email_tag = contact_section.css("p.field--type-email").get()
        contact_info["email"] = email_tag.replace("mailto:", "") if email_tag else None
        contact_info["phone"] = contact_section.css(
            "p.field--type-telephone a::text"
        ).get()

        # Extracting links in the contact section
        contact_info["links"] = []
        links = contact_section.css(
            "ul.field--type-entity-reference-revisions li.field__item a"
        )
        for link in links:
            contact_info["links"].append(
                {
                    "title": link.css("::text").get(),
                    "url": link.css("::attr(href)").get(),
                }
            )

        return contact_info
