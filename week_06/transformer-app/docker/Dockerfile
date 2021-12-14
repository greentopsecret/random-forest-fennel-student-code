FROM python:3.9

ARG POSTGRES_USER
ARG POSTGRES_DBNAME

WORKDIR /app
COPY ../app /app

RUN pip install --trusted-host pypi.python.org -r requirements.txt

ENTRYPOINT ["python", "/app/app.py", "-vv"]