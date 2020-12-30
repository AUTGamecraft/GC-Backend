FROM python:3.8
ENV PYTHONNONBUFFERED 1
WORKDIR /app
COPY requirements.txt /app/requirements.txt
# COPY migrate.sh /app/migrate.sh
RUN pip install -r requirements.txt
COPY . /app
# RUN ./migrate.sh

ENTRYPOINT [ "python" , "manage.py" , "runserver" ]

CMD ["0.0.0.0:8000"]