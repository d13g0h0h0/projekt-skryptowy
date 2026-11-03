# projekt-skryptowy

All commands are run from the `backend/` directory (where `manage.py` is).

## Create migrations

```
python manage.py makemigrations
```

## Apply migrations

```
python manage.py migrate
```

## Run the development server

```
python manage.py runserver
```

The API is available at `http://127.0.0.1:8000/api/tasks/`.

## Run tests

```
python manage.py test
```

Run tests for the `tasks` app only:

```
python manage.py test tasks
```

Run a single test class or test:

```
python manage.py test tasks.tests.CreateTaskTests
python manage.py test tasks.tests.CreateTaskTests.test_create_task_with_subtasks
```