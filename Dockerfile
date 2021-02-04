
FROM python:3.8-alpine AS DJANGO_APP

ENV PATH="/scripts:${PATH}"

COPY ./requirements.txt /requirements.txt
RUN \
 apk add --no-cache postgresql-libs && \
 apk add --no-cache --virtual .build-deps gcc musl-dev postgresql-dev && \
 python3 -m pip install -r requirements.txt --no-cache-dir && \
 apk --purge del .build-deps

RUN mkdir /app
COPY . /app
WORKDIR /app
COPY ./scripts /scripts

RUN chmod +x /scripts/*

RUN mkdir -p /vol/web/media
RUN mkdir -p /vol/web/static



RUN adduser -D ali
USER ali

CMD ["entrypoint.sh"]




