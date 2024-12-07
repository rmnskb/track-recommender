# builder stage
FROM python:3.10-slim AS builder

RUN apt-get update && \
    apt-get install -y libpq-dev gcc # get gcc to compile psycopg2

# create and activate venv
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .
RUN pip install -r requirements.txt

# operational stage
FROM python:3.10-slim

RUN apt-get update && \
    apt-get install -y libpq-dev && \
    rm -rf /var/lib/apt/lists/* # remove packages that are not needed in runtime

# copy from builder stage
COPY --from=builder /opt/venv /opt/venv

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH"

WORKDIR /app

COPY app/ /app
RUN chmod +x /app/ml/entrypoint.sh
RUN /app/ml/entrypoint.sh

#RUN chmod +x /app/db/etl.py
#RUN python /app/db/etl.py

EXPOSE 5000

CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]
