import scrapy
import json


class CalsProfDetailSpider(scrapy.Spider):
    name = "cals_prof_detail"
    allowed_domains = ["cals.cornell.edu"]

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

        summary = "\n".join(
            response.css(
                "div.clearfix.text-formatted.field--type-text-with-summary p::text"
            ).getall()
        ).strip()

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

            title = news.css("a#card-title-59639::text").get()
            if title:
                title = title.strip()

            date = news.css("time.datetime::text").get()
            if date:
                date = date.strip()

            summary = news.css("div.card-copy p::text").get()
            if summary:
                summary = summary.strip()

            tags = news.css("ul.card-tags li.field__item::text").getall()

            news_items.append(
                {
                    "image_url": image_url,
                    "title": title,
                    "date": date,
                    "summary": summary,
                    "tags": tags,
                }
            )

        yield {
            "name": name,
            "position": position,
            "summary": summary,
            "courses_taught": courses_taught,
            "news_items": news_items,
        }
