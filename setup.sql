create table tsys_roles (
	id serial primary key
	, email varchar(45) not null
    , role varchar(20) not null
    , level int not null
)

CREATE TABLE tsys_users (
    id_role SERIAL REFERENCES tsys_roles(id) PRIMARY KEY
    , google_id VARCHAR(64) UNIQUE
    , google_email VARCHAR(45) NOT NULL
    , google_picture_url VARCHAR(255) NOT NULL
    , google_access_token VARCHAR(255) NOT NULL
    , name VARCHAR(45) NOT NULL
    , locale VARCHAR(8) NOT NULL
    , created_at TIMESTAMP DEFAULT NOW()
    , updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE tsys_sessions (
    google_id VARCHAR(64) REFERENCES tsys_users(google_id) PRIMARY KEY
    , id_role INTEGER REFERENCES tsys_roles(id)
    , token VARCHAR(255) NOT NULL
    , user_agent VARCHAR(255) NOT NULL
    , client_ip VARCHAR(45) NOT NULL
    , created_at TIMESTAMP DEFAULT NOW()
    , updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE tsys_symbols (
    id serial primary key
    , short varchar(5) not null
    , long varchar(20) not null
    , base integer not null
    , type varchar(50) not null -- mass, volume, length, time, datetime, etc
);