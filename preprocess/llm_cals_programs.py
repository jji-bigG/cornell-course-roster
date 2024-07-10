EXTRACT_MAJOR_REQUIREMENTS_PROMPT = """
### FIELD OF STUDY: {major}

### DESCRIPTION
{description}

### REQUIREMENTS
{requirements}

### OUTCOMES
{back}

### OTHER INFORMATION for your reference (they are NOT output fields, but may be helpful for your analysis)
to better get an idea of where this studies would concentrate on, here are some more information that may or may not be helpful. Take it with a grain of salt when analyzing the data.
sample_classes: {sample_classes}
related_disciplines: {related_disciplines}
associated_interests: {associated_interests}

### INSTRUCTIONS
BELOW ARE THE FIELDS THAT NEED TO BE EXTRACTED. IF THE INFORMATION IS NOT AVAILABLE, OUTPUT EMPTY STRINGS OR EMPTY LISTS. DO NOT MAKE ANY EDUCATED GUESS ON PURELY THE TITLE!
- description: output a LIST of short and concise string capturing the DESCRIPTION section. This can but not limited to include what works are expected, what are covered, what are the goals of this study... 2-5 short sentences suffice
- outcomes: output a LIST of short and concise string capturing the OUTCOMES section. This can but not limited to include what can you achieve, where does this enable you to work in, is there anything that this major allows you to achieve, how does this study benefit you in terms of academic & career & personal growth goals... 2-5 short sentences suffice
- requirements: output a LIST of short and concise string capturing the REQUIREMENTS section. This can but not limited to include what are the requirements, what are the perceived prerequisites, what are the core courses... YOU MUST INCLUDE THIS SECTION. MAKE IT UP IF NECESSARY
using the above information, output a comprehensive JSON data that can be used for further analysis and recommendation.

### OUTPUT REQUIREMENTS
EXTRACT THE FIELDS AS SPECIFIED under INSTRUCTIONS.
DO NOT MAKE UP ANY INFORMATION. IF THE DESCRIPTION IS NOT AVIALBLE OR IS EMPTY OR SUCH, OUTPUT EMPTY STRINGS OR EMPTY LISTS FOR EVERY FIELD; DO NOT MAKE ANY EDUCATED GUESS ON PURELY THE TITLE!
If there is not enough information to extract these information, output "[]" as an empty JSON list.
JSON output must be compatible and must begin with {{ and end with }} so that python's json.loads can parse it.

### JSON DATA EXTRACTED (beginning with {{ and ending with }} WITHOUT ```json and ```):
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

as_details_df = pd.read_json("as-studies-details.json")

SEEN_STUDIES = set()

try:
    with open("llm_as_extracted_studies.jsonl") as f:
        for line in f:
            extracted_studies = json.loads(line)
            SEEN_STUDIES.add(extracted_studies["study"])
except FileNotFoundError:
    pass


async def process_row(row, f, seamore):
    async with seamore:
        sample_classes = row.get("sample_classes", [])
        related_disciplines = row.get("related_disciplines", [])
        associated_interests = row.get("associated_interests", [])

        title = row["title"]
        prompt = EXTRACT_MAJOR_REQUIREMENTS_PROMPT.format(
            major=title,
            description=row["description"],
            requirements=row["requirements"],
            outcomes=row["outcomes"],
            sample_classes=sample_classes,
            related_disciplines=related_disciplines,
            associated_interests=associated_interests,
        )
        response = json.loads(await chat(prompt))
        print(f"processed {title}")
        f.write(
            json.dumps(
                {
                    "study": title,
                    "response": response,
                }
            )
            + "\n"
        )


import asyncio


async def main():
    with open("llm_as_extracted_studies.jsonl", "a") as f:
        semaphore = asyncio.Semaphore(2)
        tasks = [
            process_row(row, f, semaphore)
            for i, row in as_details_df.iterrows()
            if row["title"] not in SEEN_STUDIES
        ]
        await asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(main())
