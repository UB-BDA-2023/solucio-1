-- transactional: false

CREATE MATERIALIZED VIEW sensor_data_daily
WITH (timescaledb.continuous) AS
SELECT time_bucket('1 day', time) AS bucket,
       sensor_id,
       AVG(temperature) AS temperature,
       AVG(humidity) AS humidity,
       AVG(velocity) AS velocity,
       AVG(battery_level) AS battery_level
FROM sensor_data
GROUP BY bucket, sensor_id;