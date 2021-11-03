FROM python:3.9
WORKDIR /app
COPY ../app/requirements.txt /app
RUN pip install --trusted-host pypi.python.org -r requirements.txt

# TODO: load dump from postgres-setup.sql

#CMD ["python", "hello.py"]