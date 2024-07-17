fname = "relationship_course_descriptions.jsonl"

COURSE_DESCRIPTION_TEMPLATE = """
### {course_name}
##### HIGH LEVEL SUMMARY
PERCEIVED PREREQUISITES (what seems to be necessary according to the description): {perceived_prerequisites}
CONTENTS: {contents}
OUTCOMES: {outcomes}
##### DESCRIPTION
{description}
"""

PROMPT = """
You are an elite student at a prestigious American university, and you are looking at the courses and thinking about what it allows you to achieve.
You have a course you're interested in and its list of pre-requisites or co-requisites. You dug up the entire chain of pre-requisites and co-requisites starting from the beginning that would lead you to this class.

You want to know where this course can take you and what relationships it has with its prerequisites.

# INFORMATION
you have already read through its descriptions and extracted some HIGH LEVEL SUMMARY based on its factual description and made some inferences.

## CURRENT COURSE INFORMATION
{current_course}

## PRE-REQUISITES or CO-REQUISITES
{courses}

# EXTRACTION

### INSTRUCTION
- relationship: LIST of JSON OBJECTS that lists courses in the prerequisites that seem to be helpful and required to take this course. The courses in this list contain information that is relevant to what you will achieve from that course.
- foundational: LIST of JSON OBJECTS of COURSE CODE and REASON for courses in PRE-REQUISITES or CO-REQUISITES that seem to lay a solid foundation for this course. THESE ARE ABSOLUTELY NECESSARY FOR TAKING THIS COURSE, otherwise you won't be able to know what is going on.
- advanced: LIST of JSON OBJECTS of COURSE CODE and REASON for courses in PRE-REQUISITES or CO-REQUISITES that seem to be advanced and are not necessary for taking this course, but would be helpful to know before taking this course.
- unrelated: LIST of JSON OBJECTS of COURSE CODE and REASON for courses in PRE-REQUISITES or CO-REQUISITES that seem to be unrelated to this course and don't seem to be necessary for taking this course.
the json object in the LIST should be in the following format:
[{{ "course_code": "CS 2110", "reason": "<REASON>" }}, ...]

### OUTPUT REQUIREMENT
for each bullet point in INSTRUCTIONS, OUTPUT A LIST OF STRINGS that captures the information as needed.
MAKE INFERENCES AND INSIGHTS THAT YOU THINK IS NECESSARY BASED ON ALL THE INFORMATION ABOVE. IT IS FINE TO MAKE UP INFORMATION IF IT IS LOGICALLY CONNECTED.
If there is not enough information to extract these information, output "[]" as an empty JSON list.
JSON output must be compatible and must begin with {{ and end with }} so that python's json.loads can parse it. DO NOT BEGIN WITH ```json and end with ```! 
No escape character is needed for ', and wrap string with double quotes.

OUTPUT IN JSON FORMAT STARTING WITH {{ and ending with }}:
"""

from openai import AsyncOpenAI
import json

from volcenginesdkarkruntime import AsyncArk

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


async_client = AsyncArk(api_key="23932667-123e-4f75-b2c2-d464f6efa691")
# endpoint_id = 'ep-20240715082642-jjzqf' # lite-32k
# endpoint_id = 'ep-20240715083915-94zbz' # lite-128K
endpoint_id = "ep-20240715083302-q4xcw"  # pro-32k
# endpoint_id = 'ep-20240711095338-wtmfq' # pro-128k


def call_doubao(prompt):
    try:
        completion = client.chat.completions.create(
            model=endpoint_id,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0,
        )
        return completion.choices[0].message.content
    except Exception as e:
        print(e)
        return "error"


async def call_doubao_async(prompt):
    all_content = ""
    try:
        completion = await async_client.chat.completions.create(
            model=endpoint_id,
            messages=[{"role": "user", "content": prompt}],
            stream=True,
            temperature=0.0,
            timeout=600,
        )
        async for item in completion:
            content = item.choices[0].delta.content
            all_content += content
    except Exception as e:
        print(e)
        return "error"
    return all_content


