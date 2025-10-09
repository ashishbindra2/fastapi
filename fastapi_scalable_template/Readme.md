## Scalabel

Scalabel means it should scale with size

- code base grow over time we dont have to do a ton of refactoring work.

- make sure that tings like config is centralized.
- switching between diferent environment like development, staging, production

- app: contain the scource code of our project
  - api
  - core: Contains Cross cutting concerns, Thing that are used througn out application in different ways
  - basically user route is HTTP layer
  - db
  - models
  - service
- test: test case for projects

This api has single route which is users route
Router is empty no business logic but specify waht to write

pydantic setting can wrok naturaly with envioment verable
just load it will automtically fill  the values

After database we have models

model for validation

services contain actual business logic

It is importatnt to keep you test cases into another folder (separate from your application code)

Why strucure work
-api is thin then it realy work

- one router one server simple

Starting the server:

uv run uvicorn app.main:app --reload

Example requests:

Here’s a set of simple curl examples you can use to interact with your FastAPI app once it’s running (default at <http://localhost:8000>):

1️⃣ Create a User

curl -X POST "<http://localhost:8000/api/v1/users>" \
     -H "Content-Type: application/json" \
     -d '{"name": "Ada Lovelace"}'

2️⃣ Get All Users

curl -X GET "<http://localhost:8000/api/v1/users>"

3️⃣ Get a User by ID

(Replace 1 with the actual ID from the create response)

curl -X GET "<http://localhost:8000/api/v1/users/1>"

4️⃣ Update a User

curl -X PUT "<http://localhost:8000/api/v1/users/1>" \
     -H "Content-Type: application/json" \
     -d '{"name": "Grace Hopper"}'

⸻

5️⃣ Delete a User

curl -X DELETE "<http://localhost:8000/api/v1/users/1>"
