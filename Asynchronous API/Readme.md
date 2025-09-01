# Project Setup

You should now have:

    fastapi-crud
        ├── docker-compose.yml
        └── src
            ├── Dockerfile
            ├── app
            │   ├── __init__.py
            │   ├── api
            │   │   ├── __init__.py
            │   │   └── ping.py
            │   └── main.py
            ├── requirements.txt
            └── tests
                ├── __init__.py
                ├── conftest.py
                └── test_ping.py

## Routes

Next, let's set up the basic CRUD routes, following RESTful best practices:

| Endpoint       | HTTP Method | CRUD Method | Description         |
|----------------|-------------|-------------|---------------------|
| `/notes/`      | GET         | READ        | Get all notes       |
| `/notes/:id/`  | GET         | READ        | Get a single note   |
| `/notes/`      | POST        | CREATE      | Add a note          |
| `/notes/:id/`  | PUT         | UPDATE      | Update a note       |
| `/notes/:id/`  | DELETE      | DELETE      | Delete a note       |

Build the image and spin up the container:

```sh
docker-compose up -d --build
```

```
docker-compose up -d --build
docker-compose exec web pytest .
```

    (in_venv) C:\Users\Bindra\Desktop\todo\web development\backend\fastapi\Asynchronous API>docker-compose exec web pytest .
    ======================================================================== test session starts =========================================================================platform linux -- Python 3.11.0, pytest-7.2.0, pluggy-1.6.0
    rootdir: /usr/src/app
    plugins: anyio-4.9.0
    collected 1 item

    test/test_main.py .                                                                                                                                            [100%]

    ========================================================================= 1 passed in 1.58s ==========================================================================

to tun the code

```
docker-compose up -d --build
```

Ensure the notes table was created:

```
docker-compose exec db psql --username=hello_fastapi --dbname=hello_fastapi_dev
```

```
docker-compose exec db psql --username=hello_fastapi --dbname=hello_fastapi_dev

psql (15.1)
Type "help" for help.

hello_fastapi_dev=# \l
                                            List of databases
       Name        |     Owner     | Encoding |  Collate   |   Ctype    |        Access privileges
-------------------+---------------+----------+------------+------------+---------------------------------
 hello_fastapi_dev | hello_fastapi | UTF8     | en_US.utf8 | en_US.utf8 |
 postgres          | hello_fastapi | UTF8     | en_US.utf8 | en_US.utf8 |
 template0         | hello_fastapi | UTF8     | en_US.utf8 | en_US.utf8 | =c/hello_fastapi               +
                   |               |          |            |            | hello_fastapi=CTc/hello_fastapi
 template1         | hello_fastapi | UTF8     | en_US.utf8 | en_US.utf8 | =c/hello_fastapi               +
                   |               |          |            |            | hello_fastapi=CTc/hello_fastapi
(4 rows)

hello_fastapi_dev=# \c hello_fastapi_dev
You are now connected to database "hello_fastapi_dev" as user "hello_fastapi".

hello_fastapi_dev=# \dt
           List of relations
 Schema | Name  | Type  |     Owner
--------+-------+-------+---------------
 public | notes | table | hello_fastapi
(1 row)

hello_fastapi_dev=# \q
```

http --json POST <http://localhost:8002/notes/> title=foo description=bar

## Pydantic Model

Create a NoteSchema Pydantic model with two required fields, title and description

NoteSchema will be used for validating the payloads for creating and updating notes.

docker-compose exec web pytest .