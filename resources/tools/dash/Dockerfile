ARG PYTHON_VERSION=3.10
FROM python:${PYTHON_VERSION}-buster

WORKDIR /app

COPY ./app/requirements.txt .

RUN pip3 install -r requirements.txt

EXPOSE 80

CMD [ "flask", "run", "--host", "0.0.0.0", "--port", "80"]