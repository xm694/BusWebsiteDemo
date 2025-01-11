/* create users for authorisation purpose*/
CREATE TABLE staff (
    id serial PRIMARY KEY NOT NULL,
	username text NOT NULL,
	email text NOT NULL,
	password text NOT NULL
);

INSERT INTO staff (username, email, password)
VALUES
('admin001','admin001@example.com', '$pbkdf2-sha256$29000$itEaAyDkPGeMcY4RYmzNeQ$DnGJOM1DQpqyO93bAD8GHzICFDIc9bah0Jgz0cq2WBU'),
('john_doe1', 'john.doe1@example.com','$2y$10$gLaIRSGf8rzEPoSYmGYNs.EdWOQEf8IuiUM89szeUPRtUYXTf5CvG');

/*create optimised data table busRoute for user searching purpose*/
/*create optimised table for user query*/
CREATE TABLE busRoute (
    route text DEFAULT NULL,
    route_type text DEFAULT NULL,
    start_stop_TSN bigint(20) DEFAULT NULL,
    start_stop text DEFAULT NULL,
    mid_stop_TSN bigint(20) DEFAULT NULL,
    mid_stop text DEFAULT NULL,
    end_stop_TSN bigint(20) DEFAULT NULL,
    end_stop text DEFAULT NULL,
    earliest_start_time text DEFAULT NULL,
    latest_start_time text DEFAULT NULL,
    operator text DEFAULT NULL
);

/* If use mariadb */
/* Mariadb server cannot perform full outer join, hence used left join*/
/* Populate busRoute from raw data using Mariadb*/
INSERT INTO busRoute (
    route,
    route_type,
    start_stop_TSN,
    start_stop,
    mid_stop_TSN,
    mid_stop,
    end_stop_TSN,
    end_stop,
    earliest_start_time,
    latest_start_time,
    operator
)
SELECT 
    COALESCE(start.Route, mid.Route, end.Route) AS route,
    COALESCE(start.Route_Type, mid.Route_Type, end.Route_Type) AS route_type,
    start.TSN AS start_stop_TSN,
    start.TSN_Description AS start_stop,
    mid.TSN AS mid_stop_TSN,
    mid.TSN_Description AS mid_stop,
    end.TSN AS end_stop_TSN,
    end.TSN_Description AS end_stop,
    MIN(start.Sched_Start_Time) AS earliest_start_time,
    MAX(start.Sched_Start_Time) AS latest_start_time,
    COALESCE(start.Operator, mid.Operator, end.Operator) AS operator
FROM PremierDemo.rd_otr_at_nominated_first_stop start
LEFT JOIN PremierDemo.rd_otr_at_mid_stop mid ON start.trip_id = mid.trip_id AND start.Trip_Start_Date = mid.Trip_Start_Date
LEFT JOIN PremierDemo.rd_otr_at_nominated_end_stop end ON start.trip_id = end.trip_id AND start.Trip_Start_Date = end.Trip_Start_Date
GROUP BY 
    COALESCE(start.Route, mid.Route, end.Route),
    start.TSN,
    start.TSN_Description,
    mid.TSN,
    mid.TSN_Description,
    end.TSN,
    end.TSN_Description,
    COALESCE(start.Operator, mid.Operator, end.Operator);

/* IF USE SQL SERVER, full outer join can include null cases in data records */
/* populate data from raw data using sql server */
INSERT INTO busRoute (
    route,
    route_type,
    start_stop_TSN,
    start_stop,
    mid_stop_TSN,
    mid_stop,
    end_stop_TSN,
    end_stop,
    earliest_start_time,
    latest_start_time,
    operator
)
SELECT 
    COALESCE(start.Route, mid.Route, end.Route) AS route,
    COALESCE(start.Route_Type, mid.Route_Type, end.Route_Type) AS route_type,
    start.TSN AS start_stop_TSN,
    start.TSN_Description AS start_stop,
    mid.TSN AS mid_stop_TSN,
    mid.TSN_Description AS mid_stop,
    end.TSN AS end_stop_TSN,
    end.TSN_Description AS end_stop,
    MIN(start.Sched_Start_Time) AS earliest_start_time,
    MAX(start.Sched_Start_Time) AS latest_start_time,
    COALESCE(start.Operator, mid.Operator, end.Operator) AS operator
FROM PremierDemo.rd_otr_at_nominated_first_stop start
FULL OUTER JOIN PremierDemo.rd_otr_at_mid_stop mid ON start.trip_id = mid.trip_id AND start.Trip_Start_Date = mid.Trip_Start_Date
FULL OUTER JOIN PremierDemo.rd_otr_at_nominated_end_stop end ON COALESCE(start.trip_id, mid.trip_id) = end.trip_id AND COALESCE(start.Trip_Start_Date, mid.Trip_Start_Date) = end.Trip_Start_Date
GROUP BY 
    COALESCE(start.Route, mid.Route, end.Route),
    start.TSN,
    start.TSN_Description,
    mid.TSN,
    mid.TSN_Description,
    end.TSN,
    end.TSN_Description;