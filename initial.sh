#! /usr/bin/env bash

# Let the DB start
python init_db.py

until pg_isready -h $PG_HOST -U $POSTGRES_USER; do
  echo "Waiting for the database to be ready..."
  sleep 1
done

# Run migrations
python manage.py migrate --no-input

# run tests
pytest --disable-warnings -vv -x


# starts application
python manage.py initial_data
python manage.py runserver 0.0.0.0:8000