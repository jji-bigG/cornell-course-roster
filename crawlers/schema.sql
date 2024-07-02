-- schema.sql
DROP TABLE IF EXISTS subjects;
DROP TABLE IF EXISTS courses;
DROP TABLE IF EXISTS course_descriptions;

CREATE TABLE IF NOT EXISTS subjects (
    subject_id INTEGER PRIMARY KEY AUTOINCREMENT,
    semester TEXT,
    subject_code TEXT,

    ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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

    ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS course_descriptions (
    course_description_id INTEGER PRIMARY KEY AUTOINCREMENT,
    -- foreign key to refer to the specific courses row
    course_id INTEGER,

    description TEXT,
    title TEXT,
    credits INTEGER,
    prerequisites TEXT,
    when_offered TEXT,
    combined_with TEXT,
    distribution TEXT,
    outcomes TEXT,

    ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (course_id) REFERENCES courses(course_id)
);
