CREATE DATABASE IF NOT EXISTS bunk_house;

USE bunk_house;

-- =========================================================
-- SUPERVISORS
-- =========================================================

CREATE TABLE IF NOT EXISTS supervisors (
    supervisor_id INT AUTO_INCREMENT PRIMARY KEY,
    supervisor_name VARCHAR(100) NOT NULL,
    phone_no VARCHAR(20),
    email VARCHAR(100)
);

-- USERS

CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'student',
    supervisor_id INT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (supervisor_id)
        REFERENCES supervisors(supervisor_id)
);

-- =========================================================
-- CURRENT SUPERVISORS
-- =========================================================

INSERT INTO supervisors
(supervisor_name, phone_no, email)
VALUES
    ('Mr. Rahman', '01700000001', 'rahman@example.com'),
    ('Ms. Akter', '01700000002', 'akter@example.com'),
    ('Mr. Chowdhury', '01700000003', 'chowdhury@example.com');


-- =========================================================
-- STAFF
-- =========================================================

CREATE TABLE IF NOT EXISTS staff (
    staff_id INT AUTO_INCREMENT PRIMARY KEY,
    staff_name VARCHAR(100) NOT NULL,
    phone_no VARCHAR(20),
    email VARCHAR(100),
    service_type VARCHAR(100),
    status VARCHAR(20) DEFAULT 'Available'
);

-- =========================================================
-- CURRENT STAFF
-- =========================================================

INSERT INTO staff
(staff_name, phone_no, email, service_type, status)
VALUES
    (
        'Staff Member 1',
        '01700000011',
        'staff1@bunkhouse.com',
        'Electrical',
        'Available'
    ),
    (
        'Staff Member 2',
        '01700000012',
        'staff2@bunkhouse.com',
        'Plumbing',
        'Available'
    ),
    (
        'Staff Member 3',
        '01700000013',
        'staff3@bunkhouse.com',
        'General Maintenance',
        'Available'
    );



-- =========================================================
-- SUPERVISOR LOGIN ACCOUNTS
-- =========================================================

INSERT INTO users
(username, email, password, role, supervisor_id)
VALUES
    (
        'supervisor1',
        'supervisor1@bunkhouse.com',
        'supervisor123',
        'supervisor',
        NULL
    ),
    (
        'rahman',
        'rahman@bunkhouse.com',
        'hi',
        'supervisor',
        1
    ),
    (
        'akter',
        'akter@bunkhouse.com',
        'akter123',
        'supervisor',
        2
    ),
    (
        'chowdhury',
        'chowdhury@bunkhouse.com',
        'chowdhury123',
        'supervisor',
        3
    );


-- =========================================================
-- STAFF LOGIN ACCOUNTS
-- =========================================================

INSERT INTO users
(username, email, password, role)
VALUES
    (
        'staff1',
        'staff1@bunkhouse.com',
        'staff1login123',
        'staff'
    );

---- Leave applications

CREATE TABLE IF NOT EXISTS leaves (
    leave_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    supervisor_id INT NOT NULL,
    leave_days INT NOT NULL,
    start_date DATE NOT NULL,
    return_date DATE NOT NULL,
    reason TEXT NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'Pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES users(id),
    FOREIGN KEY (supervisor_id) REFERENCES supervisors(supervisor_id)
);

---- Shared approvals 

CREATE TABLE IF NOT EXISTS approvals (
    approval_id INT AUTO_INCREMENT PRIMARY KEY,
    leave_id INT NULL,
    booking_id INT NULL,
    supervisor_id INT NOT NULL,
    approval_status VARCHAR(20) NOT NULL,
    comments TEXT NULL,
    approval_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (leave_id) REFERENCES leaves(leave_id),
    FOREIGN KEY (supervisor_id) REFERENCES supervisors(supervisor_id)
);

--- 
----create table booking 

CREATE TABLE IF NOT EXISTS bookings (
    booking_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    room_no INT NOT NULL,
    booking_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) DEFAULT 'Pending',
    FOREIGN KEY (student_id) REFERENCES users(id),
    FOREIGN KEY (room_no) REFERENCES rooms(room_no)
);

--- ALTER TABLE approvals
--- ADD CONSTRAINT fk_approvals_booking
--- FOREIGN KEY (booking_id) REFERENCES bookings(booking_id);   


ALTER TABLE approvals
ADD CONSTRAINT chk_one_reference
CHECK (
    (leave_id IS NOT NULL AND booking_id IS NULL)
    OR
    (leave_id IS NULL AND booking_id IS NOT NULL)
); 



