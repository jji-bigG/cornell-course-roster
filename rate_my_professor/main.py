# the main crawler file for scrapping relevant information in rate my professors related to Cornell
import ratemyprofessor
import sqlite3
import json

conn = sqlite3.connect("roster_reviews.sqlite.db")
c = conn.cursor()

professors = c.execute("SELECT DISTINCT instructor FROM courses").fetchall()
professors = sorted(professors, key=len)[1:]

f = open("professor_reviews.jsonl", "a+")

# cornell = ratemyprofessor.get_schools_by_name("Cornell University")
# print([c.id for c in cornell])
# print([c.name for c in cornell])
cornell = ratemyprofessor.School(298)
# print(cornell.name)

for prof in professors:
    prof = prof[0].split(" (")[0]
    print(prof)
    profs = ratemyprofessor.get_professors_by_school_and_name(cornell, prof)
    print(f"Found {len(profs)} professors for {prof}")
    professor_data = []
    for p in profs:
        data = {
            "id": p.id,
            "name": p.name,
            "rating": p.rating,
            "difficulty": p.difficulty,
            "num_ratings": p.num_ratings,
            "would_take_again": p.would_take_again,
            "department": p.department,
            "courses": [
                {
                    "name": c.name,
                    "professor": [c.professor.id, c.professor.name],
                    "count": c.count,
                }
                for c in p.courses
            ],
        }
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
                    #  :param rating: The rating number.
                    # :param difficulty: The difficulty rating.
                    # :param comment: The rating comment.
                    # :param class_name: The class the rating was for.
                    # :param date: The date the rating was made.
                    # :param take_again: If the person who made the rating would take the class again, if any
                    # :param grade: The grade of the person who made the rating, if any
                    # :param thumbs_up: The number of thumbs up for the rating
                    # :param thumbs_down: The number of thumbs down for the rating
                    # :param online_class: If the rating is for an online class, if any
                    # :param credit: If the rating was for credit, if any
                    # :param attendance_mandatory: If attendance was mandatory for the class, if any
                }
            )
        data["ratings"] = ratings
        professor_data.append(data)
    f.write(json.dumps({prof: professor_data}) + "\n")
    # break


# profs = ratemyprofessor.get_professors_by_school_and_name(
#     cornell, "A.J. Edwards (aje45)"
# )
# print([(prof.id, prof.name, prof.rating, prof.school) for prof in profs])

# ['courses', 'department', 'difficulty', 'get_ratings', 'id', 'name', 'num_ratings', 'rating', 'school', 'would_take_again']

# prof_ratings = prof.get_ratings()

# for r in prof_ratings:
#     print(r.class_name, r.rating, r.difficulty, r.date, r.comment)
f.close()
