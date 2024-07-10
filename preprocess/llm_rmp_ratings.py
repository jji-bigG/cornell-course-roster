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
"positive": What are some positive aspects of the professor based on the reviews? This should be a list of strings each under 20 words. short phrases or sentences suffice as long as it captures the essential meaning of these reviews.
"negative": list of strings each of length under 20 words. short phrases or sentences suffice as long as it captures the essential meaning of these reviews.
"others": other attributes that are not positive or negative. This should be a list of strings.
"summary": in one or two sentences, summarize the professor based on the reviews. If mixed reviews, summarize both sides, do not mention it is mixed reviews.

### OUTPUT REQUIREMENT
Do not make up any information, only strictly based on the professor reviews. Output less than 3 attributes if there is not enough relevant information to be classified into that category.
If there is not enough information to extract these information, output "[]" as an empty JSON list.
JSON output must be compatible and must begin with {{ and end with }} so that python's json.loads can parse it.
No escape character is needed for ', and wrap string with double quotes.

### JSON DATA EXTRACTED FROM REVIEWS (beginning with {{ and ending with }}):
"""

GLEAN_PROFESSOR_REVIEW_PROMPT = """
### PREVIOUS OUTPUT INSTRUCTIONS
From the above reviews, please extract the following:
"positive": What are some positive aspects of the professor based on the reviews? This should be a list of strings each under 20 words. short phrases or sentences suffice as long as it captures the essential meaning of these reviews.
"negative": list of strings each of length under 20 words. short phrases or sentences suffice as long as it captures the essential meaning of these reviews.
"others": other attributes that are not positive or negative. This should be a list of strings.
"summary": in one or two sentences, summarize the professor based on the reviews. If mixed reviews, summarize both sides, do not mention it is mixed reviews.

### PREVIOUS OUTPUTS
{previous_outputs}

### OUTPUT & INSTRUCTIONS
due to a limited context window, I have generated several outputs based on above PREVIOUS OUTPUT INSTRUCTIONS.

review and combine the generated outputs from the previous few steps to generate the final output that follows the PREVIOUS OUTPUT INSTRUCTIONS.

Do not make up any information.
If there is not enough information to extract these information, output "[]" as an empty JSON list.
JSON output must be compatible and must begin with {{ and end with }} so that python's json.loads can parse it.
No escape character is needed for ', and wrap string with double quotes.

### CLEANED JSON DATA (beginning with {{ and ending with }}):
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


# Define the function to split the list into chunks
def split_into_chunks(lst, max_chunk_size):
    for i in range(0, len(lst), max_chunk_size):
        yield lst[i : i + max_chunk_size]


async def main():
    fr = open("llm_professor_reviews.jsonl", "r")
    seen = set([json.loads(l)["professor"] for l in fr.readlines()])
    fr.close()

    f = open("llm_professor_reviews.jsonl", "a")

    ratings_df = pd.read_json("ratings.jsonl", lines=True)
    max_token_limit = 16000  # Define the token limit

    # Estimate average token size per review. Adjust as needed.
    avg_token_per_review = 100

    # Calculate the maximum number of reviews that can fit within the token limit
    max_reviews_per_chunk = max_token_limit // avg_token_per_review

    for i in range(len(ratings_df)):
        if ratings_df.iloc[i]["name"] in seen:
            print(f'Skipping {ratings_df.iloc[i]["name"]}: Already seen')
            continue

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

        # Split the ratings_sample_list into manageable chunks
        chunks = list(split_into_chunks(ratings_sample_list, max_reviews_per_chunk))
        responses = []

        for chunk in chunks:
            prompt = EXTRACT_PROFESSOR_REVIEW_PROMPT.format(
                professor=ratings_df.iloc[i]["name"],
                department=department,
                overall_rating=overall_rating,
                overall_difficulty=overall_difficulty,
                reviews=chunk,
            )

            response = await chat(prompt)
            try:
                responses.append(json.loads(response))
            except:
                responses.append(response)
            print(response)

        # Combine responses
        combined_response = {
            "professor": str(ratings_df.iloc[i]["name"]),
            "rmp_id": int(ratings_df.iloc[i]["id"]),
            "responses": responses,
            "gleaned": None,
        }

        f.write(json.dumps(combined_response) + "\n")
        print(f'Processed {i + 1}/{len(ratings_df)}: {ratings_df.iloc[i]["name"]}')

    f.close()


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
