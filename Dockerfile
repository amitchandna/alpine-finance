FROM python:3.12.0
WORKDIR home/alpine-finance/
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .

