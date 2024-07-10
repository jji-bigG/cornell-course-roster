import scrapy
import json


class AsStudiesDetailsSpider(scrapy.Spider):
    name = "as_studies_details"
    allowed_domains = ["as.cornell.edu"]

    # start_urls = [
    #     "https://as.cornell.edu/major_minor_gradfield/africana-studies",
    # ]

    def start_requests(self):
        with open("as-studies-list.json") as f:
            studies = json.load(f)
        for study in studies:
            yield scrapy.Request(
                url=study["url"], callback=self.parse, meta={"title": study["title"]}
            )

    def parse(self, response):
        title = response.css("h1.title::text").get().strip()
        content = response.css("div.content")
        sidebar = response.css("div.sidebar")

        details = {
            "title": title,
            "url": response.url,
            "description": content.css("p::text").get(default="").strip(),
            "requirements": self.extract_requirements(response),
            "sample_classes": self.extract_sample_classes(content),
            "outcomes": self.extract_outcomes(content),
            "sidebar": self.extract_sidebar(sidebar),
        }

        yield details

    def extract_requirements(self, response):
        requirements = response.css(
            "h2#requirments + h3 + p::text, h2#requirments + h3 + p + p::text, h2#requirments + h3 + p + p + p::text, h2#requirments + h3 + ul li::text, h2#requirments + h3 + p + ul li::text, h2#requirments + h3 + p + p + ul li::text, h2#requirments + h3 + p + p + p + ul li::text, h2#requirments + p::text, h2#requirments + p + p::text, h2#requirments + p + p + p::text, h2#requirments + p + p + p + p::text, h2#requirments + ul li::text, h2#requirments + ul + ul li::text"
        ).getall()
        return requirements

    def extract_sample_classes(self, content):
        return content.css("h2#classes + div ul li::text").getall()

    def extract_outcomes(self, content):
        outcomes = {
            "description": content.css("h2#outcomes + p::text").getall(),
            "graduate_school": content.css(
                "h3:contains('Graduate school') + p::text"
            ).getall(),
            "employment": content.css("h3:contains('Employment') + p::text").getall(),
            "where_graduates_work": self.extract_graduates_work(content),
        }
        return outcomes

    def extract_graduates_work(self, content):
        rows = content.css("table.as-table tbody tr")
        graduates_work = []
        for row in rows:
            employer = row.css("td:nth-child(1)::text").get()
            job_title = row.css("td:nth-child(2)::text").get()
            graduates_work.append({"employer": employer, "job_title": job_title})
        return graduates_work

    def extract_sidebar(self, sidebar):
        return {
            "degree_levels": sidebar.css("div.levels span.level::text").getall(),
            "image_url": sidebar.css("figure img::attr(src)").get(),
            "related_links": sidebar.css("ul li a::attr(href)").getall(),
            "related_articles": self.extract_related_articles(sidebar),
            "associated_interests": sidebar.xpath(
                ".//h3[contains(text(), 'Associated interests')]/following-sibling::ul[1]/li/text()"
            ).getall(),
            "related_disciplines": sidebar.xpath(
                ".//h3[contains(text(), 'Related disciplines')]/following-sibling::ul[1]/li/text()"
            ).getall(),
        }

    def extract_related_articles(self, sidebar):
        articles = sidebar.css("div.card--article")
        related_articles = []
        for article in articles:
            title = article.css("h2.card__title a::text").get()
            url = article.css("h2.card__title a::attr(href)").get()
            date = article.css("span.card__date time::attr(datetime)").get()
            related_articles.append({"title": title, "url": url, "date": date})
        return related_articles
