# scrap reddit data from r/cornell

import praw
import pandas as pd

import json
import sqlite3
import os

from concurrent.futures import ThreadPoolExecutor, as_completed

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
    search,
    limit: int,
    subreddit: str = "cornell",
    fname: str = None,
    cursor=None,
):
    if fname is None:
        fname = f"reddit/data/{search}.csv"
    if os.path.exists(fname):
        print(f"File {fname} already exists. Skipping.")
        return
    try:
        data = redditData(subreddit, search, limit, cursor=cursor)
        data.to_csv(fname, index=False)
    except Exception as e:
        print(f"Error: {e}")
        return None


# Initialize the database
def init_db(
    db_path="roster_reviews.sqlite.db",
    schema_path=os.path.join(current_dir, "schema.sql"),
    run_schema=False,
):
    conn = sqlite3.connect(db_path)
    if run_schema:
        with open(schema_path, "r") as f:
            conn.executescript(f.read())
        conn.commit()
    return conn


conn = init_db()
cursor = conn.cursor()

NUM_PARALLEL_TASKS = 6
NUM_TOP_POSTS = 10

courses = set(
    sorted(
        [c[0] for c in cursor.execute("SELECT DISTINCT name FROM courses").fetchall()],
        key=lambda x: len(x[0]),
    )
)
# print(courses)

for course in courses:
    generateCSVForReddit(course, NUM_TOP_POSTS, cursor=cursor)
    print(f"reddit: done with course: {course}")
# with ThreadPoolExecutor(max_workers=NUM_PARALLEL_TASKS) as executor:
#     for course in courses:
#         executor.submit(generateCSVForReddit, course, NUM_TOP_POSTS, cursor=cursor)
#         print(f"reddit: done with course: {course}")

professors = set(
    sorted(
        [
            p[0]
            for p in cursor.execute(
                "SELECT DISTINCT instructors FROM courses"
            ).fetchall()
        ],
        key=lambda x: len(x[0]),
    )
)

for professor in professors:
    generateCSVForReddit(professor, NUM_TOP_POSTS, cursor=cursor)
    print(f"reddit: done with professor: {professor}")

# with ThreadPoolExecutor(max_workers=NUM_PARALLEL_TASKS) as executor:
#     for professor in professors:
#         executor.submit(generateCSVForReddit, professor, NUM_TOP_POSTS, cursor=cursor)
# print(f"reddit: done with professor: {professor}")
