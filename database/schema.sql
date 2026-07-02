-- ============================================================
-- Internship Portal - MySQL Schema
-- ============================================================

CREATE DATABASE IF NOT EXISTS internship_portal;
USE internship_portal;

-- ------------------------------------------------------------
-- 1. USERS  (shared table for all 3 roles)
-- ------------------------------------------------------------
CREATE TABLE users (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    full_name       VARCHAR(100)    NOT NULL,
    email           VARCHAR(120)    NOT NULL UNIQUE,
    password_hash   VARCHAR(255)    NOT NULL,
    role            ENUM('student', 'teacher', 'admin') NOT NULL DEFAULT 'student',
    is_active       BOOLEAN         DEFAULT TRUE,
    must_reset_password BOOLEAN     DEFAULT FALSE,  -- forces password change on first login (used for teacher/admin accounts created by admin)
    created_at      TIMESTAMP       DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP       DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- ------------------------------------------------------------
-- 2. STUDENT PROFILES (extra fields only students need)
-- ------------------------------------------------------------
CREATE TABLE student_profiles (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    user_id         INT NOT NULL UNIQUE,
    college_name    VARCHAR(150),
    course          VARCHAR(100),
    year_of_study   VARCHAR(20),
    phone           VARCHAR(20),
    resume_path     VARCHAR(255),          -- path to uploaded resume file
    internship_domain VARCHAR(100),         -- e.g. "Web Dev", "Data Science"
    application_status ENUM('not_applied','applied','under_review','accepted','rejected') DEFAULT 'not_applied',
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- ------------------------------------------------------------
-- 3. TEACHER PROFILES
-- ------------------------------------------------------------
CREATE TABLE teacher_profiles (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    user_id         INT NOT NULL UNIQUE,
    department      VARCHAR(100),
    designation     VARCHAR(100),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- ------------------------------------------------------------
-- 4. CONVERSATIONS  (one per student; tracks who/what is handling it)
-- ------------------------------------------------------------
CREATE TABLE conversations (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    student_id      INT NOT NULL,
    assigned_teacher_id INT NULL,           -- NULL until a teacher picks it up
    handled_by      ENUM('bot','teacher') DEFAULT 'bot',
    status          ENUM('open','escalated','resolved','closed') DEFAULT 'open',
    subject         VARCHAR(150),            -- short summary, e.g. "Eligibility query"
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (assigned_teacher_id) REFERENCES users(id) ON DELETE SET NULL
);

-- ------------------------------------------------------------
-- 5. MESSAGES  (every message in a conversation - bot, student, or teacher)
-- ------------------------------------------------------------
CREATE TABLE messages (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    conversation_id INT NOT NULL,
    sender_type     ENUM('student','bot','teacher') NOT NULL,
    sender_id       INT NULL,                -- NULL when sender_type = 'bot'
    message_text    TEXT NOT NULL,
    is_read         BOOLEAN DEFAULT FALSE,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE
);

-- ------------------------------------------------------------
-- 6. ENQUIRIES  (structured ticket created when bot escalates)
-- ------------------------------------------------------------
CREATE TABLE enquiries (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    conversation_id INT NOT NULL,
    student_id      INT NOT NULL,
    category        VARCHAR(100),            -- e.g. "Eligibility", "Document Issue", "Stipend"
    summary         TEXT,                    -- bot-generated summary of the issue
    priority        ENUM('low','medium','high') DEFAULT 'medium',
    status          ENUM('pending','in_progress','resolved') DEFAULT 'pending',
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolved_at     TIMESTAMP NULL,
    FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE,
    FOREIGN KEY (student_id) REFERENCES users(id) ON DELETE CASCADE
);

-- ------------------------------------------------------------
-- 7. ACTIVITY LOGS  (for admin oversight / DBA monitoring)
-- ------------------------------------------------------------
CREATE TABLE activity_logs (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    user_id         INT NULL,
    action          VARCHAR(255) NOT NULL,   -- e.g. "Logged in", "Created teacher account"
    details         TEXT,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
);

-- ------------------------------------------------------------
-- Indexes for performance
-- ------------------------------------------------------------
CREATE INDEX idx_conversations_student ON conversations(student_id);
CREATE INDEX idx_conversations_teacher ON conversations(assigned_teacher_id);
CREATE INDEX idx_messages_conversation ON messages(conversation_id);
CREATE INDEX idx_enquiries_status ON enquiries(status);
