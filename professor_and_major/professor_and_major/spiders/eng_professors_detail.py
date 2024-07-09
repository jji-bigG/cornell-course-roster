import scrapy
import json


class EngProfessorsDetailSpider(scrapy.Spider):
    name = "eng_professors_detail"

    def start_requests(self):
        with open("eng-prof-list.json") as f:
            profs = json.load(f)
        for prof in profs:
            yield scrapy.Request(url=prof["url"], callback=self.parse)

    def parse(self, response):
        # Extracting professor's name
        prof_name = response.css(
            "div.columns.small-12.medium-8.small-order-2.medium-order-3 h1 span::text"
        ).get()

        # Extracting biography
        bio_section = response.css(
            "section.section--faculty-detail.faculty-detail__biography"
        )
        bio = ""
        if bio_section.css("h2::text").get() == "Biography":
            bio = " ".join(bio_section.css("p::text").getall())

        # Extracting research interests
        research_interests_section = response.xpath(
            "(//section[@class='section--faculty-detail faculty-detail__biography'])[2]"
        )
        research_interests = []
        if (
            research_interests_section
            and research_interests_section.css("h2::text").get() == "Research Interests"
        ):
            research_interests = [
                {"text": a.css("::text").get(), "link": a.css("::attr(href)").get()}
                for a in research_interests_section.css("ul li a")
            ]
            research_interests.extend(
                research_interests_section.css("p::text").getall()
            )

        # Extracting selected publications
        selected_publications_section = response.css(
            "section.section--faculty-detail.faculty-detail__publications"
        )
        selected_publications = selected_publications_section.css("ul li")

        publications = []
        for publication in selected_publications:
            publication_dict = {}
            publication_dict["text"] = " ".join(publication.css("*::text").getall())
            publication_dict["hyperlink"] = publication.css("a::attr(href)").get()
            publications.append(publication_dict)

        # Extracting awards
        awards_section = response.css(
            "section.section--faculty-detail.faculty-detail__awards"
        )
        awards = awards_section.css("ul li::text").getall()

        # Extracting education
        education_section = response.css(
            "section.section--faculty-detail.faculty-detail__education"
        )
        education = []
        if education_section:
            education = education_section.css("p::text").getall()

        # Extracting in the news articles
        in_the_news_articles = response.css("article")

        articles = []
        for article in in_the_news_articles:
            article_dict = {}
            article_dict["link"] = article.css("a::attr(href)").get()
            article_dict["title"] = article.css("h3 a span::text").get()
            article_dict["image_url"] = article.css(
                ".listing-small__img a img::attr(src)"
            ).get()
            article_dict["date"] = article.css(
                ".listing-small__text__date time::attr(datetime)"
            ).get()
            article_dict["subtitle"] = (
                article.css(".listing-small__text__summary p::text").get().strip()
            )

            articles.append(article_dict)

        # Extracting related links
        related_links_section = response.css(
            "section.section--faculty-detail.section--field_faculty_related_links"
        )
        related_links = [
            (a.css("::text").get(), a.css("::attr(href)").get())
            for a in related_links_section.css("ul li a")
        ]

        # Extracting teaching interests
        teaching_interests_section = response.css(
            "section.section--faculty-detail.faculty-detail__teaching-interests"
        )
        teaching_interests = teaching_interests_section.css("p::text").getall()

        # Extracting websites
        websites_section = response.css(
            "section.section--faculty-detail.faculty-detail__websites"
        )
        websites = [
            (a.css("::text").get(), a.css("::attr(href)").get())
            for a in websites_section.css("ul li a")
        ]

        # Storing the extracted data
        yield {
            "prof_name": prof_name,
            "bio": bio,
            "research_interests": research_interests,
            "selected_publications": publications,  # fixed to use `publications` list
            "awards": awards,
            "education": education,
            "in_the_news": articles,  # fixed to use `articles` list
            "related_links": related_links,
            "teaching_interests": teaching_interests,
            "websites": websites,
        }
