# profile pages for coe professors, later we can extract other colleges

EXTRACT_FACULTY_PROMPT = """
### FACULTY DETAILS
education: {education}
department: {department}
position: {position}

##### BIOGRAPHY
{bio}

##### RESEARCH INTERESTS
{research}

##### PUBLICATIONS
{publications}


### INSTRUCTIONS
From the above faculty details, please extract the following (they're the keys to our JSON output): 
"subdomains": Which subdomain of academia does the faculty have expertise in based on ? (e.g. within Artificial Intelligence, we have reinforcement learning with human feedback, traditioal ML algorithms & its proofs, convolutional neural networks in multi-object tracking, etc.). Subdomains are areas where the faculty has expertise in. The output should be a list of strings of ideally length 3-5.
"goals": What is the faculty working towards based on his research, publications, biography? (e.g. "to develop a new algorithm for X", "to improve the efficiency of Y", etc.) THIS SHOULD BE A LIST OF STRINGS.
"experience": How experienced is the faculty? What are his research? output should be a list of strings. concise short sentences are preferred.
"summary": in one or two sentences, summarize the faculty's expertise and research interests.

### OUTPUT REQUIREMENT
DO NOT MAKE UP ANY INFORMATION, ONLY EXTRACT INFORMATION THAT IS PRESENT IN THE TEXT.
If there is not enough information to extract these information, output "None".
If there is not enough information to extract these information, output "[]" as an empty JSON list.
JSON output must be compatible and must begin with {{ and end with }} so that python's json.loads can parse it.
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

eng_profs = pd.read_json("eng-prof-details.json")
eng_profs_list = pd.read_json("eng-prof-list.json")


async def main():
    fr = open("llm_eng_professor_profiles.jsonl", "r")
    seen_profs = set()
    for line in fr:
        data = json.loads(line)
        seen_profs.add(data["prof"])
    fr.close()
    f = open("llm_eng_professor_profiles.jsonl", "a")

    for prof in eng_profs_list["prof_name"]:
        if prof in seen_profs:
            print(f"Skipping {prof}: Already seen")
            continue
        prof_description = eng_profs_list[eng_profs_list["prof_name"] == prof]
        matched = eng_profs[eng_profs["prof_name"] == prof]
        if matched.empty:
            print(f"Could not find profile for {prof}")
            continue
        prof_details = matched.iloc[0]
        # print(prof_details)
        # break
        prompt = EXTRACT_FACULTY_PROMPT.format(
            education=prof_details["education"],
            department=prof_description["department"],
            position=prof_description["position"],
            bio=prof_details["bio"],
            research=prof_details["research_interests"],
            publications=prof_details["selected_publications"],
        )
        response = json.loads(await chat(prompt))
        f.write(json.dumps({"prof": prof, "response": response}) + "\n")
        print(f"Extracted profile for {prof}")

    f.close()


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
