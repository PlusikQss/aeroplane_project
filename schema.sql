CREATE TABLE countries (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL
);

CREATE TABLE aeroplanes (
    id SERIAL PRIMARY KEY,
    icao24 VARCHAR(10),
    callsign VARCHAR(20),
    velocity FLOAT,
    altitude FLOAT,
    country_id INTEGER REFERENCES countries(id) ON DELETE CASCADE
);