-- shaj code start 
-- complaints

CREATE TABLE IF NOT EXISTS complaints (
    complaint_id INT AUTO_INCREMENT PRIMARY KEY,
    description TEXT NOT NULL,
    student_id INT NOT NULL,
    supervisor_id INT NOT NULL,
    room_no VARCHAR(20) NULL,
    status VARCHAR(20) DEFAULT 'Pending',
    remark TEXT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id)
        REFERENCES users(id),
    FOREIGN KEY (supervisor_id)
        REFERENCES supervisors(supervisor_id)
);
-- shaj code end




-- roza code start
-- =========================================================
-- SERVICE REQUESTS / TECHNICAL ISSUES
-- =========================================================

CREATE TABLE IF NOT EXISTS service_requests (

    request_id INT AUTO_INCREMENT PRIMARY KEY,

    student_id INT NOT NULL,

    service_type VARCHAR(100) NOT NULL,

    description TEXT NOT NULL,

    status VARCHAR(20) DEFAULT 'Pending',

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Supervisor responsible for the request
    supervisor_id INT NULL,

    -- Staff member assigned to the request
    staff_id INT NULL,

    -- Time when supervisor approves the request
    approved_at TIMESTAMP NULL,

    -- Time when staff is assigned
    assigned_at TIMESTAMP NULL,

    FOREIGN KEY (student_id)
        REFERENCES users(id),

    FOREIGN KEY (supervisor_id)
        REFERENCES supervisors(supervisor_id),

    FOREIGN KEY (staff_id)
        REFERENCES staff(staff_id)

);

-- roza code end

--- lisan

-- Feedback 
CREATE TABLE IF NOT EXISTS feedback (
    feedback_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    rating INT NOT NULL,
    comments TEXT,
    feedback_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES users(id)
);

-- Meal 

CREATE TABLE IF NOT EXISTS meal_schedule (
    schedule_id INT AUTO_INCREMENT PRIMARY KEY,
    day_name VARCHAR(10) NOT NULL,
    meal_type VARCHAR(20) NOT NULL,
    item_description VARCHAR(150) NOT NULL
);

INSERT INTO meal_schedule (day_name, meal_type, item_description) VALUES
('Saturday','Breakfast','Bread, Egg, Banana'),
('Saturday','Lunch','Rice, Fish Curry, Vegetables'),
('Saturday','Snack','Tea, Biscuits'),
('Saturday','Dinner','Rice, Chicken Curry, Dal'),
('Sunday','Breakfast','Paratha, Egg, Milk'),
('Sunday','Lunch','Rice, Beef Curry, Salad'),
('Sunday','Snack','Singara, Tea'),
('Sunday','Dinner','Rice, Fish Curry, Dal'),
('Monday','Breakfast','Bread, Jam, Banana'),
('Monday','Lunch','Rice, Chicken Curry, Vegetables'),
('Monday','Snack','Tea, Biscuits'),
('Monday','Dinner','Khichuri, Egg'),

('Tuesday','Breakfast','Paratha, Vegetable Curry'),
('Tuesday','Lunch','Rice, Fish Curry, Dal'),
('Tuesday','Snack','Muri, Tea'),
('Tuesday','Dinner','Rice, Beef Curry, Salad'),
('Wednesday','Breakfast','Bread, Egg, Milk'),
('Wednesday','Lunch','Rice, Chicken Curry, Dal'),
('Wednesday','Snack','Tea, Biscuits'),
('Wednesday','Dinner','Rice, Fish Curry, Vegetables'),
('Thursday','Breakfast','Paratha, Egg, Banana'),
('Thursday','Lunch','Rice, Beef Curry, Vegetables'),
('Thursday','Snack','Singara, Tea'),
('Thursday','Dinner','Rice, Chicken Curry, Dal'),
('Friday','Breakfast','Semai, Bread'),
('Friday','Lunch','Polao, Chicken Roast, Salad'),
('Friday','Snack','Tea, Biscuits'),
('Friday','Dinner','Rice, Fish Curry, Dal');

-- ===== Room Booking feature =====
CREATE TABLE IF NOT EXISTS rooms (
    room_no INT PRIMARY KEY,
    capacity INT DEFAULT 4,
    occupancy INT DEFAULT 0
);

INSERT INTO rooms (room_no, capacity, occupancy) VALUES
(101,4,0),(102,4,0),(103,4,0),(104,4,0),(105,4,0),
(106,4,0),(107,4,0),(108,4,0),(109,4,0),(110,4,0),
(111,4,0),(112,4,0),(113,4,0),(114,4,0),(115,4,0);
