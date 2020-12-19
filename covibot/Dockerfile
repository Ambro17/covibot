FROM python:3.8-slim

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1
ENV AWS_DEFAULT_REGION=us-east-2

# Steo 0: Set app context
WORKDIR /app

# Install environment dependencies
RUN pip install chalice boto3

# Install app dependencies
COPY requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt

# COPY Chalice config file
COPY .chalice/config.json /app/.chalice/config.json

# COPY application sources
COPY app.py /app/app.py
COPY chalicelib/ /app/chalicelib

# Start local chalice server
CMD ["chalice", "local", "--host=0.0.0.0", "--port=5000"]
