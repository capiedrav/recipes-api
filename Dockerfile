FROM python:3.10.15-alpine3.19

LABEL maintainer="capiedrav"

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

EXPOSE 8000

# install dependencies
WORKDIR /recipe-app-api
COPY ./requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache -r requirements.txt

# create non-root user   
RUN adduser --disabled-password --no-create-home django-user

# copy source code
COPY . .

# change ownership of the files
RUN chown -R django-user .

# switch to django-user
USER django-user
