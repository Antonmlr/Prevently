# Prevently

Prevently is a small database-backed application that tracks which preventive
medical checkups a user is due for, based on their age, gender and insurance
coverage. It's the term project for the *Databases* course (DBMS_10) at THGA
Bochum.

The system has three parts: a PostgreSQL database, a FastAPI REST API that is
the only component talking to the database, and a tkinter desktop client that
talks to the API over HTTP.

## Repository layout

```
Prevently/
├── api/                        FastAPI REST API
├── db/
│   ├── 01_schema.sql           Database schema (source of truth)
│   ├── 02_sample_data.sql      Init seed data script
│   └── schema.puml             ER diagram (PlantUML), rendered to out/schema.png
├── frontend/                   tkinter desktop client
│   └── src/                    App code 
├── docs/
│   ├── proposal-template/      Project proposal (LaTeX)
│   ├── example-documentation/  Final documentation (LaTeX)
│   └── User-manual             User guide for the frontend UI
├── tests/                      pytest suite (Tests for requirements from proposal)
├── docker-compose.yml          Postgres + API for everyday use
├── docker-compose.test.yml     Disposable Postgres for running the tests
├── pytest.ini
└── Makefile                    Builds the LaTeX documents and the ER diagram
└── style/                      Shared LaTeX style (thga-db.sty)
└── out                         Output folder for docu and ER diagram
```

## Running the system

**Prerequisites:** Docker with the Compose plugin.

1. Create a `.env` file in the repository root, or rename the example:

   ```
   POSTGRES_USER=Your_username
   POSTGRES_PASSWORD=Your_password
   POSTGRES_DB=DB_name
   API_KEY=<choose a secret value>
   ```

2. Start the database and the API:

   ```
   docker compose up -d --build
   ```

   On first start, Postgres automatically loads `db/01_schema.sql`.

   Verify with:

   ```
   docker compose ps
   ```

3. Check that the API is up:

   ```
   curl http://localhost:8000/
   ```

   should return `{"status":"API läuft"}`. The API listens on port `8000`,
   Postgres on port `1904`.

4. Run the desktop client against it:

   ```
   cd frontend
   uv sync
   uv run python -m src
   ```

   On startup it asks for the API's URL and the `X-API-Key` you set above. This
   runs the app directly with Python, not packaged as a `.deb`. To build it as
   a `.deb`, please see the documentation.

## Running the tests

The test suite (`tests/`) uses `pytest` and FastAPI's `TestClient` and runs
against its own, disposable database — never against the one from
`docker-compose.yml` above, since tests freely insert and wipe rows.

1. Start the test database:

   ```
   docker compose -f docker-compose.test.yml up -d
   ```

2. Install the test dependencies and run the suite:

   ```
   cd api
   uv sync --group dev
   cd ..
   uv run --project api pytest
   ```
   This runs the test suite automatically and prints the results directly to your terminal.

3. When you're done, tear the test database back down:

   ```
   docker compose -f docker-compose.test.yml down -v
   ```

## Building the documentation

The proposal and the final documentation are LaTeX documents in `docs/`,
built together with the ER diagram via the `Makefile`.

**Prerequisites:** TeX Live with `latexmk` (`texlive-latex-extra`,
`texlive-lang-german`, `texlive-fonts-recommended`) and `plantuml`.

```
make all
```

produces `out/proposal.pdf`, `out/documentation.pdf` and `out/schema.png`.
`make clean` removes auxiliary build files, `make distclean` removes `out/`
entirely.

## Course context

This repository was built for the Databases course at THGA Bochum and will be used afterwards as a starting point for my idea of a personal checkup assistant. This is a first, minimal working product to show in which direction this project could go.

I would also like to thank [Stephan Bökelmann](https://github.com/MaxClerkwell) for the hands-on learning and the opportunity to bring this project to life in this course.