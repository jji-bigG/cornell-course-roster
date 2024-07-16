EXTRACT_CALS_STUDIES_PROMPT = """
You are an expert in the field of Agriculture and Life Sciences at Cornell University. You have been asked to extract information and make your own analysis and expert insights on these fields of study.

# INFORMATION

## TITLE: {title}
## WHO's EGLIGIBLE: {field}

### DESCRIPTION
{description}

### MORE INFORMATION
{back}

### URL
{url}

# WHAT TO EXTRACT

### INSTRUCTIONS
- offered_by: who offers this field of study based on the url? if the url starts with /education/, then it is offered by Cornell University. one phrase should suffice (STRING REQUIRED, NOT LIST, NOT EMPTY, e.g. "Cornell University")
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

details_df = pd.read_json("cals-studies-list.jsonl", lines=True)

fname = "llm_cals_studies_extracted.jsonl"

try:
    SEEN = set()
    f = open(fname, "r")
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
        prompt = EXTRACT_CALS_STUDIES_PROMPT.format(
            title=title,
            field=row["field"],
            description=row["description"],
            back=row["back"],
            url=row["url"],
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
    semaphore = asyncio.Semaphore(3)
    with open(fname, "a") as f:
        tasks = [process_row(row, f, semaphore) for _, row in details_df.iterrows()]
        await asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(main())
