EXTRACT_AS_STUDIES_PROMPT = """
You are an administrator at a world prestigious American college, and given the information about a faculty (that can be students, professors, partners in various fields), you want to extract & come up with insightful analysis of the faculty.

# INFORMATION

these are scraped websites which contains relevant contents that can provide insightful analysis for your reference.

## FACULTY POSITION: {position}
email: {email}

### SUMMARY
{summary}

### DESCRIPTION (may not have this section for some faculty)
{edu_and_awards}

### INTERESTS
{interests}

### PUBLICATIONS
{publications}

### OTHER RELEVANT INFORMATIONS that may not be present
courses_taught: {courses_taught}
news_items: {news_items}
links: {links}. this might not be helpful, just a quick reference


# WHAT TO EXTRACT

### INSTRUCTIONS
- goals: What is the faculty working towards based on his research, publications, biography? (e.g. "to develop a new algorithm for X", "to improve the efficiency of Y", etc.) THIS SHOULD BE A LIST OF STRINGS. This can be short or long sentences as needed.

### OUTPUT REQUIREMENT
for each bullet point in INSTRUCTIONS, OUTPUT A LIST OF STRINGS that captures the information as needed.
MAKE INFERENCES AND INSIGHTS THAT YOU THINK IS NECESSARY BASED ON ALL THE INFORMATION ABOVE. IT IS FINE TO MAKE UP INFORMATION IF IT IS LOGICALLY CONNECTED.
If there is not enough information to extract these information, output "[]" as an empty JSON list.

DO NOT BEGIN WITH ```json and end with ```! JSON output must be compatible and must begin with {{ and end with }} so that python's json.loads can parse it.

No escape character is needed for ', and wrap string with double quotes.
DO NOT INCLUDE ANY EXPLANATIONS OR COMMENTS IN THE OUTPUT. ONLY THE JSON OUTPUT starting with {{ and ending with }}.


output:
"""

# - email: give me the faculty's email from that unparsed HTML tags (example output: rj378@cornell.edu)
# - research: give me the faculty's research interests. in what fields do him/her excel? where is this faculty going with the research? what research goals do he/she have? 5-7 short sentences should suffice
# - experience: based on the faculty's education, awards, publications, and such, what is the faculty's experience like? is he/she a seasoned professional or a fresh graduate? 4-6 short sentences should suffice
# - teaching: what courses does the faculty teach? what are the faculty's teaching methods? what are the faculty's teaching goals? 4-6 short sentences should suffice. THIS MAY NOT BE PRESENT IN THE INFORMATION AND MUST BE BASED ON FACTUAL INFORMATION (if not present, output "[]")
# - is_student: TRUE or FALSE output based on the above information. output TRUE if the faculty is a student, otherwise FALSE
# - has_extensive_profile: TRUE or FALSE output based on the above information to determine whether the profile has a very complete information or not (if there are a lot that is covered about the professor, output TRUE, otherwise FALSE)
# - fields: what fields does the faculty specialize in? what are the faculty's research interests? what are the faculty's teaching interests? 3-5 short phrases should suffice

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

df = pd.read_json("cals-prof-details.json")

try:
    SEEN = set()
    f = open("llm_cals_faculties_extracted-goals.jsonl", "r")
    for line in f:
        l = json.loads(line)
        SEEN.add(l["title"])
    f.close()
except FileNotFoundError:
    SEEN = set()

import asyncio


async def process_row(row, f, semaphore):
    title = row["name"]

    if title in SEEN:
        print(f"seen {title} already")
        return
    async with semaphore:
        prompt = EXTRACT_AS_STUDIES_PROMPT.format(
            position=row["position"],
            summary=row["summary"],
            edu_and_awards=row["edu_and_awards"],
            interests=row["interests"],
            publications=row["publications"],
            courses_taught=row["courses_taught"],
            news_items=row["news_items"],
            email=row["contacts"]["email"] if "email" in row["contacts"] else "[]",
            links=row["contacts"]["links"] if "links" in row["contacts"] else "[]",
        )
        if len(prompt) > 45000:
            prompt = EXTRACT_AS_STUDIES_PROMPT.format(
                position=row["position"],
                summary=row["summary"],
                edu_and_awards='row["edu_and_awards"]',
                interests=row["interests"],
                publications=row["publications"],
                courses_taught=row["courses_taught"],
                news_items=row["news_items"],
                email=row["contacts"]["email"] if "email" in row["contacts"] else "[]",
                links=row["contacts"]["links"] if "links" in row["contacts"] else "[]",
            )
            print(f"prompt too long for {title}")

        response = await chat(prompt)

        try:
            if response.startswith("```json"):
                extracted = json.loads(response[len("```json\n") : -len("\n```")])
            else:
                extracted = json.loads(response)
        except:
            extracted = response
        study = {
            "title": title,
            "extracted": extracted,
        }
        f.write(json.dumps(study) + "\n")
        SEEN.add(title)
        print(f"processed {title}")


async def main():
    semaphore = asyncio.Semaphore(10)
    with open("llm_cals_faculties_extracted-goals.jsonl", "a") as f:
        tasks = [process_row(row, f, semaphore) for _, row in df.iterrows()]
        await asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(main())
