FROM python:3.9-slim-buster

COPY requirements.txt /tmp
RUN pip install -r /tmp/requirements.txt

RUN mkdir -p /code
COPY . /code/
WORKDIR /code
ENV FLASK_APP=entrypoints/flask_app.py FLASK_DEBUG=1 PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1
RUN chmod +x /code/entrypoint.sh
ENTRYPOINT ["sh","/code/entrypoint.sh"]