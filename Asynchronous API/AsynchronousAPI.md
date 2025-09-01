# Developing and Testing an Asynchronous API with FastAPI and Pytest

**Dependencies:**

1. FastAPI v0.88.0
2. Docker v20.10.21
3. Python v3.11.0
4. pytest v7.2.0
5. Databases v0.6.2

## Objectives

By the end of this tutorial you should be able to:

1. Develop an asynchronous RESTful API with Python and FastAPI
2. Practice Test-driven Development
3. Test a FastAPI app with pytest
4. Interact with a Postgres database asynchronously
5. Containerize FastAPI and Postgres inside a Docker container
6. Parameterize test functions and mock functionality in tests with pytest
7. Document a RESTful API with Swagger/OpenAPI

## FastAPI

FastAPI is a modern, high-performance, batteries-included Python web framework that's perfect for building RESTful APIs. It can handle both synchronous and asynchronous requests and has built-in support for data validation, JSON serialization, authentication and authorization, and OpenAPI (version 3.0.2 as of writing) documentation.

1. It takes advantage of Python type hints for parameter declaration which enables data validation (via Pydantic) and OpenAPI/Swagger documentation.
2. Built on top of Starlette, it supports the development of asynchronous APIs.
3. It's fast. Since async is much more efficient than the traditional synchronous threading model, it can compete with Node and Go with regards to performance.

**Note:**

Unlike Django or Flask, FastAPI does not have a built-in development server. So, we'll use Uvicorn, an ASGI server, to serve up FastAPI.

### Dockerfile

So, we started with an Alpine-based Docker image for Python 3.13+.3. We then set a working directory along with two environment variables:

1. `PYTHONDONTWRITEBYTECODE`: Prevents Python from writing pyc files to disc (equivalent to `python -B` option)
2. `PYTHONUNBUFFERED`: Prevents Python from buffering stdout and stderr (equivalent to `python -u` option)

Here’s a breakdown of what these two Python environment variables do:

---

### 1. `PYTHONDONTWRITEBYTECODE`

**Purpose:** Prevents Python from writing `.pyc` files (compiled bytecode) to disk.

* **What are `.pyc` files?** When Python runs a script, it compiles it into bytecode (a lower-level, platform-independent representation of the code) and saves it as a `.pyc` file (usually in a `__pycache__` directory). This helps speed up subsequent runs of the script.
* **Why disable it?** Useful when:

  * You want a clean working directory (e.g., in a container or CI/CD pipeline).
  * You don't want unnecessary files cluttering your environment.
  * You're debugging and don't want stale bytecode files causing confusion.

**How to use:**

```bash
export PYTHONDONTWRITEBYTECODE=1
python script.py
```

Equivalent to running:

```bash
python -B script.py
```

---

### 2. `PYTHONUNBUFFERED`

**Purpose:** Disables output buffering for `stdout` and `stderr`.

* **Buffered vs. unbuffered output:**

  * By default, Python buffers output to `stdout` and `stderr`, which means it collects output in memory and writes it in chunks (for performance).
  * When unbuffered, Python writes output immediately—this is especially useful in real-time logging or when using containers and you want logs to show up instantly.

**Why use it?**

* In Docker containers, CI/CD logs, or long-running scripts where you want real-time output.
* Avoids delays or missing output when the program crashes before flushing buffers.

**How to use:**

```bash
export PYTHONUNBUFFERED=1
python script.py
```

Equivalent to:

```bash
python -u script.py
```

---

### Summary Table

| Environment Variable        | Effect                                       | CLI Equivalent |
| --------------------------- | -------------------------------------------- | -------------- |
| `PYTHONDONTWRITEBYTECODE=1` | Disables `.pyc` file creation                | `python -B`    |
| `PYTHONUNBUFFERED=1`        | Disables output buffering (real-time output) | `python -u`    |

## docker-compose

So, when the container spins up, Uvicorn will run with the following settings:

1. `--reload` enables auto-reload so the server will restart after changes are made to the code base.
2. `--workers 1` provides a single worker process.
3. `--host 0.0.0.0` defines the address to host the server on.
4. `--port 8000` defines the port to host the server on.

