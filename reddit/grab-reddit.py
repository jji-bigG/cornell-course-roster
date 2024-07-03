# scrap reddit data from r/cornell

import praw
import pandas as pd

import json
import sqlite3
import os

current_dir = os.path.dirname(os.path.realpath(__file__))

api_keys = json.loads(open(os.path.join(current_dir, "reddit_key.json")).read())


def write_sql(post_data, comments_df, cursor):
    res = cursor.execute(
        """
        INSERT INTO reddit_posts (subreddit, title, url, author, score, num_comments, created_utc, selftext, permalink)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        post_data,
    )
    comments_df["post_id"] = res.lastrowid
    comments_df.to_sql("reddit_comments", conn, if_exists="append", index=False)
    conn.commit()


def get_subreddit_data(submissions, cursor=None):
    topics_dict = {
        "title": [],
        "score": [],
        "id": [],
        "url": [],
        "num_comments": [],
        "created": [],
        "body": [],
    }
    for submission in submissions:
        topics_dict["title"].append(submission.title)
        topics_dict["score"].append(submission.score)
        topics_dict["id"].append(submission.id)
        topics_dict["url"].append(submission.url)
        topics_dict["num_comments"].append(submission.num_comments)
        topics_dict["created"].append(submission.created)
        topics_dict["body"].append(submission.selftext)
        # print(f"submission from {submission.author}: {submission.title}")
        # print(submission.comments)
        comments_df = pd.DataFrame(
            columns=[
                "body",
                "score",
                "username",
                "user_id",
                "created_utc",
                "permalink",
                "subreddit",
                "parent_id",
            ],
            index=None,
        )
        # submission.comments.replace_more(limit=32)
        for comment in submission.comments.list():
            if isinstance(comment, praw.models.MoreComments):
                print(f"more comments: {comment.body}")
                continue
            # topics_dict["comment"].append(comment.body)
            # else: continue
            # print(f"comment ({comment.score}) from {comment.author}: {comment.body}\n")

            if comment.author is None:
                id = "[deleted]"
                name = "[deleted]"
            elif (
                hasattr(comment.author, "is_suspended") and comment.author.is_suspended
            ):
                id = "[suspended]"
            else:
                id = comment.author.id
                name = comment.author.name

            comments_df.loc[len(comments_df)] = [
                comment.body,
                comment.score,
                name,
                id,
                comment.created_utc,
                comment.permalink,
                "cornell",
                comment.parent_id,
            ]
            comments_df.sort_values(by="score", ascending=False)
        topics_dict["comments"] = comments_df.to_json(orient="split")

        if cursor is not None:
            write_sql(
                # subreddit TEXT,
                # title TEXT,
                # url TEXT,
                # author TEXT,
                # score INTEGER,
                # num_comments INTEGER,
                # created_utc INTEGER,
                # selftext TEXT,
                # permalink TEXT,
                (
                    "cornell",
                    submission.title,
                    submission.url,
                    submission.author.name,
                    submission.score,
                    submission.num_comments,
                    submission.created_utc,
                    submission.selftext,
                    submission.permalink,
                ),
                comments_df,
                cursor,
            )

    return topics_dict


def redditData(subreddit: str, search: str, limit: int, cursor=None):
    reddit = praw.Reddit(
        client_id=api_keys["client_id"],
        client_secret=api_keys["client_secret"],
        user_agent="jji-bigg",
    )
    subreddit = reddit.subreddit("cornell")

    return pd.DataFrame(
        get_subreddit_data(subreddit.search(search, limit=limit), cursor=cursor)
    )


def generateCSVForReddit(
    search, limit: int, subreddit: str = "cornell", fname: str = None, cursor=None
):
    if fname is None:
        fname = f"reddit/data/{search}.csv"
    data = redditData(subreddit, search, limit, cursor=cursor)
    data.to_csv(fname, index=False)


def init_db(
    db_path="roster_reviews.sqlite.db",
    schema_path=os.path.join(current_dir, "schema.sql"),
):
    conn = sqlite3.connect(db_path)
    with open(schema_path, "r") as f:
        conn.executescript(f.read())
    conn.commit()
    return conn


conn = init_db()
cursor = conn.cursor()

courses = cursor.execute("SELECT DISTINCT name FROM courses").fetchall()
# print(courses)

for course in courses:
    generateCSVForReddit(course[0], 6, cursor=cursor)
    print(f"reddit: done with {course}")

professors = cursor.execute("SELECT DISTINCT name FROM courses").fetchall()

for professor in professors:
    generateCSVForReddit(professor[0], 6, cursor=cursor)
    print(f"reddit: done with {professor}")
