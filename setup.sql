-- Run this in phpMyAdmin (SQL tab) or via the mysql CLI that comes with XAMPP.
-- It creates the database and the users table your Flask app will use.

CREATE DATABASE IF NOT EXISTS bunk_house;

USE bunk_house;

CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ===== Complaint feature: Supervisor + Complaint entities =====
CREATE TABLE IF NOT EXISTS supervisors (
    supervisor_id INT AUTO_INCREMENT PRIMARY KEY,
    supervisor_name VARCHAR(100) NOT NULL,
    phone_no VARCHAR(20),
    email VARCHAR(100)
);

INSERT INTO supervisors (supervisor_name, phone_no, email) VALUES
    ('Mr. Rahman', '01700000001', 'rahman@example.com'),
    ('Ms. Akter', '01700000002', 'akter@example.com'),
    ('Mr. Chowdhury', '01700000003', 'chowdhury@example.com');

CREATE TABLE IF NOT EXISTS complaints (
    complaint_id INT AUTO_INCREMENT PRIMARY KEY,
    description TEXT NOT NULL,
    student_id INT NOT NULL,
    supervisor_id INT NOT NULL,
    status VARCHAR(20) DEFAULT 'Pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES users(id),
    FOREIGN KEY (supervisor_id) REFERENCES supervisors(supervisor_id)
);