-- ============================================================
-- Seed Data - run AFTER schema.sql
-- Creates one default admin account so you can log in for the
-- first time and create teacher accounts from the admin dashboard.
-- ============================================================

USE internship_portal;

-- Default admin login:
--   email:    admin@firm.com
--   password: Admin@123   (CHANGE THIS after first login)
--
-- The password_hash below is a placeholder. Run the Python helper
-- `python utils/generate_password_hash.py` to generate a real hash
-- and paste it here, OR just let app.py auto-seed this on first run
-- (see app.py create_default_admin() function).

INSERT INTO users (full_name, email, password_hash, role, must_reset_password)
VALUES ('System Admin', 'admin@firm.com', 'REPLACE_WITH_REAL_HASH', 'admin', TRUE);
