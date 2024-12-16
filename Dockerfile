FROM python:3.10.15-alpine3.19

LABEL maintainer="capiedrav"

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

EXPOSE 8000

# install postgres and pillow dependencies
RUN pip install --upgrade pip && \ 
    # install postgres client
    apk add --update --no-cache postgresql-client \
    # install pillow dependency
    jpeg-dev && \ 
    # install psycopg2 build dependencies
    apk add --update --no-cache --virtual .tmp-build-deps \
    build-base postgresql-dev musl-dev \
    # install more pillow dependencies
    zlib zlib-dev && \
    # install psycopg2 and pillow
    pip install psycopg2 pillow && \
    # remove pyscopg2 and pillow build dependencies
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
