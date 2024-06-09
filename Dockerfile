FROM python:3.10-alpine

WORKDIR /usr/src/app

RUN pip install quart
COPY . .

CMD [ "python3.10", "./main.py" ]