-- Use the database
USE users_db;

-- Create users table if not exists
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    firstName VARCHAR(255) NOT NULL,
    lastName VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    birthDate DATE NOT NULL,
    city VARCHAR(255) NOT NULL,
    postalCode VARCHAR(5) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Add some test data
INSERT INTO users (firstName, lastName, email, birthDate, city, postalCode) VALUES
('John', 'Doe', 'john.doe@test.com', '1990-01-01', 'Paris', '75000'),
('Jane', 'Smith', 'jane.smith@test.com', '1985-05-15', 'Lyon', '69000');
