FROM python:3.8.7-alpine3.12

COPY . /app
WORKDIR /app


CMD python /app/server.py

RUN addgroup -S appgroup && adduser \
    -S appuser \
    -G appgroup

USER appuser
