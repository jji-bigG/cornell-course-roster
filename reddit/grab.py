# scrap reddit data from r/cornell

import praw
import pandas as pd
import datetime as dt
import os
import csv


def redditData(subreddit: str, limit: int):
    reddit = praw.Reddit(
        client_id="jOKiM6A9lyq-0apUyNwQNw",
        client_secret="sgRFQtP7vzOjUcR16vAjGvUeTw0Q7A",
        user_agent="jji-bigg",
    )
    subreddit = reddit.subreddit("cornell")
    top_subreddit = subreddit.top(limit=10)

    topics_dict = {
        "title": [],
        "score": [],
        "id": [],
        "url": [],
        "num_comments": [],
        "created": [],
        "body": [],
        "comments": [],
    }
    for submission in top_subreddit:
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
        c = 0
        for comment in submission.comments.list():
            if isinstance(comment, praw.models.MoreComments):
                print(f"more comments: {comment.count}")
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
            c += 1
            if c % 10 == 0:
                print(f"{c} comments added")

        comments_df.sort_values(by="score", ascending=False)
        topics_dict["comments"].append(comments_df.to_json(orient="split"))
    topics_data = pd.DataFrame(topics_dict)
    return topics_data


def generateCSVForReddit(subreddit: str, limit: int, fname: str = "reddit_data"):
    if not os.path.exists(subreddit):
        os.makedirs(subreddit)
    redditData(subreddit, limit).to_csv(f"reddit/{fname}.csv", index=False)


print("impoted packages")
generateCSVForReddit("cornell", 2)
