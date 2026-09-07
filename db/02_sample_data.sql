INSERT INTO prevently_user (first_name, last_name, date_of_birth, gender) VALUES ('Albert', 'Einstein', '1990-01-01', 'Male');
INSERT INTO prevently_user (first_name, last_name, date_of_birth, gender) VALUES ('Marie', 'Curie', '1992-02-02', 'Female');
INSERT INTO prevently_user (first_name, last_name, date_of_birth, gender) VALUES ('Isaac', 'Newton', '2016-03-03', 'Male');
INSERT INTO prevently_user (first_name, last_name, date_of_birth, gender) VALUES ('Claude', 'Shannon', '1966-04-04', 'Male');

INSERT INTO insurance_provider (i_name) VALUES ('Knappschaft');
INSERT INTO insurance_provider (i_name) VALUES ('Techniker Krankenkasse');
INSERT INTO insurance_provider (i_name) VALUES ('BARMER');
INSERT INTO insurance_provider (i_name) VALUES ('AOK');

INSERT INTO checkup (title, age_min, age_max, required_gender) VALUES ('Hautkrebs Vorsorge', 18, 65, 'Any');
INSERT INTO checkup (title, age_min, age_max, required_gender) VALUES ('Cholesterin-Screening', 20, 70, 'Any');
INSERT INTO checkup (title, age_min, age_max, required_gender) VALUES ('Prostatakrebs Vorsorge', 30, 80, 'Male');
INSERT INTO checkup (title, age_min, age_max, required_gender) VALUES ('Diabetes Check', 25, 75, 'Any');
INSERT INTO checkup (title, age_min, age_max, required_gender) VALUES ('Brustkrebs Vorsorge', 30, 70, 'Female');
INSERT INTO checkup (title, age_min, age_max, required_gender) VALUES ('Darmkrebs Vorsorge', 50, 80, 'Male');

INSERT INTO doctor (d_name, location) VALUES ('Dr. Robert Koch', 'Berlin');
INSERT INTO doctor (d_name, location) VALUES ('Fredekrik Banting', 'Hamburg');
INSERT INTO doctor (d_name, location) VALUES ('Prof. Dr. Carsten Saft', 'Bochum');

INSERT INTO medical_checkup (doctor_id, checkup_id) VALUES (1, 1);
INSERT INTO medical_checkup (doctor_id, checkup_id) VALUES (1, 2);
INSERT INTO medical_checkup (doctor_id, checkup_id) VALUES (2, 3);
INSERT INTO medical_checkup (doctor_id, checkup_id) VALUES (2, 4);
INSERT INTO medical_checkup (doctor_id, checkup_id) VALUES (3, 5);
INSERT INTO medical_checkup (doctor_id, checkup_id) VALUES (3, 6);

INSERT INTO included_checkup (insurance_id, checkup_id, coverage_amount) VALUES (1, 1, 100);
INSERT INTO included_checkup (insurance_id, checkup_id, coverage_amount) VALUES (1, 2, 150);
INSERT INTO included_checkup (insurance_id, checkup_id, coverage_amount) VALUES (2, 3, 200);
INSERT INTO included_checkup (insurance_id, checkup_id, coverage_amount) VALUES (2, 4, 250);
INSERT INTO included_checkup (insurance_id, checkup_id, coverage_amount) VALUES (3, 5, 300);

INSERT INTO completed_checkup (user_id, doctor_id, completed_date, checkup_id) VALUES (1, 1, '2023-01-01', 1);
INSERT INTO completed_checkup (user_id, doctor_id, completed_date, checkup_id) VALUES (2, 1, '2023-02-01', 2);
INSERT INTO completed_checkup (user_id, doctor_id, completed_date, checkup_id) VALUES (3, 2, '2023-03-01', 3);
INSERT INTO completed_checkup (user_id, doctor_id, completed_date, checkup_id) VALUES (4, 2, '2023-04-01', 4);
INSERT INTO completed_checkup (user_id, doctor_id, completed_date, checkup_id) VALUES (1, 3, '2023-05-01', 5);
INSERT INTO completed_checkup (user_id, doctor_id, completed_date, checkup_id) VALUES (2, 3, '2023-06-01', 6);

INSERT INTO appointment (user_id, doctor_id, checkup_date, checkup_id, duration) VALUES (1, 1, '2024-01-01', 1, 30);
INSERT INTO appointment (user_id, doctor_id, checkup_date, checkup_id, duration) VALUES (2, 1, '2024-02-01', 2, 30);
INSERT INTO appointment (user_id, doctor_id, checkup_date, checkup_id, duration) VALUES (3, 2, '2024-03-01', 3, 30);
INSERT INTO appointment (user_id, doctor_id, checkup_date, checkup_id, duration) VALUES (4, 2, '2024-04-01', 4, 30);
