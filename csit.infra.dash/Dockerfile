ARG PYTHON_VERSION=3.11
FROM python:${PYTHON_VERSION}-buster

WORKDIR /var/app/current

COPY ./app/requirements.txt .

RUN pip3 install -r requirements.txt

EXPOSE 5000

CMD [ "uwsgi", "app.ini" ]