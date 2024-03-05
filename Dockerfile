FROM python:3.12-slim
WORKDIR /app

ADD . /app

RUN pip3 install -r requirements.txt

CMD python -u main.py

