import os
import sqlite3
import json
import praw
import pandas as pd
from concurrent.futures import ThreadPoolExecutor

current_dir = os.path.dirname(os.path.realpath(__file__))

api_keys = json.loads(open(os.path.join(current_dir, "reddit_key.json")).read())


def write_sql(post_data, comments_df, conn):
    cursor = conn.cursor()
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


def get_subreddit_data(submissions, conn=None):
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
        for comment in submission.comments.list():
            if isinstance(comment, praw.models.MoreComments):
                continue

            if comment.author is None:
                id = "[deleted]"
                name = "[deleted]"
            elif (
                hasattr(comment.author, "is_suspended") and comment.author.is_suspended
            ):
                id = "[suspended]"
                name = "[suspended]"
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

        if conn is not None:
            write_sql(
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
                conn,
            )

    return topics_dict


def redditData(subreddit: str, search: str, limit: int, conn=None):
    reddit = praw.Reddit(
        client_id=api_keys["client_id"],
        client_secret=api_keys["client_secret"],
        user_agent="jji-bigg",
    )
    subreddit = reddit.subreddit("cornell")

    return pd.DataFrame(
        get_subreddit_data(subreddit.search(search, limit=limit), conn=conn)
    )


def generateCSVForReddit(
    search,
    limit: int,
    db_path="roster_reviews.sqlite.db",
    subreddit: str = "cornell",
    fname: str = None,
):
    if fname is None:
        fname = f"reddit/data/{search}.csv"
    if os.path.exists(fname):
        print(f"File {fname} already exists. Skipping.")
        return
    try:
        conn = sqlite3.connect(db_path, check_same_thread=False)
        data = redditData(subreddit, search, limit, conn=conn)
        data.to_csv(fname, index=False)
        conn.close()
    except Exception as e:
        print(f"Error: {e}")
        return None


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


def main():
    db_path = "roster_reviews.sqlite.db"
    conn = init_db(db_path)
    cursor = conn.cursor()

    NUM_TOP_POSTS = 10

    courses = set(
        sorted(
            [
                c[0]
                for c in cursor.execute("SELECT DISTINCT name FROM courses").fetchall()
            ],
            key=lambda x: len(x[0]),
        )
    )

    professors = set(
        sorted(
            [
                p[0]
                for p in cursor.execute(
                    "SELECT DISTINCT instructor FROM courses"
                ).fetchall()
            ],
            key=lambda x: len(x[0]),
        )
    )

    conn.close()

    with ThreadPoolExecutor(max_workers=1) as executor:
        professor_futures = [
            executor.submit(generateCSVForReddit, professor, NUM_TOP_POSTS, db_path)
            for professor in professors
        ]
        course_futures = [
            executor.submit(generateCSVForReddit, course, NUM_TOP_POSTS, db_path)
            for course in courses
        ]

        for future in professor_futures + course_futures:
            future.result()


if __name__ == "__main__":
    main()
