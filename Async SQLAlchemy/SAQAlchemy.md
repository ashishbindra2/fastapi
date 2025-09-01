# FastAPI with Async SQLAlchemy, SQLModel, and Alembic

## SQLModel

SQLModel, a library for interacting with SQL databases from Python code,

ased on Python type annotations, it's essentially a wrapper on top of pydantic and SQLAlchemy, making it easy to work with both.

we defined three models:

1. `SongBase` is the base model that the others inherit from. It has two properties, name and `artist`, both of which are strings. This is a data-only model since it lacks `table=True`, which means that it's only used as a pydantic model.
2. `Song`, meanwhile, adds an `id` property to the base model. It's a table model, so it's a pydantic and SQLAlchemy model. It represents a database table.
3. `SongCreate` is a data-only, pydantic model that will be used to create new song instances.

Initialized a new SQLAlchemy engine using create_engine from SQLModel.

The major differences between SQLModel's create_engine and SQLAlchemy's version is that the SQLModel version adds type annotations (for editor support) and enables the SQLAlchemy "2.0" style of engines and connections.

we passed in echo=True so we can see the generated SQL queries in the terminal.

This is always nice to enable in development mode for debugging purposes.

```sh
curl -d '{"name":"Midnight Fit", "artist":"Mogwai"}' -H "Content-Type: application/json" -X POST http://localhost:8004/songs

{
  "id": 1,
  "name": "Midnight Fit",
  "artist": "Mogwai"
}
```

## Async SQLModel

add async support to SQLModel.


Update the database URI in docker-compose.yml, adding in +asyncpg:

```
environment:
  - DATABASE_URL=postgresql+asyncpg://postgres:postgres@db:5432/foo
  ```

Notes:

1. We used the SQLAlchemy constructs -- i.e., AsyncEngine and AsyncSession -- since SQLModel does not have wrappers for them as of writing.
2. We disabled expire on commit behavior by passing in expire_on_commit=False.
3. metadata.create_all doesn't execute asynchronously, so we used run_sync to execute it synchronously within the async function.

Alembic into the mix to properly handle database schema changes.