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

CREATE TABLE recipes (
    id SERIAL PRIMARY KEY
    , name VARCHAR(90) NOT NULL
    , description VARCHAR(255)
    , timing VARCHAR(45)
    , type VARCHAR(45)
    , course VARCHAR(45)
    , created_at TIMESTAMP DEFAULT NOW()
    , created_by VARCHAR(64) NOT NULL
    , updated_at TIMESTAMP DEFAULT NOW()
    , updated_by VARCHAR(64) NOT NULL
);

CREATE TABLE ingredients (
    id SERIAL PRIMARY KEY
    , name VARCHAR(255) NOT NULL
    , description VARCHAR(255)
    , type VARCHAR(45) NOT NULL
    , created_at TIMESTAMP DEFAULT NOW()
    , created_by VARCHAR(64) NOT NULL
    , updated_at TIMESTAMP DEFAULT NOW()
    , updated_by VARCHAR(64) NOT NULL
);

CREATE TABLE recipe_ingredients (
    id SERIAL PRIMARY KEY
    , id_recipe INT REFERENCES recipes(id) NOT NULL
    , id_ingredient INT REFERENCES ingredients(id) NOT NULL
    , quantity INTEGER NOT NULL
    , id_unit INT REFERENCES units(id) NOT NULL
    , created_at TIMESTAMP DEFAULT NOW()
    , created_by VARCHAR(64) NOT NULL
    , updated_at TIMESTAMP DEFAULT NOW()
    , updated_by VARCHAR(64) NOT NULL
);

-- CREATE TABLE recipe_ingredients_nodes (
--     id serial primary key
--     , id_recipe INT REFERENCES recipes(id) NOT NULL
--     , id_recipe_ingredient INT REFERENCES recipe_ingredients(id) NOT NULL
--     , node_uid varchar(36) not null
--     , node_type varchar(50) not null
--     , node_level integer not null
--     , node_json jsonb not null
--     , created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
--     , created_by VARCHAR(64) NOT NULL
--     , updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
--     , updated_by VARCHAR(64) NOT NULL
-- );

-- CREATE TABLE recipe_ingredients_edges (
--     id serial primary key
--     , id_recipe INT REFERENCES recipes(id) NOT NULL
--     , id_recipe_ingredient INT REFERENCES recipe_ingredients(id) NOT NULL
--     , source_uid varchar(36) NOT NULL 
--     , target_uid varchar(36) NOT NULL
--     , created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
--     , created_by VARCHAR(64) NOT NULL
--     , updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
--     , updated_by VARCHAR(64) NOT NULL
-- );

-- CREATE TABLE recipe_files (
--     id serial primary key
--     , id_recipe INT REFERENCES recipes(id) NOT NULL
--     , name varchar(255) NOT NULL
--     , extension varchar(5) NOT NULL
--     , file_bytea BYTEA not null
--     , created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
-- );