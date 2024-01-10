CREATE TABLE users (
    google_id VARCHAR(64) PRIMARY KEY
    , google_email VARCHAR(45) NOT NULL
    , google_picture_url VARCHAR(255) NOT NULL
    , google_access_token VARCHAR(255) NOT NULL
    , name VARCHAR(45) NOT NULL
    , locale VARCHAR(8) NOT NULL
    , created_at TIMESTAMP DEFAULT NOW()
    , updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE sessions (
    id SERIAL PRIMARY KEY
    , google_id VARCHAR(64) REFERENCES users(google_id) NOT NULL
    , token VARCHAR(255) NOT NULL
    , user_agent VARCHAR(255) NOT NULL
    , client_ip VARCHAR(45) NOT NULL
    , created_at TIMESTAMP DEFAULT NOW()
    , updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE categories (
    id SERIAL PRIMARY KEY
    , name VARCHAR(45) NOT NULL
    , type VARCHAR(45) NOT NULL
    , created_at TIMESTAMP DEFAULT NOW()
    , created_by VARCHAR(64) NOT NULL
    , updated_at TIMESTAMP DEFAULT NOW()
    , updated_by VARCHAR(64) NOT NULL
);

CREATE TABLE units (
    id SERIAL PRIMARY KEY
    , name VARCHAR(20) NOT NULL
    , abbreviation VARCHAR(5) NOT NULL
    , base INT NOT NULL
    , created_at TIMESTAMP DEFAULT NOW()
    , created_by VARCHAR(64) NOT NULL
    , updated_at TIMESTAMP DEFAULT NOW()
    , updated_by VARCHAR(64) NOT NULL
);
