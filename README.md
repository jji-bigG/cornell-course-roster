# Cornell Roster Data Analysis

### Roster Web Scrapper

Scraps the Cornell rosters to analyze and find interesting maps and insights so as not to constantly check back and forth during the pre-enrollments.

#### Implementation

> Parse the roster pages subject by subject for each semester.

1. Grab the list of semesters that uses this new version of the roster (from fall 2014 to today)
2. For each semester, grab the list of course codes (subjects) that are offered that semester
3. Click into the link of each subject code and Cornell roster will show all the courses that have that subject code.
4. Generate the CSV file that captures all the relevant information for each of the section offerings. They include lecture/discussion, professor, date time location, and more (see actual implementation).
5. The main part: Create a Beautiful Soup parser that filters relevant HTML tag and its attributes (known from playing with the inspect tool on chrome).
6. Cache the HTML information into a relevant folder while traversing through the semesters and subjects in that semester. This way, I do not have to request again.
7. While traversing, add a check on whether I already have these information cached. If so, grab the HTML text instead of sending another request. If not, then send the request but also write the HTML into a file so later when we want to resume we can simply skip the long waiting part.

### Professors Filtering

A lookup system not based on semesters that we originally parsed the roster from, but with professors.

This allows us to check the past offerings from the professor and with the help of Cornell Median Grades, we can better plan the courses to work around and get good GPAs.

#### Implementation

> Create a class that checks all the csv files in that directory and finds a list of lecture type sections that corresponds to that professor. Return that list.

1. Helper function that finds all the distinct professors from the section
2. For each professor, run that class and with the List of CSV rows to grab the relevant datas, save these rows into a file (in the folder called professors).
