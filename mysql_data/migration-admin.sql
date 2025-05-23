USE users_db;

CREATE TABLE IF NOT EXISTS administrators (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO administrators (email, password) 
VALUES ('admin@example.com', 'admin123')
ON DUPLICATE KEY UPDATE password = 'admin123';