import pandas as pd

course_descriptions_df = pd.read_json("llm_course_descriptions.jsonl", lines=True)
course_descriptions_infer_df = pd.read_json(
    "llm_course_descriptions-inference.jsonl", lines=True
)

import sqlite3

conn = sqlite3.connect("roster_reviews.sqlite.db")

descriptions = pd.read_sql_query("SELECT * FROM course_descriptions", conn)
courses = pd.read_sql_query("SELECT * FROM courses", conn)

conn.close()

try:
    SEEN = set()
    f = open(fname, "r")
    for line in f:
        course = json.loads(line)
        SEEN.add(course["course_id"])
    f.close()
except FileNotFoundError:
    SEEN = set()


def get_course_name_from_id(course_id):
    # print("getting name from id", course_id)
    return courses[courses["course_id"] == course_id]["name"].values[0]


def get_course_id_from_name(course_name):
    return courses[courses["name"] == course_name]["course_id"].values[0]


def get_pre_reqs_from_id(id):
    for c in course_descriptions_df[course_descriptions_df["course_id"] == id][
        "response"
    ].values[0]["hard_written_prerequisites"]:
        d = c.split(" ")[0]
        code = c.split(" ")[1]
        yield f"{d} {code}"


# now let's traverse it through
test_id = get_course_id_from_name("CS 3110")


def get_all_pre_reqs(id):
    frontier = set([id])
    visited = set()
    while frontier:
        current = frontier.pop()
        visited.add(current)
        for pre_req in get_pre_reqs_from_id(current):
            pre_req_id = get_course_id_from_name(pre_req)
            if pre_req_id not in visited:
                frontier.add(pre_req_id)
    return reversed(list(visited))


def get_all_pre_reqs_description_prompt(test_id):
    pts = []
    for id in get_all_pre_reqs(test_id):
        pts.append(
            COURSE_DESCRIPTION_TEMPLATE.format(
                course_name=get_course_name_from_id(id),
                perceived_prerequisites=course_descriptions_infer_df[
                    course_descriptions_infer_df["course_id"] == id
                ]["response"].values[0]["perceived_prerequisites"],
                contents=course_descriptions_infer_df[
                    course_descriptions_infer_df["course_id"] == id
                ]["response"].values[0]["contents"],
                outcomes=course_descriptions_infer_df[
                    course_descriptions_infer_df["course_id"] == id
                ]["response"].values[0]["outcomes"],
                description=descriptions[descriptions["course_id"] == id][
                    "description"
                ].values[0],
            )
        )
    return pts


async def process_row(row, f, semaphore):
    course_id = row["course_id"]

    if course_id in SEEN:
        print(f"seen {course_id} already")
        return

    prereqs = get_all_pre_reqs_description_prompt(course_id)
    if not prereqs:
        print(f"no prereqs for {course_id}")
        return

    async with semaphore:
        print(f"processing {course_id}")
        descrs = prereqs
        prompt = PROMPT.format(
            current_course=descrs[-1],
            courses="\n".join(descrs[:-1]),
        )
        response = await chat(prompt)
        try:
            extracted = json.loads(response)
        except:
            extracted = response
        relationship = {
            "course_id": int(course_id),
            "extracted": extracted,
            "prompt": prompt,
        }
        # print(prompt)
        # print(relationship)
        f.write(json.dumps(relationship) + "\n")
        f.flush()
        SEEN.add(course_id)
        print(f"processed {course_id}")


import asyncio


async def main():
    semaphore = asyncio.Semaphore(3)
    with open(fname, "a") as f:
        tasks = [process_row(row, f, semaphore) for _, row in courses.iterrows()]
        # row = courses.loc[courses["course_id"] == test_id].iloc[0]
        # print(row)
        # tasks = [process_row(row, f, semaphore)]
        await asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(main())
