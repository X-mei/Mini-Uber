FROM python:3
ENV PYTHONUNBUFFERED 1
RUN mkdir /code
WORKDIR /code
ADD Ride/requirements.txt /code/
RUN pip install -r requirements.txt
ADD . /code/
