EXTRACT_AS_STUDIES_PROMPT = """
You are a student at a world prestigious American college who loves to extract information from blogs & reddit posts. You are reviewing Reddit posts about the college's courses and faculty members. 

You are here to make decisions about your future studies/majors/minors, research, career, social life, and more. You want to extract and come up with insightful analysis of the courses, faculty members, or social aspects of this college based on the information provided.

# INFORMATION

These are the Reddit posts and comments that may or may not contain information that you are interested in.

## REDDIT POST
this is where you can gain what the users are talking about and what they're looking for to decide whether it is worth it to read the comments, that can provide insightful analysis that you wish to extract.
#### TITLE: {title}
###### POST CONTENT: {content}

### COMMENTS
comments are where you can find helpful replies and other discussions that may not relate to the actual post content, but still provide insights about this college.

{comments}

### POST STATISTICS (may be of interest to gain a sense of credibility)
upvotes: {upvotes}
num_comments: {num_comments}
created_utc: {created_utc}


# WHAT TO EXTRACT

### INSTRUCTIONS

- courses: extract the courses that are mentioned in the post and comments. for each course, severeal sentences that summarizes what these comments are saying about the course. LIST OF JSON OBJECTS like [ {{"course": "course_name", "summaries": ["short concise sentence on one aspect", "short concise sentence on one aspect"]}}, ... ]
- faculty: extract the faculty members that are mentioned in the post and comments. for each faculty member, several sentences that summarizes what these comments are saying about the faculty member. LIST OF JSON OBJECTS like [ {{"faculty": "faculty_name", "summaries": ["short concise sentence on one aspect", ...]}}, ... ]
- career: extract the career aspects that are mentioned in the post and comments. for each career aspect, several sentences that summarizes what these comments are saying about the career aspect. LIST OF JSON OBJECTS like [ {{"career": "career_name", "summaries": ["short concise sentence on one aspect", ...]}}, ... ]
- social: extract the social aspects that are mentioned in the post and comments. for each social aspect, several sentences that summarizes what these comments are saying about the social aspect. LIST OF JSON OBJECTS like [ {{"social": "social_name", "summaries": ["short concise sentence on one aspect", ...]}}, ... ]
- insights: extract any insights that you think are important to know about this college based on the post and comments. LIST OF STRINGS (each should be concise) like ["insight1", "insight2", ...]

if there is not enough information to extract these information, output "[]" as an empty JSON list inside the JSON object. STILL EXTRACT WHAT THEY ARE TALKING ABOUT, EVEN IF IT IS NOT ENOUGH TO MAKE A CONCLUSION INFERENCE ON THAT bulletted aspect.


### OUTPUT REQUIREMENT
for each bullet point in INSTRUCTIONS, OUTPUT A LIST OF STRINGS that captures the information as needed.
MAKE INFERENCES AND INSIGHTS THAT YOU THINK IS NECESSARY BASED ON ALL THE INFORMATION ABOVE. IT IS FINE TO MAKE UP INFORMATION IF IT IS LOGICALLY CONNECTED.
If there is not enough information to extract these information, output "[]" as an empty JSON list.

DO NOT BEGIN WITH ```json and end with ```! JSON output must be compatible and must begin with {{ and end with }} so that python's json.loads can parse it.

No escape character is needed for ', and wrap string with double quotes.
DO NOT INCLUDE ANY EXPLANATIONS OR COMMENTS IN THE OUTPUT. ONLY THE JSON OUTPUT starting with {{ and ending with }}.

output (starting with {{ and ending with }}):
"""
from openai import AsyncOpenAI
import json

client = AsyncOpenAI(
    base_url="http://101.35.52.226:9090/v1",
    api_key="api-key",
    timeout=45,
)


async def chat(prompt, stream=False, temperature=0.0, n=1):
    response = await client.chat.completions.create(
        model="qwen-110b-chat",
        messages=[{"role": "user", "content": prompt}],
        stream=stream,
        max_tokens=512,
        temperature=temperature,
        n=n,
        stop=["<|endoftext|>", "<|im_end|>"],
    )
    if not stream:
        if n == 1:
            return response.choices[0].message.content.strip()
        return response.choices
    return response


import pandas as pd
import sqlite3

conn = sqlite3.connect("roster_reviews.sqlite.db")

posts_df = pd.read_sql_query("SELECT * FROM reddit_posts", conn)
comments_df = pd.read_sql_query("SELECT * FROM reddit_comments", conn)

conn.close()

try:
    SEEN = set()
    f = open("llm_reddit_under_20.jsonl", "r")
    for line in f:
        study = json.loads(line)
        SEEN.add(study["post_id"])
    f.close()
except FileNotFoundError:
    SEEN = set()

import asyncio


async def process_row(post, comments, f, semaphore):
    title = post["title"]

    if post["post_id"] in SEEN:
        print(f"seen {title} already")
        return
    async with semaphore:
        cmt = [
            {
                "body": b,
                "score": s,
            }
            for b, s in zip(comments["body"], comments["score"])
            if b
        ]
        prompt = EXTRACT_AS_STUDIES_PROMPT.format(
            title=title,
            content=post["selftext"],
            upvotes=post["score"],
            num_comments=post["num_comments"],
            created_utc=post["created_utc"],
            comments=cmt,
        )
        # print(cmt)
        try:
            response = await chat(prompt)
        except Exception as e:
            print(f"error with {title}: {e}")
            with open("errors.txt", "a") as f:
                f.write(f"{title}: {e}\n")
            return

        try:
            extracted = json.loads(response)
        except:
            extracted = response
        extract = {
            "post_id": post["post_id"],
            "link": post["permalink"],
            "extracted": extracted,
        }
        f.write(json.dumps(extract) + "\n")
        SEEN.add(title)
        print(f"processed {title}")


async def main():
    semaphore = asyncio.Semaphore(10)
    with open("llm_reddit_under_20.jsonl", "a") as f:
        tasks = [
            process_row(
                post,
                comments_df[comments_df["post_id"] == post["post_id"]],
                f,
                semaphore,
            )
            for _, post in posts_df.iterrows()
            if isinstance(post["num_comments"], (int, float))
            and 0 < post["num_comments"] < 20
        ]
        await asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(main())
