FROM python:3.8-slim


ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1
ENV AWS_DEFAULT_REGION=us-east-2

# NOTE: READ ME PLEASE!!!
# All paths are relative to project root. NOT Current Dir.
# In order to copy tests files we must do this
# As a con, we must specify all paths relative to project root

# Steo 0: Set context
WORKDIR /covibot

# Install environment dependencies
RUN pip install chalice boto3

# Install app dependencies including test ones
COPY covibot/requirements.txt covibot/covibot/requirements.txt
COPY covibot/requirements_dev.txt covibot/covibot/requirements_dev.txt

RUN pip install -r covibot/covibot/requirements_dev.txt

COPY tests /covibot/tests

# COPY Chalice config file
COPY covibot/.chalice/config.json /covibot/covibot/.chalice/config.json

RUN ls covibot
RUN ls covibot/covibot
# COPY application sources

COPY covibot/app.py /covibot/covibot/app.py
COPY covibot/chalicelib/ /covibot/covibot/chalicelib

# Start local chalice server
CMD ["chalice", "local", "--host=0.0.0.0", "--port=5000"]
