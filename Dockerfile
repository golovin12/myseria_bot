FROM python:3.11

WORKDIR /myseria_bot

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV REDIS_HOST='redis'

COPY . .

RUN pip install --upgrade pip
RUN pip install -r requirements.txt
