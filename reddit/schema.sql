DROP TABLE IF EXISTS reddit_posts;
DROP TABLE IF EXISTS reddit_comments;

CREATE TABLE IF NOT EXISTS reddit_posts (
    post_id INTEGER PRIMARY KEY AUTOINCREMENT,
    subreddit TEXT,
    title TEXT,
    url TEXT,
    author TEXT,
    score INTEGER,
    num_comments INTEGER,
    created_utc INTEGER,
    selftext TEXT,
    permalink TEXT,
    ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS reddit_comments (
    comment_id INTEGER PRIMARY KEY AUTOINCREMENT,
    post_id INTEGER,
    parent_id INTEGER,
    subreddit TEXT,
    author TEXT,
    score INTEGER,
    created_utc INTEGER,
    body TEXT,
    permalink TEXT,
    ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (post_id) REFERENCES reddit_posts(post_id)
);