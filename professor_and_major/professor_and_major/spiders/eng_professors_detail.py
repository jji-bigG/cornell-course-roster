from typing import Iterable
import scrapy
import json


class EngProfessorsDetailSpider(scrapy.Spider):
    name = "eng_professors_detail"
    
    def start_requests(self) -> Iterable[scrapy.Request]:
        with open("prof-list.json") as f:
            profs = json.load(f)
        for prof in profs:
            yield scrapy.Request(url=prof["url"], callback=self.parse)

    def parse(self, response):
        # Extracting professor's name
        prof_name = response.css('div.columns.small-12.medium-8.small-order-2.medium-order-3 h1#nf-1561 span::text').get()

        # Extracting biography
        bio_section = response.css('section.section--faculty-detail.faculty-detail__biography')
        bio = ''
        if bio_section.css('h2#nf-b-1561::text').get() == 'Biography':
            bio = ' '.join(bio_section.css('p::text').getall())

        # Extracting research interests
        research_interests_section = bio_section
        research_interests = []
        if research_interests_section.css('h2#nf-b-1561::text').get() == 'Research Interests':
            research_interests = [(a.css('::text').get(), a.css('::attr(href)').get()) for a in research_interests_section.css('ul li a')]
            research_interests.extend(research_interests_section.css('p::text').getall())

        # Extracting selected publications
        selected_publications_section = response.css('section.section--faculty-detail.faculty-detail__publications')
        selected_publications = selected_publications_section.css('ul li').getall()

        # Extracting awards
        awards_section = response.css('section.section--faculty-detail.faculty-detail__awards')
        awards = awards_section.css('ul li::text').getall()

        # Extracting education
        education_section = response.css('section.section--faculty-detail.faculty-detail__education')
        education = education_section.css('ul li::text').getall()

        # Extracting in the news articles
        in_the_news_articles = response.css('article').getall()

        # Extracting related links
        related_links_section = response.css('section.section--faculty-detail.section--field_faculty_related_links')
        related_links = [(a.css('::text').get(), a.css('::attr(href)').get()) for a in related_links_section.css('ul li a')]

        # Extracting teaching interests
        teaching_interests_section = response.css('section.section--faculty-detail.faculty-detail__teaching-interests')
        teaching_interests = teaching_interests_section.css('p::text').getall()

        # Extracting websites
        websites_section = response.css('section.section--faculty-detail.faculty-detail__websites')
        websites = [(a.css('::text').get(), a.css('::attr(href)').get()) for a in websites_section.css('ul li a')]

        # Storing the extracted data
        yield {
            'prof_name': prof_name,
            'bio': bio,
            'research_interests': research_interests,
            'selected_publications': selected_publications,
            'awards': awards,
            'education': education,
            'in_the_news': in_the_news_articles,
            'related_links': related_links,
            'teaching_interests': teaching_interests,
            'websites': websites,
        }