# we might not have requested all the ratings from the start & stop of our scraping
# need to synthesize them into a list of ratings corresponding to the sqlite db's prof instances

import json
import sqlite3
import ratemyprofessor

seen_ids = set()
fetched_ids = set()
unfetched_ids = set()
saved_ids = set()

cornell = ratemyprofessor.School(298)

saved_ratings = set()
f_ratings = open("ratings.jsonl", "r")
for line in f_ratings.readlines():
    saved_ratings.add(json.loads(line)["id"])
f_ratings.close()

print(f"resuming with {len(saved_ratings)} saved ratings")

f_ratings = open("ratings.jsonl", "a")


def check_belong_school(prof_id, school_id):
    prof = ratemyprofessor.Professor(prof_id)
    return prof.school.id == school_id


with open("professor_data.jsonl", "r") as f:
    for line in f.readlines():
        saved_profs = json.loads(line)
        for prof in saved_profs[list(saved_profs.keys())[0]]:
            if prof["id"] not in saved_ratings:
                seen_ids.add(prof["id"])
                if "ratings" in prof:
                    fetched_ids.add(prof["id"])
                    if prof["id"] not in saved_ids and check_belong_school(
                        prof["id"], 298
                    ):
                        f_ratings.write(json.dumps(prof) + "\n")
                        saved_ids.add(prof["id"])
                        print(f"rating processed for {prof['name']}")
                else:
                    unfetched_ids.add(prof["id"])

f_ratings.close()
# print(
#     len(seen_ids),
#     len(fetched_ids),
#     len(unfetched_ids),
#     len(fetched_ids - unfetched_ids),
# )
# print(list(unfetched_ids)[0:10])
