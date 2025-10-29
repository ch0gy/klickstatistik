/*
	Justin Barthel
	-------------------------------------------------------------------------------------- 
	Projekt: Campus Statistik Tool
	-------------------------------------------------------------------------------------- 
	IT Lehrlabor ETH Zürich| 01.02.2023
*/
# -------------------------------------------------------------------------------------

# Löscht die Datenbank campus_statistic_tool
DROP DATABASE IF EXISTS campus_statistic_tool;

# Erstellt die Datenbank campus_statistic_tool
CREATE DATABASE campus_statistic_tool; 

# zur DB wechseln
USE campus_statistic_tool;
 

# -------------------------------------------------------------------------------------

# Tabelle campusinfo definieren

# Tabelle löschen falls sie bereits existiert
DROP TABLE IF EXISTS campusinfo;

# Tabelle erstellen
CREATE TABLE campusinfo (
	id BIGINT NOT NULL UNIQUE AUTO_INCREMENT,
	name VARCHAR(100) NOT NULL UNIQUE,
	PRIMARY KEY(id)
);


# -------------------------------------------------------------------------------------

# Tabelle subject definieren

# Tabelle löschen falls sie bereits existiert
DROP TABLE IF EXISTS subject;

# Tabelle rstellen
CREATE TABLE subject (
	id BIGINT NOT NULL UNIQUE AUTO_INCREMENT,
	name VARCHAR(100) NOT NULL UNIQUE,
	color VARCHAR(6) NOT NULL,
	image VARCHAR(255),
	PRIMARY KEY(id)
);
# -------------------------------------------------------------------------------------

# Tabelle campusinfo_subject definieren

# Tabelle löschen falls sie bereits existiert
DROP TABLE IF EXISTS campusinfo_subject;

# Tabelle erstellen
CREATE TABLE campusinfo_subject (
    id BIGINT NOT NULL UNIQUE AUTO_INCREMENT,
	campusinfo_id BIGINT NOT NULL ,
	subject_id BIGINT NOT NULL ,
    PRIMARY KEY(id),
    FOREIGN KEY(campusinfo_id) REFERENCES campusinfo(id),
    FOREIGN KEY(subject_id) REFERENCES subject(id)
);


# -------------------------------------------------------------------------------------

# Tabelle campusinfo_log definieren

# Tabelle löschen falls sie bereits exsistiert
DROP TABLE IF EXISTS campusinfo_log;

# Tabelle erstellen
CREATE TABLE campusinfo_log (
	id BIGINT NOT NULL UNIQUE AUTO_INCREMENT,
	timestamp DATETIME NOT NULL,
	campusinfo_id BIGINT NOT NULL,
	subject_id BIGINT NOT NULL,
	PRIMARY KEY(id),
	FOREIGN KEY(campusinfo_id) REFERENCES campusinfo(id),
    FOREIGN KEY(subject_id) REFERENCES subject(id)
);

# -------------------------------------------------------------------------------------

# Tabelle account definieren

# Tabelle löschen falls sie bereits existiert
DROP TABLE IF EXISTS account;

# Tabelle erstellen;
CREATE TABLE account (
	id 			    BIGINT 	NOT NULL UNIQUE AUTO_INCREMENT,
	username 		VARCHAR(50) NOT NULL UNIQUE,
	password 	    VARCHAR(255) NOT NULL UNIQUE,
	firstname 		VARCHAR(50) NOT NULL,					
	surname 		VARCHAR(100) NOT NULL,	
	PRIMARY KEY(id)
);

# -------------------------------------------------------------------------------------

INSERT INTO campusinfo (name)
VALUES
("Empfang"),
("Zentrum"),
("Hönggerberg");

INSERT INTO subject (name, color)
VALUES
("Print+Publish", "08407E"),
("Auskunft", "215CAF"),
("Anmeldung", "365213"),
("Post", "A7117A"),
("Orientierung", "007894"),
("Finanzdienst", "627313"),
("Parking", "6F6F6F");

INSERT INTO campusinfo_subject (campusinfo_id, subject_id)
VALUES
(1, 2),
(1, 5),
(1, 3);

INSERT INTO campusinfo_subject (campusinfo_id, subject_id)
VALUES
(2, 2),
(2, 4),
(2, 6);


INSERT INTO campusinfo_subject (campusinfo_id, subject_id)
VALUES
(3, 1),
(3, 2),
(3, 3);

INSERT INTO account (username, password, firstname, surname)
VALUES
("admin", "$5$rounds=535000$Jp4vS1ahNLXhRVD8$39WN3.deuWiqjxeKHbbnNIwlhIU7XWwfvouN/Bt4Yq6", "David", "Weisstanner");

