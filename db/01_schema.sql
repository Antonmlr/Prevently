CREATE TABLE prevently_user (
    user_id          INTEGER     PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    first_name       TEXT NOT NULL,
    last_name        TEXT NOT NULL,
    date_of_birth    DATE        NOT NULL,
    gender           TEXT NOT NULL
);

CREATE TABLE insurance_provider (
    insurance_id     INTEGER     PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    i_name           TEXT NOT NULL
);

CREATE TABLE checkup (
    checkup_id       INTEGER     PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    title            TEXT NOT NULL,
    age_min          INTEGER     NOT NULL CHECK (age_min >= 0),
    age_max          INTEGER     NOT NULL CHECK (age_max > age_min),
    required_gender  TEXT NOT NULL
);

CREATE TABLE doctor (
    doctor_id        INTEGER     PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    d_name          TEXT NOT NULL,
    location         TEXT NOT NULL
);

CREATE TABLE medical_checkup (
    medical_id       INTEGER     PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    doctor_id        INTEGER     NOT NULL,
    checkup_id       INTEGER     NOT NULL,
    FOREIGN KEY (doctor_id) REFERENCES doctor(doctor_id)
        ON DELETE RESTRICT ON UPDATE CASCADE,
    FOREIGN KEY (checkup_id) REFERENCES checkup(checkup_id)
        ON DELETE RESTRICT ON UPDATE CASCADE
);

CREATE TABLE included_checkup (
    coverage_id      INTEGER     PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    insurance_id     INTEGER     NOT NULL,
    checkup_id       INTEGER     NOT NULL,
    coverage_amount   INTEGER     NOT NULL CHECK (coverage_amount >= 0),
    FOREIGN KEY (insurance_id) REFERENCES insurance_provider(insurance_id)
        ON DELETE RESTRICT ON UPDATE CASCADE,
    FOREIGN KEY (checkup_id) REFERENCES checkup(checkup_id)
        ON DELETE RESTRICT ON UPDATE CASCADE
);

CREATE TABLE completed_checkup (
    completed_id    INTEGER     PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    user_id         INTEGER     NOT NULL,
    doctor_id       INTEGER     NOT NULL,
    completed_date   DATE        NOT NULL,
    checkup_id      INTEGER     NOT NULL,
    FOREIGN KEY (user_id) REFERENCES prevently_user(user_id)
        ON DELETE RESTRICT ON UPDATE CASCADE,
    FOREIGN KEY (doctor_id) REFERENCES doctor(doctor_id)
        ON DELETE RESTRICT ON UPDATE CASCADE,
    FOREIGN KEY (checkup_id) REFERENCES checkup(checkup_id)
        ON DELETE RESTRICT ON UPDATE CASCADE
);

CREATE TABLE appointment (
    appointment_id   INTEGER     PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    user_id          INTEGER     NOT NULL,
    doctor_id        INTEGER     NOT NULL,
    checkup_id       INTEGER     NOT NULL,
    checkup_date      DATE        NOT NULL,
    duration          INTEGER     NOT NULL CHECK (duration > 0),
    FOREIGN KEY (user_id) REFERENCES prevently_user(user_id)
        ON DELETE RESTRICT ON UPDATE CASCADE,
    FOREIGN KEY (doctor_id) REFERENCES doctor(doctor_id)
        ON DELETE RESTRICT ON UPDATE CASCADE,
    FOREIGN KEY (checkup_id) REFERENCES checkup(checkup_id) 
        ON DELETE RESTRICT ON UPDATE CASCADE
);