-- TSYS
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

CREATE TABLE tsys_units (
    id serial primary key
    , name varchar(20) not null
    , abbreviation varchar(5) not null
    , type varchar(50) not null -- mass, volume, length, time, datetime, etc
    , created_by VARCHAR(64)
);

CREATE TABLE tsys_categories (
    id serial primary key
    , name varchar(50) not null
    , description varchar(255) not null
    , type varchar(50) not null -- units, skills, resources, tasks, etc
);

CREATE TABLE tsys_tags (
	id SERIAL PRIMARY KEY
	, code_a VARCHAR(255)
	, counter_a INT
	, code_b VARCHAR(255)
	, counter_b INT
	, code_c VARCHAR(255)
	, counter_c INT
	, code_d VARCHAR(255)
	, counter_d INT
	, code_e VARCHAR(255)
	, counter_e INT
	, type VARCHAR(64) not NULL
	, agg VARCHAR(255) GENERATED ALWAYS AS (
	    COALESCE(code_a, '') || COALESCE(CAST(counter_a AS VARCHAR), '') ||
	    COALESCE(code_b, '') || COALESCE(CAST(counter_b AS VARCHAR), '') ||
	    COALESCE(code_c, '') || COALESCE(CAST(counter_c AS VARCHAR), '') ||
	    COALESCE(code_d, '') || COALESCE(CAST(counter_d AS VARCHAR), '') ||
	    COALESCE(code_e, '') || COALESCE(CAST(counter_e AS VARCHAR), '') ||
	    type
	) stored
	, created_by VARCHAR(64)
	, created_at TIMESTAMP DEFAULT NOW()
	, updated_by VARCHAR(64)
	, updated_at TIMESTAMP DEFAULT NOW()
	, CONSTRAINT unique_aggregate_combination UNIQUE (agg)
);



-- TPROD
CREATE TABLE tprod_resources (
    id SERIAL PRIMARY KEY
    , name VARCHAR(255) NOT NULL
    , created_by VARCHAR(64)
    , created_at TIMESTAMP DEFAULT NOW()
    , updated_by VARCHAR(64)
    , updated_at TIMESTAMP DEFAULT NOW()
)

CREATE TABLE tprod_skills (
    id SERIAL PRIMARY KEY
    , name VARCHAR(255) NOT NULL
    , description VARCHAR(255) NOT NULL
    , created_by VARCHAR(64)
    , created_at TIMESTAMP DEFAULT NOW()
    , updated_by VARCHAR(64)
    , updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE tprod_tasks (
    id SERIAL PRIMARY KEY
    , name VARCHAR(255) NOT NULL
    , description VARCHAR(255) NOT NULL
    , duration REAL NOT NULL
    , id_unit INTEGER REFERENCES tsys_units(id) NOT NULL
    , interruptible BOOLEAN DEFAULT FALSE
    , error_margin REAL DEFAULT 0.0
    , created_by VARCHAR(64)
    , created_at TIMESTAMP DEFAULT NOW()
    , updated_by VARCHAR(64)
    , updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE tprod_taskskills (
    id_task INTEGER REFERENCES tprod_tasks(id)
    , id_skill INTEGER REFERENCES tprod_skills(id)
    , PRIMARY key (id_task, id_skill)
);

CREATE TABLE tprod_resourceskills (
    id_resource INTEGER REFERENCES tprod_resources(id)
    , id_skill INTEGER REFERENCES tprod_skills(id)
    , PRIMARY key (id_resource, id_skill)
);