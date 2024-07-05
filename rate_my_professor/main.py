# the main crawler file for scrapping relevant information in rate my professors related to Cornell
import ratemyprofessor

# cornell = ratemyprofessor.get_schools_by_name("Cornell University")
# print([c.id for c in cornell])
# print([c.name for c in cornell])
cornell = ratemyprofessor.School(298)
print(cornell.name)
profs = ratemyprofessor.get_professors_by_school_and_name(
    cornell, "A.J. Edwards (aje45)"
)
print([(prof.id, prof.name, prof.rating, prof.school) for prof in profs])

# ['__class__', '__delattr__', '__dict__', '__dir__', '__doc__', '__eq__', '__format__', '__ge__', '__getattribute__', '__getstate__', '__gt__', '__hash__', '__init__', '__init_subclass__', '__le__', '__lt__', '__module__', '__ne__', '__new__', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__', '__sizeof__', '__str__', '__subclasshook__', '__weakref__', '_get_rating_info', 'courses', 'department', 'difficulty', 'get_ratings', 'id', 'name', 'num_ratings', 'rating', 'school', 'would_take_again']

# prof_ratings = prof.get_ratings()

# for r in prof_ratings:
#     print(r.class_name, r.rating, r.difficulty, r.date, r.comment)
