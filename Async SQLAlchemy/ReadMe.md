```cmd
 docker-compose down -v
 docker-compose up -d --build

```

 docker-compose exec db psql --username=postgres --dbname=foo

 docker-compose exec web alembic init -t async migrations