EXTRACT_AS_STUDIES_PROMPT = """
You are an academic & career expert or counselor at a world prestigious American college, and given the information about a field of study, you want to extract & come up with insightful analysis of the field of study (that can be a major, minor, special program...).

# INFORMATION

these are scraped websites which contains relevant contents that can provide insightful analysis for your reference.

## FIELD OF STUDY: {title}

### DESCRIPTION
{description}

### REQUIREMENTS
{requirements}

### OUTCOMES
{outcomes}

### OTHER RELEVANT INFORMATIONS that may not be present
related_studies: {related_studies}
associated_interests: {associated_interests}
degree_levels: {degree_levels}

# WHAT TO EXTRACT

### INSTRUCTIONS
- requirements: what type of people are suitable for this field of study? what are the requirements to get into this field of study? 5-7 short sentences should suffice
- prerequisites: what skills are suitable to have before entering this field of study? 2-5 short sentences should suffice
- outcomes: what do this field of study graduates do after graduation? what do this enable you to do (make relavant inferences as fit)? 4-6 short sentences should suffice
- interests: what should you be interested in to excel in this field of study? which groups of people / interest group would appreciate this field of study? 2-4 short sentences should suffice
- industries: what industries are related to this field of study? what are the job prospects for this field of study? 3-5 short phrases should suffice

### OUTPUT REQUIREMENT
for each bullet point in INSTRUCTIONS, OUTPUT A LIST OF STRINGS that captures the information as needed.
MAKE INFERENCES AND INSIGHTS THAT YOU THINK IS NECESSARY BASED ON ALL THE INFORMATION ABOVE. IT IS FINE TO MAKE UP INFORMATION IF IT IS LOGICALLY CONNECTED.
If there is not enough information to extract these information, output "[]" as an empty JSON list.
JSON output must be compatible and must begin with {{ and end with }} so that python's json.loads can parse it. DO NOT BEGIN WITH ```json and end with ```! 
No escape character is needed for ', and wrap string with double quotes.


JSON OUTPUT starting with {{ and ending with }}:
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

details_df = pd.read_json("as-studies-details.json")

try:
    SEEN = set()
    f = open("llm_as_studies_extracted.jsonl", "r")
    for line in f:
        study = json.loads(line)
        SEEN.add(study["title"])
    f.close()
except FileNotFoundError:
    SEEN = set()

import asyncio


async def process_row(row, f, semaphore):
    title = row["title"]

    if title in SEEN:
        print(f"seen {title} already")
        return
    async with semaphore:
        prompt = EXTRACT_AS_STUDIES_PROMPT.format(
            title=title,
            description=row["description"],
            requirements=row["requirements"],
            outcomes=row["outcomes"],
            degree_levels=row["sidebar"]["degree_levels"],
            related_studies=row["sidebar"]["related_disciplines"],
            associated_interests=row["sidebar"]["associated_interests"],
        )
        response = await chat(prompt)
        try:
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
    with open("llm_as_studies_extracted.jsonl", "a") as f:
        tasks = [process_row(row, f, semaphore) for _, row in details_df.iterrows()]
        await asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(main())
