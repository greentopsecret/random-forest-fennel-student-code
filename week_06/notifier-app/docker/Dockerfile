FROM python:3.9
WORKDIR /app
COPY ../app/requirements.txt /app
#COPY ../app/prepare-db.py /app
#
#ARG EBAY_HOST
#ARG MONGODB_NAME
#ARG MONGODB_HOST
#ARG MONGODB_PORT

RUN pip install --trusted-host pypi.python.org -r requirements.txt
#RUN python ./prepare-db.py -v

#CMD ["python", "./app.py"]