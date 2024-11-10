FROM python:3.10.15-alpine3.19

LABEL maintainer="capiedrav"

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

EXPOSE 8000

# install postgress client and psycopg2 (postgres python adaptor)
RUN pip install --upgrade pip && \    
    apk add --update --no-cache postgresql-client && \
    # install psycopg2 build dependencies
    apk add --update --no-cache --virtual .tmp-build-deps \
    build-base postgresql-dev musl-dev && \
    # install psycopg2
    pip install psycopg2 && \
    # remove pyscopg2 build dependencies
    apk del .tmp-build-deps        

# install requirements
WORKDIR /recipe-app-api
COPY ./requirements.txt .
RUN pip install --no-cache -r requirements.txt

# create non-root user   
RUN adduser --disabled-password --no-create-home django-user

# copy source code
COPY . .

# change ownership of the files
RUN chown -R django-user .

# switch to django-user
USER django-user
