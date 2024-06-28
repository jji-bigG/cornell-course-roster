-- schema.sql
DROP TABLE IF EXISTS subjects;
DROP TABLE IF EXISTS courses;
DROP TABLE IF EXISTS course_descriptions;

CREATE TABLE IF NOT EXISTS subjects (
    subject_id INTEGER PRIMARY KEY AUTOINCREMENT,
    semester TEXT,
    subject_code TEXT
);

CREATE TABLE IF NOT EXISTS courses (
    course_id INTEGER PRIMARY KEY AUTOINCREMENT,
    semester TEXT,
    subject TEXT,
    name TEXT,
    type TEXT,
    section_number TEXT,
    location TEXT,
    days TEXT,
    time TEXT,
    dates TEXT,
    instructor TEXT
);

CREATE TABLE IF NOT EXISTS course_descriptions (
    course_description_id INTEGER PRIMARY KEY AUTOINCREMENT,
    course_code TEXT,
    description TEXT
);
