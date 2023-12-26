# DS analysis
# find all the professors and list all of their lectures
# (but bc discussions r kinda bs just listed there)
import csv
import os

# compile this professor to every directory, then synthesize into one big csv


class ProfessorSearch:
    files = []

    def __init__(self, files) -> None:
        self.files = files
        print(files)


prof = ProfessorSearch([f for f in os.listdir() if f.endswith('.csv')])
