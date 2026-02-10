# swimming_app
This product is geared towards swimmers with iPhones that want to analyze their training history, they will manually download their health data and upload it into the app which will then store and analyze their swimming workouts and provide a nice summary with statistics overtime.

Run the app:
```
uv run flask --app src/main.py run
```

Run docker:
```
docker-compose up --build
```

Query db:
```
sqlite3 ./instance/swimmers.db "SELECT count(*) FROM swimming_workout LIMIT 5;"
```

Clear out table:
```
sqlite3 ./instance/swimmers.db "drop table swimming_workout;"
```
