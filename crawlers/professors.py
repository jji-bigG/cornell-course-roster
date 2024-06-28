# find all the professors and list all of their websites and stuff
# (but bc discussions r kinda bs just listed there)

import csv
import os

# compile this professor to every directory, then synthesize into one big csv


class ProfessorSearch:
    sections = []
    files = []

    def __init__(self, folder) -> None:
        self.files = []
        self.sections = []


prof = ProfessorSearch('FA14')
