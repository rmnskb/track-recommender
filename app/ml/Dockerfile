FROM python:3.10-slim

WORKDIR /app

COPY recommender.py .

RUN pip install --no-cache-dir python-dotenv sqlalchemy sklearn

COPY entrypoint.sh .

RUN chmod +x entrypoint.sh

ENTRYPOINT ["./entrypoint.sh"]