-- Use the database
USE users_db;

-- Create administrators table if not exists
CREATE TABLE IF NOT EXISTS administrators (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert administrator record
INSERT INTO administrators (email, password, role)
VALUES ('loise.fenoll@ynov.com', 'ANKymoUTFu4rbybmQ9Mt', 'admin');