FROM 3.8.7-alpine3.12

COPY . /app
WORKDIR /app


RUN ["python server.py"]

RUN addgroup -S appgroup && adduser \
    -S appuser \
    -G appgroup \
    --disable-password

USER appuser