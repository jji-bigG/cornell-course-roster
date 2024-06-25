# scrap reddit data from r/cornell

import praw
import pandas as pd
import datetime as dt
import os
import csv

courses = [
    "cs 4780",
    "cs 4820",
    "cs 4320",
]


def get_subreddit_data(submissions):
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
            columns=["comment", "score", "username", "user_id", "created"], index=None
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
                comment.created,
            ]
            comments_df.sort_values(by="score", ascending=False)
        topics_dict["comments"] = comments_df.to_json(orient="split")

    return topics_dict


def redditData(subreddit: str, search: str, limit: int):
    reddit = praw.Reddit(
        client_id="jOKiM6A9lyq-0apUyNwQNw",
        client_secret="sgRFQtP7vzOjUcR16vAjGvUeTw0Q7A",
        user_agent="jji-bigg",
    )
    subreddit = reddit.subreddit("cornell")

    return pd.DataFrame(get_subreddit_data(subreddit.search(search, limit=limit)))


def generateCSVForReddit(
    search, limit: int, subreddit: str = "cornell", fname: str = None
):
    if fname is None:
        fname = f"reddit/{search}.csv"
    data = redditData(subreddit, search, limit)
    data.to_csv(fname, index=False)


for course in courses:
    generateCSVForReddit(course, 6)
    print(f"done with {course}")
