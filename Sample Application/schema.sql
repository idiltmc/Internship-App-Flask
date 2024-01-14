CREATE DATABASE IF NOT EXISTS cs353hw4db;
USE cs353hw4db;

CREATE TABLE student (
    sid CHAR(6) PRIMARY KEY,
    sname VARCHAR(50) NOT NULL,
    bdate DATE NOT NULL,
    dept CHAR(2) NOT NULL,
    syear VARCHAR(15) NOT NULL,
    gpa FLOAT NOT NULL
);

CREATE TABLE company (
    cid CHAR(5) PRIMARY KEY,
    cname VARCHAR(20) NOT NULL,
    quota INT NOT NULL,
    gpa_threshold FLOAT NOT NULL,
    city VARCHAR(20) NOT NULL
);

CREATE TABLE applied (
    sid CHAR(6),
    cid CHAR(5),
    PRIMARY KEY (sid, cid),
    FOREIGN KEY (sid) REFERENCES student(sid),
    FOREIGN KEY (cid) REFERENCES company(cid)
);

INSERT INTO student (sid, sname, bdate, dept, syear, gpa)
VALUES
    ('S101','Ali','1999-07-15', 'CS', 'sophomore', 2.92),
    ('S102','Veli','2002-01-17', 'EE', 'junior', 3.96),
    ('S103','Ayşe','2004-02-11', 'IE', 'freshman', 3.30),
    ('S104','Mehmet','2003-05-23', 'CS', 'junior', 3.07);

INSERT INTO company (cid, cname, quota, gpa_threshold, city)
VALUES
    ('C101', 'tubitak', 10, 2.5, 'Ankara'),
    ('C102', 'bist', 2, 2.80, 'Istanbul'),
    ('C103', 'aselsan', 3, 3.0, 'Ankara'),
    ('C104', 'thy', 5, 2.40, 'Istanbul'),
    ('C105', 'milsoft', 6, 2.5, 'Ankara'),
    ('C106', 'amazon', 1, 3.80, 'Palo Alto'),
    ('C107', 'tai', 4, 3.0, 'Ankara');

INSERT INTO applied (sid, cid)
VALUES 
    ('S101', 'C101'),
    ('S101', 'C102'),
    ('S101', 'C104'),
    ('S102', 'C106'),
    ('S103', 'C104'),
    ('S103', 'C107'),
    ('S104', 'C102'),
    ('S104', 'C107');
