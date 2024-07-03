-- schema.sql
DROP TABLE IF EXISTS courses;
DROP TABLE IF EXISTS course_descriptions;

CREATE TABLE IF NOT EXISTS courses (
    course_id INTEGER PRIMARY KEY AUTOINCREMENT,
    semester VARCHAR(63),
    subject VARCHAR(255),
    name VARCHAR(63),
    type VARCHAR(127),
    section_number VARCHAR(127),
    location VARCHAR(255),
    days VARCHAR(127),
    time VARCHAR(127),
    dates VARCHAR(127),
    instructor VARCHAR(255),

    ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_courses_name_semester ON courses(name, semester);
CREATE INDEX IF NOT EXISTS idx_courses_instructor ON courses(instructor);
CREATE INDEX IF NOT EXISTS idx_courses_name ON courses(name);

CREATE TABLE IF NOT EXISTS course_descriptions (
    course_description_id INTEGER PRIMARY KEY AUTOINCREMENT,
    -- foreign key to refer to the specific courses row
    course_id INTEGER,

    description TEXT,
    title VARCHAR(255),
    credits INTEGER,
    prerequisites TEXT,
    when_offered VARCHAR(127),
    combined_with TEXT,
    distribution VARCHAR(255),
    outcomes TEXT,

    ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (course_id) REFERENCES courses(course_id)
);

CREATE INDEX IF NOT EXISTS idx_course_descriptions_id ON course_descriptions(course_description_id);
CREATE INDEX IF NOT EXISTS idx_course_descriptions_course_id ON course_descriptions(course_id);
CREATE INDEX IF NOT EXISTS idx_course_descriptions_title ON course_descriptions(title);
