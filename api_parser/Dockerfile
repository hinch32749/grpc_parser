FROM python:3.7-alpine
ENV PYTHONUNBUFFERED 1
WORKDIR /app/parser
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
COPY . .
