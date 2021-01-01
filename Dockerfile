FROM python:3.8
ENV PYTHONNONBUFFERED 1
WORKDIR /app
COPY requierments.txt /app/requierments.txt
RUN pip install -r requierments.txt
COPY . /app

CMD ["python" , "manage.py" , "runserver" , "0.0.0.0:8000"]