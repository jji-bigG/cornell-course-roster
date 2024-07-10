EXTRACTION_COURSE_DESCRIPTION_PROMPT = """
### COURSE TITLE: {title}

### HARD_WRITTEN_PREREQUISITES
{prereqs}

### DESCRIPTION
{description}
IF NO DESCRIPTION IS AVAILABLE, OUTPUT EMPTY LIST. DO NOT MAKE ANY EDUCATED GUESS ON PURELY THE TITLE!

#### said outcomes. may not be provided in the course description.
{outcomes}

### OTHER INPUT INFORMATIONS
may or may not be provided.

combined_with: {combined_with}
distribution_requirements: {distributions}
dates: {dates}


### INSTRUCTION
- perceived_prerequisites: what is actually needed to understand these. NOT the hard-written prerequisites list because that can be misleading and inaccurate, since some concepts are rarely used. output a list of short and concise string capturing everything. short sentences suffice
- contents: what is taught in this course? output a list of short and concise string capturing everything. short sentences suffice
- outcomes: What can you now achieve from taking this class that you previously cannot? How does this class benefit you in terms of academic & career & personal growth goals? How does it fit into the prerequisites chain? output a list of short and concise string capturing everything. short sentences suffice
- hard_written_prerequisites: output as a list of course codes string is fine
- distributions: a list (multiselect) from a predefined set of distributions, rest is ignored.
- combined_with: output a list of course codes from the natural language input.

### OUTPUT REQUIREMENTS
DO NOT MAKE UP ANY INFORMATION. IF THE DESCRIPTION IS NOT AVIALBLE OR IS EMPTY OR SUCH, OUTPUT EMPTY STRINGS OR EMPTY LISTS FOR EVERY FIELD; DO NOT MAKE ANY EDUCATED GUESS ON PURELY THE TITLE!
If there is not enough information to extract these information, output "[]" as an empty JSON list.
JSON output must be compatible and must begin with {{ and end with }} so that python's json.loads can parse it.
No escape character is needed for ', and wrap string with double quotes.

### JSON DATA EXTRACTED (beginning with {{ and ending with }} WITHOUT ```json and ```):
"""

import pandas as pd
import sqlite3
import json

conn = sqlite3.connect("roster_reviews.sqlite.db")

course_descriptions_df = pd.read_sql_query("SELECT * FROM course_descriptions", conn)
courses_df = pd.read_sql_query("SELECT * FROM courses", conn)

# c = conn.cursor()
# res = c.execute("SELECT * FROM course_descriptions").fetchall()

conn.close()

try:
    fr = open("llm_course_descriptions.jsonl", "r")
    seen_courses = set()
    for l in fr.readlines():
        saved_courses = json.loads(l)
        seen_courses.add(saved_courses["course_id"])
    fr.close()
except FileNotFoundError:
    seen_courses = set()

course_descriptions_df = course_descriptions_df.loc[
    ~course_descriptions_df["course_id"].isin(seen_courses)
]
courses_df = courses_df.loc[~courses_df["course_id"].isin(seen_courses)]

from openai import AsyncOpenAI


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


import asyncio


async def process_row(row, f, semaphore):
    async with semaphore:
        title = row["title"]
        course_id = row["course_id"]
        prereqs = row["prerequisites"]
        description = row["description"]
        outcomes = row["outcomes"]
        combined_with = row["combined_with"]
        distributions = row["distribution"]
        dates = courses_df.loc[courses_df["course_id"] == course_id, "dates"].values[0]

        prompt = EXTRACTION_COURSE_DESCRIPTION_PROMPT.format(
            title=title,
            prereqs=prereqs,
            description=description,
            outcomes=outcomes,
            combined_with=combined_with,
            distributions=distributions,
            dates=dates,
        )

        response = json.loads(await chat(prompt))
        print(f"processed {title}")
        f.write(
            json.dumps(
                {
                    "course_id": course_id,
                    "semester": courses_df.loc[
                        courses_df["course_id"] == course_id, "semester"
                    ].values[0],
                    "response": response,
                }
            )
            + "\n"
        )


async def main():
    semaphore = asyncio.Semaphore(5)  # Limit concurrent tasks to 3
    with open("llm_course_descriptions.jsonl", "a") as f:
        tasks = [
            process_row(row, f, semaphore)
            for i, row in course_descriptions_df.iterrows()
        ]
        await asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(main())
