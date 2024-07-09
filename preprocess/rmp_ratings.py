# rate my professors ratings and reviews extraction using LLMs

EXTRACT_PROFESSOR_REVIEW_PROMPT = """
professor: {professor}
department: {department}
overall rating: {overall_rating}
overall difficulty: {overall_difficulty}

### PROFESSOR REVIEWS
{reviews}

### INSTRUCTIONS
From the above reviews, please extract the following:
"positive": What are some positive aspects of the professor based on the reviews? This should be a list of strings.
"negative": list of strings.
"others": other attributes that are not positive or negative. This should be a list of strings.
"summary": in one or two sentences, summarize the professor based on the reviews. If mixed reviews, summarize both sides, do not mention it is mixed reviews.

### OUTPUT REQUIREMENT
Do not make up any information, only strictly based on the professor reviews. Output less than 3 attributes if there is not enough relevant information to be classified into that category.
If there is not enough information to extract these information, output "[]" as an empty JSON list.
JSON output must be compatible and must begin with {{ and end with }} so that python's json.loads can parse it.

### JSON DATA EXTRACTED FROM REVIEWS (beginning with {{ and ending with }}):
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


async def main():
    f = open("llm_professor_reviews.json", "a")

    ratings_df = pd.read_json("ratings.jsonl", lines=True)
    for i in range(len(ratings_df)):
        ratings_sample_list = [
            {
                "score": r["rating"],
                "difficulty": r["difficulty"],
                "review": r["comment"],
            }
            for r in ratings_df.iloc[i]["ratings"]
        ]
        department = ratings_df.iloc[i]["department"]
        overall_rating = ratings_df.iloc[i]["rating"]
        overall_difficulty = ratings_df.iloc[i]["difficulty"]

        prompt = EXTRACT_PROFESSOR_REVIEW_PROMPT.format(
            professor=ratings_df.iloc[i]["name"],
            department=department,
            overall_rating=overall_rating,
            overall_difficulty=overall_difficulty,
            reviews=ratings_sample_list,
        )

        response = await chat(prompt)
        print(response)
        response = json.loads(response)
        f.write(json.dumps(response))
        f.write("\n")
        print(f'Processed {i + 1}/{len(ratings_df)}: {ratings_df.iloc[i]["name"]}')

    f.close()


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
