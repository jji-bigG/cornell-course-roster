# profile pages for coe professors, later we can extract other colleges

EXTRACT_FACULTY_PROMPT = """
### FACULTY DETAILS
education: {education}
department: {department}

##### CONTENTS on his profile page
it contain a lot of information, but may not. make use of EVERYTHING in the profile page for the INSTRUCTIONS.
PAY ATTENTION TO THE BIOGRAPHY, PUBLICATIONS, TEACHING INTERESTS, AND THE RESEARCH PORTIONS WHEN IF HE TALKS ABOUT THEM.
{bio}

##### IN THE NEWS for cornell's own website
{in_the_news}


### INSTRUCTIONS
From the above faculty details, please extract the following (they're the keys to our JSON output): 
"subdomains": Which subdomain of academia does the faculty have expertise in based on ? (e.g. within Artificial Intelligence, we have reinforcement learning with human feedback, traditioal ML algorithms & its proofs, convolutional neural networks in multi-object tracking, etc.). Subdomains are areas where the faculty has expertise in. The output should be a list of strings of ideally length 3-5.
"goals": What is the faculty working towards based on his research, publications, biography? (e.g. "to develop a new algorithm for X", "to improve the efficiency of Y", etc.) THIS SHOULD BE A LIST OF STRINGS. concise short sentences are preferred.
"experience": What are his researches? What experience does he have in these researches? output should be a list of strings. concise short sentences are preferred.
"summary": in one or two sentences, summarize the faculty's expertise and research interests.

### OUTPUT REQUIREMENT
DO NOT MAKE UP ANY INFORMATION, ONLY EXTRACT INFORMATION THAT IS PRESENT IN THE TEXT.
If there is not enough information to extract these information, output "None".
If there is not enough information to extract these information, output "[]" as an empty JSON list.
JSON output must be compatible and must begin with {{ and end with }} so that python's json.loads can parse it. DO NOT BEGIN WITH ```json and end with ```! 
No escape character is needed for ', and wrap string with double quotes.

For example:
{{ "subdomains": ["subdomain1", "subdomain2", "subdomain3"], "goals": ["goal1", "goal2", "goal3"], "experience": ["experience1", "experience2", "experience3"], "summary": "summary" }}

### EXTRACTED JSON DATA FROM FACULTY DETAILS:
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

details_df = pd.read_json("as-prof-details.json")
# print([k for k in details_df["content"][0].keys()])

try:
    SEEN = set()
    f = open("llm_as_prof_profiles.jsonl", "r")
    for line in f:
        prof = json.loads(line)
        SEEN.add(prof["prof"])
    f.close()
except FileNotFoundError:
    SEEN = set()

import asyncio


async def process_row(row, f, semaphore):
    if row["name"] in SEEN:
        return
    async with semaphore:
        bio = row["content"]
        in_the_news = row["news_items"]
        prompt = EXTRACT_FACULTY_PROMPT.format(
            education=row["education"],
            department=row["departments"],
            bio=bio,
            in_the_news=in_the_news,
        )
        response = await chat(prompt)
        try:
            extracted = json.loads(response)
        except:
            extracted = response
        f.write(json.dumps({"prof": row["name"], "extracted": extracted}) + "\n")
        print(f"Processed {row['name']}")


async def main():
    semaphore = asyncio.Semaphore(4)
    f = open("llm_as_prof_profiles.jsonl", "a")
    tasks = [process_row(row, f, semaphore) for _, row in details_df.iterrows()]
    await asyncio.gather(*tasks)
    f.close()


if __name__ == "__main__":
    asyncio.run(main())