INSERT INTO campusinfo_log (timestamp, campusinfo_id, subject_id)
VALUES
("2020-01-01 08:00:00", 1, 2),
("2020-01-01 08:00:00", 1, 5),
("2020-01-01 08:00:00", 1, 3),
("2020-01-01 08:00:00", 2, 2),
("2020-01-01 08:00:00", 2, 4),
("2020-01-01 08:00:00", 2, 6),
("2020-01-01 08:00:00", 3, 1),
("2020-01-01 08:00:00", 3, 2),
("2020-01-01 08:00:00", 3, 3),
("2020-01-01 08:00:00", 1, 2),
("2020-01-01 08:00:00", 1, 5),
("2020-01-01 08:00:00", 1, 3),
("2020-01-01 08:00:00", 2, 2),
("2020-01-01 08:00:00", 2, 4),
("2020-01-01 08:00:00", 2, 6),
("2020-01-01 08:00:00", 3, 1),
("2020-01-01 08:00:00", 3, 2),
("2020-01-01 08:00:00", 3, 3),
("2020-01-01 08:00:00", 1, 2),
("2020-01-01 08:00:00", 1, 5),
("2020-01-01 08:00:00", 1, 3),
("2020-01-01 08:00:00", 2, 2),
("2020-01-01 08:00:00", 2, 4),
("2020-01-01 08:00:00", 2, 6),
("2020-01-01 08:00:00", 3, 1),
("2020-01-01 08:00:00", 1, 5),
("2020-01-01 08:00:00", 1, 3),
("2020-01-01 08:00:00", 2, 2),
("2020-01-01 08:00:00", 2, 4),
("2020-01-01 08:00:00", 2, 6),
("2020-01-01 08:00:00", 3, 1),
("2020-01-01 08:00:00", 3, 2),
("2020-01-01 08:00:00", 3, 3),
("2020-01-01 08:00:00", 1, 2),
("2020-01-01 08:00:00", 1, 5),
("2020-01-01 08:00:00", 1, 3),
("2020-01-01 08:00:00", 2, 2),
("2020-01-01 08:00:00", 2, 4),
("2020-01-01 08:00:00", 2, 6),
("2020-01-01 08:00:00", 3, 1),
("2020-01-01 08:00:00", 3, 2),
("2020-01-01 08:00:00", 3, 3),
("2020-01-01 08:00:00", 1, 2),
("2020-01-01 08:00:00", 1, 5),
("2020-01-01 08:00:00", 1, 3),
("2020-01-01 08:00:00", 2, 2),
("2020-01-01 08:00:00", 2, 4),
("2020-01-01 08:00:00", 2, 6),
("2020-01-01 08:00:00", 3, 1),
("2020-01-01 08:00:00", 1, 5),
("2020-01-01 08:00:00", 1, 3),
("2020-01-01 08:00:00", 2, 2),
("2020-01-01 08:00:00", 2, 4),
("2020-01-01 08:00:00", 2, 6),
("2020-01-01 08:00:00", 3, 1),
("2020-01-01 08:00:00", 3, 2),
("2020-01-01 08:00:00", 3, 3),
("2020-01-01 08:00:00", 1, 2),
("2020-01-01 08:00:00", 1, 5),
("2020-01-01 08:00:00", 1, 3),
("2020-01-01 08:00:00", 2, 2),
("2020-01-01 08:00:00", 2, 4),
("2020-01-01 08:00:00", 2, 6),
("2020-01-01 08:00:00", 3, 1),
("2020-01-01 08:00:00", 3, 2),
("2020-01-01 08:00:00", 3, 3),
("2020-01-01 08:00:00", 1, 2),
("2020-01-01 08:00:00", 1, 5),
("2020-01-01 08:00:00", 1, 3),
("2020-01-01 08:00:00", 2, 2),
("2020-01-01 08:00:00", 2, 4),
("2020-01-01 08:00:00", 2, 6),
("2020-01-01 08:00:00", 3, 1),
("2020-01-01 08:00:00", 1, 5),
("2020-01-01 08:00:00", 1, 3),
("2020-01-01 08:00:00", 2, 2),
("2020-01-01 08:00:00", 2, 4),
("2020-01-01 08:00:00", 2, 6),
("2020-01-01 08:00:00", 3, 1),
("2020-01-01 08:00:00", 3, 2),
("2020-01-01 08:00:00", 3, 3),
("2020-01-01 08:00:00", 1, 2),
("2020-01-01 08:00:00", 1, 5),
("2020-01-01 08:00:00", 1, 3),
("2020-01-01 08:00:00", 2, 2),
("2020-01-01 08:00:00", 2, 4),
("2020-01-01 08:00:00", 2, 6),
("2020-01-01 08:00:00", 3, 1),
("2020-01-01 08:00:00", 3, 2),
("2020-01-01 08:00:00", 3, 3),
("2020-01-01 08:00:00", 1, 2),
("2020-01-01 08:00:00", 1, 5),
("2020-01-01 08:00:00", 1, 3),
("2020-01-01 08:00:00", 2, 2),
("2020-01-01 08:00:00", 2, 4),
("2020-01-01 08:00:00", 2, 6),
("2020-01-01 08:00:00", 3, 1);

SELECT COUNT(*) FROM campusinfo_log;

SELECT table_schema "campus_statistic_tool",
        ROUND(SUM(data_length + index_length) / 1024 / 1024, 1) "DB Size in MB" 
FROM information_schema.tables 
GROUP BY table_schema; 