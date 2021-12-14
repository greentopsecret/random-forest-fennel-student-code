FROM python:3.9
WORKDIR /app
COPY ../app /app
RUN pip install --trusted-host pypi.python.org -r requirements.txt

ENTRYPOINT ["python", "/app/runner.py", "-vv"]