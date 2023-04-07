-- transactional: false

CREATE TABLE IF NOT EXISTS sensor_data (
    time TIMESTAMPTZ NOT NULL,
    sensor_id INTEGER NOT NULL,
    temperature DOUBLE PRECISION,
    humidity DOUBLE PRECISION,
    velocity DOUBLE PRECISION,
    battery_level DOUBLE PRECISION,
    PRIMARY KEY (time, sensor_id)
);