ARG PYTHON_VERSION=3.15
FROM python:${PYTHON_VERSION}-trixie

WORKDIR /var/app/current

COPY ./app/requirements.txt .

RUN pip3 install -r requirements.txt

EXPOSE 5000

CMD [ "uwsgi", "app.ini" ]