`app.main:app` tells Uvicorn where it can find the FastAPI ASGI application -- i.e., "within the 'app' module, you'll find the ASGI app, `app = FastAPI()`, in the 'main.py' file.

Build the image and spin up the container:

```sh
docker-compose up -d --build
```

## Test

pytest==7.2.0
httpx==0.23.1

Here, we imported Starlette's TestClient, which uses the httpx library to make requests against the FastAPI app.

```
docker-compose up -d --build
docker-compose exec web pytest .
```

Add a test_app pytest fixture to a new file called src/tests/conftest.py:

## Async Handlers

Let's convert the synchronous handler over to an asynchronous one.

**Rather than having to go through the trouble of spinning up a task queue (like Celery or RQ) or utilizing threads, FastAPI makes it easy to deliver routes asynchronously. As long as you don't have any blocking I/O calls in the handler, you can simply declare the handler as asynchronous by adding the async keyword like so:**

## Routes

Next, let's set up the basic CRUD routes, following RESTful best practices:

| Endpoint       | HTTP Method | CRUD Method | Description         |
|----------------|-------------|-------------|---------------------|
| `/notes/`      | GET         | READ        | Get all notes       |
| `/notes/:id/`  | GET         | READ        | Get a single note   |
| `/notes/`      | POST        | CREATE      | Add a note          |
| `/notes/:id/`  | PUT         | UPDATE      | Update a note       |
| `/notes/:id/`  | DELETE      | DELETE      | Delete a note       |

For each route, we'll:

1. write a test
2. run the test, to ensure it fails (red)
3. write just enough code to get the test to pass (green)
4. refactor (if necessary)

You can break up and modularize larger projects as well as apply versioning to your API with the APIRouter.it is equivalent to a Blueprint.

## Postgres Setup

To persist the data beyond the life of the container we configured a volume. This config will bind postgres_data to the "/var/lib/postgresql/data/" directory in the container.

## DB

Here, using the database URI and credentials that we just configured in the Docker Compose file, we created a SQLAlchemy engine (used for communicating with the database) along with a Metadata instance (used for creating the database schema). We also created a new Database instance from Databases.

Databases is an async SQL query builder that works on top of the SQLAlchemy Core expression language. It supports the following methods:

1. database.fetch_all(query)
2. database.fetch_one(query)
3. database.iterate(query)
4. database.execute(query)
5. database.execute_many(query)

We're installing Psycopg since we will be using create_all, which is a synchronous SQLAlchemy function.

## Pydantic Model

Create a NoteSchema Pydantic model with two required fields, title and description, in a new file called models.py in "src/app/api":

```
from pydantic import BaseModel


class NoteSchema(BaseModel):
    title: str
    description: str

```

NoteSchema will be used for validating the payloads for creating and updating notes.

## POST Route

we defined a handler that expects a payload, payload: NoteSchema, with a title and a description

when the route is hit with a POST request, FastAPI will read the body of the request and validate the data:

1. If valid, the data will be available in the payload parameter. FastAPI also generates JSON Schema definitions that are then used to automatically generate the OpenAPI schema and the API documentation.
2. If invalid, an error is immediately returned.

It's worth noting that we used the async declaration here since the database communication will be asynchronous. In other words, there are no blocking I/O operations in the handler.

We added a utility function called post for creating new notes that takes a payload object and then:

    Creates a SQLAlchemy insert object expression query
    Executes the query and returns the generated ID

The NoteDB model inherits from the NoteSchema model, adding an id field.

Take note of the prefix URL along with the "notes" tag, which will be applied to the OpenAPI schema (for grouping operations).

Test it out with curl or HTTPie:

```sh
http --json POST http://localhost:8002/notes/ title=foo description=bar
```

we added the following metadata to the parameter with Path:

    ... - the value is required (Ellipsis)
    gt - the value must be greater than 0

<https://testdriven.io/blog/fastapi-crud/>

## monkeypatch

e monkeypatch fixture helps you to safely set/delete an attribute, dictionary item or environment variable, or to modify sys.path for importing.
