DROP DATABASE IF EXISTS cs122a;
CREATE DATABASE cs122a;
USE cs122a;

-- Entities

CREATE TABLE users
(	
    UCINetID char(50),
    FirstName varchar(20),
    MiddleName varchar(20),
    LastName varchar(20),
    PRIMARY KEY(UCINetID)
);

-- Student is a type of User
CREATE TABLE students
(
    student_id char(50),
    PRIMARY KEY(student_id),
    FOREIGN KEY(student_id) REFERENCES users(UCINetID)
);

-- Administrator is a type of User
CREATE TABLE admins
(
    admin_id char(50),
    PRIMARY KEY(admin_id),
    FOREIGN KEY(admin_id) REFERENCES users(UCINetID)
);


-- Each Admin can have 0 or more shift timings
-- Multi-value attribute
CREATE TABLE Admin_Shift_Timing
(
    AdminID char(8),
    shift_time datetime,
    PRIMARY KEY(AdminID, shift_time),
    FOREIGN KEY(AdminID) REFERENCES admins(admin_id) ON DELETE CASCADE
);




-- Each user can have 1 or more emails 
-- Multi-value attribute 
CREATE TABLE emails
(	
    UCINetID char(50),
    email_address varchar(50),
    PRIMARY KEY(UCINetID, email_address),
    FOREIGN KEY(UCINetID) REFERENCES users(UCINetID) ON DELETE CASCADE
);

CREATE TABLE courses
(
    course_id char(10),
    title varchar(255),
    quarter char(10),
    PRIMARY KEY(course_id)
);

CREATE TABLE projects
(
    project_id char(10),
    course_id char(10) NOT NULL,	
    project_name varchar(20),
    project_description varchar(255),
    PRIMARY KEY(project_id),
    FOREIGN KEY(course_id) REFERENCES courses(course_id) 	-- Fold
);   

CREATE TABLE machines
(
    machine_id char(10),
    name varchar(20),
    IP_address varchar(15),
    operational_status enum('Operational', 'Inactive'),
    location varchar(30),
    PRIMARY KEY(machine_id)
);

CREATE TABLE Hostname
(
    machine_id char(10),
    hostname varchar(15),
    PRIMARY KEY(machine_id, hostname),
    FOREIGN KEY(machine_id) REFERENCES machines(machine_id) 	-- Fold
);


CREATE TABLE Software
(
    software_id char(10),
    software_name varchar(20),
    version_number varchar(10),
    license_key varchar(30),
    PRIMARY KEY(software_id)
);

CREATE TABLE Task
(
    task_id char(10),
    machine_id char(10) NOT NULL,		
    task_description varchar(255),
    priority_level INTEGER,
    begin_time datetime,
    end_time datetime,
    machine_assignment_date date,		-- Relationship attribute of folded relationship
    PRIMARY KEY(task_id),
    FOREIGN KEY(machine_id) references machines(machine_id) 			-- Fold 
);

CREATE TABLE Maintenance_Record
(
    record_id char(10),
    machine_id char(10) NOT NULL,	
    service_date date,
    duration time,
    service_type varchar(10),
    PRIMARY KEY(record_id),
    FOREIGN KEY(machine_id) references machines(machine_id) 		-- Fold
);



-- Relationships

-- Relation for Install relation between Machine/Software/Project
CREATE TABLE SoftwareInstallations
(
    software_id char(10),
    machine_id char(10),
    project_id char(10),
    installation_date date,
    PRIMARY KEY(software_id, machine_id, project_id),
    FOREIGN KEY(software_id) references Software(software_id),
    FOREIGN KEY(machine_id) references machines(machine_id),
    FOREIGN KEY(project_id) references projects(project_id)
);

-- Use Relation between Student/Project/Machine
CREATE TABLE used
(
    UCINetID char(50),
    project_id char(10),
    machine_id char(10),
    start_date date,
    end_date date
);


-- Relation for Manage relation between Admin/Machine
CREATE TABLE manage
(
    UCINetID char(50),
    machine_id char(10)
);
