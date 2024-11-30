FROM python:3.9-slim-buster
# Install python packages
RUN apt-get update
RUN apt-get install -y postgresql postgresql-contrib postgresql-server-dev-all python-psycopg2
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
RUN pip install boto3 pymysql psycopg2-binary 
