FROM python:3.10.15-alpine3.19

LABEL maintainer="capiedrav"

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

EXPOSE 8000

# install postgres
RUN pip install --upgrade pip && \ 
    # install postgres client
    apk add --update --no-cache postgresql-client && \
    # install psycopg2 build dependencies
    apk add --update --no-cache --virtual .tmp-build-deps \
    build-base postgresql-dev musl-dev && \
    # install psycopg2
    pip install psycopg2 && \
    # remove pyscopg2 build dependencies
    apk del .tmp-build-deps 

# install pillow 
RUN apk add --update --no-cache jpeg-dev && \       
    # install pillow build dependencies
    apk add --update --no-cache --virtual .tmp-build-deps \
    zlib zlib-dev && \
    # install pillow
    pip install pillow && \
    # remove pillow build dependencies
    apk del .tmp-build-deps            

# install requirements
WORKDIR /recipe-app-api
COPY ./requirements.txt .
RUN pip install --no-cache -r requirements.txt

# create non-root user   
RUN adduser --disabled-password --no-create-home django-user

# copy source code
COPY . .

# create folders for static and media files
RUN mkdir -p static_files media_files

# change ownership of the files
RUN chown -R django-user .

# switch to django-user
USER django-user
