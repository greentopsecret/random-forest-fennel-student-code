FROM python:3.6-slim
WORKDIR /etl_job

COPY requirements.txt /etl_job
RUN pip install --trusted-host pypi.python.org -r requirements.txt

CMD ["python", "example_etl.py"]
