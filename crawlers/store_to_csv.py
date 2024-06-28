# dissect the main roster catalog and list the entire subject (codes) and
# call the crawler on the list of URLs

import requests
from bs4 import BeautifulSoup
import csv
import os

from crawler import SubjectRoster

# semesters_url_list = [
#     "https://classes.cornell.edu/browse/roster/FA23"
# ]
# # programmatically format this
# for i in range(14, 24):
#     semesters_url_list.append(
#         "https://classes.cornell.edu/browse/roster/" + "FA" + str(i))
#     semesters_url_list.append(
#         "https://classes.cornell.edu/browse/roster/" + "SP" + str(i))

# print(semesters_url_list)

# we move onto dissection all the section numbers in each semester's roster


def subjectIDs(url):
    if os.path.exists(f'{semester}/subjectIDs.html'):
        with open(f'{semester}/subjectIDs.html', 'r') as f:
            html = f.read()
    else:
        html = requests.get(url).text
        os.makedirs(f'{semester}')
        with open(f'{semester}/subjectIDs.html', 'w') as f:
            f.write(html)

    bsParser = BeautifulSoup(html, "lxml")

    ids = []
    for item in bsParser.find_all(name="ul", class_="subject-group"):
        # itemParser = BeautifulSoup(item)
        ids.append(item.find('li').find('a').contents[0])
    return ids


# print(subjectIDs(semesters_url_list[0]))
def generateCSVForSemestersSubject(semester: str, subject: str):
    print(f'working on {semester} {subject}')
    if not os.path.exists(semester):
        os.makedirs(semester)

    # get the html and pass down the file to the parser object
    if os.path.exists(f'{semester}/{subject}.html'):
        return
        with open(f'{semester}/{subject}.html', 'r') as f:
            reqText = f.read()
    else:
        reqText = requests.get(
            f"https://classes.cornell.edu/browse/roster/{semester}/subject/{subject}").text

        with open(f'{semester}/{subject}.html', 'a+') as f:
            f.write(reqText)

    if os.path.exists(f'{semester}/{subject}.csv'):
        os.remove(f'{semester}/{subject}.csv')

    roster = SubjectRoster(reqText)
    roster.buildSections()

    if not roster.sections:
        return

    with open(f'{semester}/{subject}.csv', 'a+') as f:
        # print(roster.sections[0][0].keys())
        w = csv.DictWriter(f, roster.sections[0][0].keys())
        w.writeheader()
        for c in roster.sections:
            w.writerows(c)


# generate for all of them then!
url = "https://classes.cornell.edu/browse/roster/"
for i in range(14, 24):
    semesters = []
    semesters.append("FA" + str(i))
    semesters.append("SU" + str(i))
    semesters.append("SP" + str(i))
    for semester in semesters:
        try:
            subjects = subjectIDs(url + semester)
        except Exception:
            print()
            print(f"requesting the subject codes for {semester} failed")
            print()
            continue

        if subjects:
            for subject in subjects:
                generateCSVForSemestersSubject(semester, subject)
        # print(subjects)
        # print(f"just printed the subject ids for {semester}")

# this if for the old format, which is kinda unnecessary at this point; not implemented yet


def subjectIDs_Old_Format(url):
    # not written yet
    page = requests.get(url)
    bsParser = BeautifulSoup(page.text, "lxml")

    ids = []
    for item in bsParser.find_all(name="ul", class_="subject-group"):
        # itemParser = BeautifulSoup(item)
        ids.append(item.find('li').find('a').contents[0])
    return ids
