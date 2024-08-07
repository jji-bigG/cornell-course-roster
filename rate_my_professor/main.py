# the main crawler file for scrapping relevant information in rate my professors related to Cornell
import ratemyprofessor
import sqlite3
import json
from concurrent.futures import ThreadPoolExecutor, as_completed

conn = sqlite3.connect("roster_reviews.sqlite.db")
c = conn.cursor()

professors = c.execute("SELECT DISTINCT instructor FROM courses").fetchall()
conn.close()
professors = sorted(professors, key=len)[1:]

cornell = ratemyprofessor.School(298)

fr = open("professor_data.jsonl", "r")

QUERIED_PROFESSORS = set()  # from the previous runs; name from the sqlite db
SEEN_PROFESSORS_IDs = set()  # id are the RMP id's

for l in fr.readlines():
    saved_profs = json.loads(l)
    p = [x for x in saved_profs.keys()][0]
    QUERIED_PROFESSORS.add(p)
    for prof in saved_profs[p]:
        if "ratings" in prof:
            SEEN_PROFESSORS_IDs.add(prof["id"])


# print(QUERIED_PROFESSORS)
fr.close()


professors = set([prof[0].split(" (")[0] for prof in professors])
professors -= QUERIED_PROFESSORS

print(f"Total professors to query: {len(professors)}")
print(professors)


def fetch_ratings(p):
    prof_ratings = p.get_ratings()
    ratings = []
    for r in prof_ratings:
        ratings.append(
            {
                "class_name": r.class_name,
                "rating": r.rating,
                "difficulty": r.difficulty,
                "comment": r.comment,
                "date": r.date.strftime("%Y-%m-%d"),
                "take_again": r.take_again,
                "grade": r.grade,
                "thumbs_up": r.thumbs_up,
                "thumbs_down": r.thumbs_down,
                "online_class": r.online_class,
                "credit": r.credit,
                "attendance_mandatory": r.attendance_mandatory,
            }
        )
    return ratings


def fetch_professor_data(prof):
    # print(prof)
    profs = ratemyprofessor.get_professors_by_school_and_name(cornell, prof)
    print(f"Found {len(profs)} professors for {prof}")
    professor_data = []
    for p in profs:
        if p.school.id != 298:
            print(f"not a cornell professor for {p.name} under search for {prof}")
            continue
        data = {
            "id": p.id,
            "name": p.name,
            "rating": p.rating,
            "difficulty": p.difficulty,
            "num_ratings": p.num_ratings,
            "would_take_again": p.would_take_again,
            "department": p.department,
            "school": p.school.name,
            "courses": [
                {
                    "name": c.name,
                    "professor": [c.professor.id, c.professor.name],
                    "count": c.count,
                }
                for c in p.courses
            ],
        }
        if p.id not in SEEN_PROFESSORS_IDs:
            data["ratings"] = fetch_ratings(p)
            SEEN_PROFESSORS_IDs.add(p.id)
        professor_data.append(data)
    return {prof: professor_data}


# Number of parallel tasks
num_parallel_tasks = 30

# Open the file to write the output

with open("professor_data.jsonl", "a") as f:
    # Create a ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=num_parallel_tasks) as executor:
        # Submit tasks to the executor
        futures = [executor.submit(fetch_professor_data, prof) for prof in professors]

        # As the tasks complete, write their results to the file
        for future in as_completed(futures):
            result = future.result()
            f.write(json.dumps(result) + "\n")
