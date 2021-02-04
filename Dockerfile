
FROM python:3.8-alpine AS DJANGO_APP

# install some package for postgresql
RUN apk update \
    && apk add postgresql-dev gcc python3-dev musl-dev

ENV PATH="/scripts:${PATH}"



RUN mkdir /app
WORKDIR /app

# first install requirement.txt
COPY ./requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# now copy project to app
COPY . /app



COPY ./scripts /scripts

RUN chmod +x /scripts/*

RUN mkdir -p /vol/web/media
RUN mkdir -p /vol/web/static



CMD ["entrypoint.sh"]




