# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import json


class ProfessorAndMajorPipeline:
    def process_item(self, item, spider):
        return item

    # def open_spider(self, spider):
    #     self.file = open("links.json", "w")
    #     self.links = []

    # def close_spider(self, spider):
    #     json.dump(self.links, self.file)
    #     self.file.close()

    # def process_item(self, item, spider):
    #     self.links.append(item["link"])
    #     return item
