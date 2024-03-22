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
    , reference varchar(50) not null -- units, skills, resources, tasks, etc
    , status BOOLEAN DEFAULT TRUE
	, created_by VARCHAR(64)
	, created_at TIMESTAMP DEFAULT NOW()
	, updated_by VARCHAR(64)
	, updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE tsys_keywords (
    id_object INTEGER
    , reference VARCHAR(15) NOT NULL
    , keyword VARCHAR(30) NOT NULL
    , CONSTRAINT tsys_keywords_unique_constraint UNIQUE (id_object, reference, keyword)
);

CREATE TABLE tsys_nodes (
    id serial primary key
    , id_object INTEGER NOT NULL
    , reference VARCHAR(50) NOT NULL
    , type VARCHAR(50) DEFAULT 'default'
    , uuid VARCHAR(36) NOT NULL
    , layer INTEGER NOT NULL
    , position VARCHAR(255) NOT NULL
    , ancestors TEXT
    , CONSTRAINT tsys_nodes_unique_constraint UNIQUE (uuid, reference, id_object)
)

CREATE TABLE tsys_edges (
    id serial primary key
    , id_object INTEGER NOT NULL
    , reference VARCHAR(50) NOT NULL -- tag reference
    , source_uuid VARCHAR(36) NOT NULL
    , target_uuid VARCHAR(36) NOT NULL
    , type VARCHAR(50) DEFAULT 'default'
    , CONSTRAINT tsys_edges_unique_constraint UNIQUE (source_uuid, target_uuid, reference, id_object)
)



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

create table tprod_producttags (
	id serial primary key
	, category VARCHAR(3)
	, registry_counter INTEGER
	, produced_counter INTEGER
	, subcategory VARCHAR(3)
    , CONSTRAINT tprod_producttags_unique_constraint UNIQUE (category, registry_counter, produced_counter, subcategory)
);

CREATE TABLE tprod_routes (
    id_tag INTEGER REFERENCES tprod_producttags(id)
    , id_task INTEGER REFERENCES tprod_tasks(id)
    , node_uuid VARCHAR(36) NOT NULL
    , created_by VARCHAR(64)
    , created_at TIMESTAMP DEFAULT NOW()
    , updated_by VARCHAR(64)
    , updated_at TIMESTAMP DEFAULT NOW()
    , PRIMARY key (id_tag, id_task)
);

CREATE TABLE tprod_products (
    id SERIAL PRIMARY KEY
    , id_tag INTEGER REFERENCES tprod_producttags(id)
    , name VARCHAR(100) NOT NULL
    , description VARCHAR(255) NOT NULL
    , weight REAL NOT NULL
    , id_unit_mass INTEGER REFERENCES tsys_units(id) NOT NULL
    , height REAL NOT NULL
    , width REAL NOT NULL
    , depth REAL NOT NULL
    , id_unit_volume INTEGER REFERENCES tsys_units(id) NOT NULL
    , created_by VARCHAR(64)
    , created_at TIMESTAMP DEFAULT NOW()
    , updated_by VARCHAR(64)
    , updated_at TIMESTAMP DEFAULT NOW()
);