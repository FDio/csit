ARG PYTHON_VERSION=3.10
FROM python:${PYTHON_VERSION}-slim-buster

WORKDIR /app

COPY app/ .

RUN pip3 install -r requirements.txt

EXPOSE 80

CMD [ "gunicorn", "--workers=4", "--threads=1", "-b 0.0.0.0:80", "app:server"]