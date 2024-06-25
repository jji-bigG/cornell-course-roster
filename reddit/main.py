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
    subreddit = reddit.subreddit(subreddit)
    top_subreddit = subreddit.top(limit=limit)
    topics_dict = {
        "title": [],
        "score": [],
        "id": [],
        "url": [],
        "comms_num": [],
        "created": [],
        "body": [],
    }
    for submission in top_subreddit:
        topics_dict["title"].append(submission.title)
        topics_dict["score"].append(submission.score)
        topics_dict["id"].append(submission.id)
        topics_dict["url"].append(submission.url)
        topics_dict["comms_num"].append(submission.num_comments)
        topics_dict["created"].append(submission.created)
        topics_dict["body"].append(submission.selftext)
    topics_data = pd.DataFrame(topics_dict)
    return topics_data


def generateCSVForReddit(subreddit: str, limit: int):
    if not os.path.exists(subreddit):
        os.makedirs(subreddit)
    redditData(subreddit, limit).to_csv(f"{subreddit}/reddit_data.csv", index=False)


generateCSVForReddit("cornell", 100)
