# GD

Game Development Event Backend

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install the project.

```bash
pip install -r requirements
```

then you need rabbitmq and celery running in the background:

```bash
sudo systemctl start rabbitmq-server
celery -A GD worker  -l info
```
finally, start the server:
```bash
python manage.py runserver
```


or simply try this:
```bash
docker-compose up
```

