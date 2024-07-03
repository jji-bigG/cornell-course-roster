# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter


import sqlite3


import sqlite3


class SQLitePipeline:
    def open_spider(self, spider):
        self.conn = sqlite3.connect("courses.db")
        self.cursor = self.conn.cursor()
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS courses (
                id INTEGER PRIMARY KEY,
                semester TEXT,
                subject_name TEXT,
                name TEXT,
                type TEXT,
                section_number TEXT,
                location TEXT,
                days TEXT,
                time TEXT,
                dates TEXT,
                instructor TEXT
            )
        """
        )
        self.conn.commit()

    def close_spider(self, spider):
        self.conn.close()

    def process_item(self, item, spider):
        self.cursor.execute(
            """
            INSERT INTO courses (semester, subject_name, name, type, section_number, location, days, time, dates, instructor)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                item.get("semester"),
                item.get("subject_name"),
                item.get("name"),
                item.get("type"),
                item.get("section_number"),
                item.get("location"),
                item.get("days"),
                item.get("time"),
                item.get("dates"),
                item.get("instructor"),
            ),
        )
        self.conn.commit()
        return item


# class SQLiteStorePipeline:

#     def open_spider(self, spider):
#         self.connection = sqlite3.connect("test.sqlite.db")
#         self.cursor = self.connection.cursor()
#         self.cursor.execute(
#             """
#             CREATE TABLE IF NOT EXISTS course_descriptions (
#                 course_id INTEGER PRIMARY KEY AUTOINCREMENT,
#                 url TEXT,
#                 title TEXT,
#                 description TEXT,
#                 prerequisites TEXT,
#                 when_offered TEXT,
#                 combined_with TEXT,
#                 distribution TEXT,
#                 credits TEXT,
#                 outcomes TEXT
#             )
#         """
#         )
#         self.connection.commit()

#     def close_spider(self, spider):
#         self.connection.close()

#     def process_item(self, item, spider):
#         self.cursor.execute(
#             """
#             INSERT INTO course_descriptions (url, title, description, prerequisites, when_offered, combined_with, distribution, credits, outcomes) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
#         """,
#             (
#                 item.get("url"),
#                 item.get("title"),
#                 item.get("description"),
#                 item.get("prerequisites"),
#                 item.get("when_offered"),
#                 item.get("combined_with"),
#                 item.get("distribution"),
#                 item.get("credits"),
#                 str(item.get("outcomes")),
#             ),
#         )
#         self.connection.commit()
#         return item


class RosterCrawlerScrapyPipeline:
    def process_item(self, item, spider):
        return item
