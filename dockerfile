FROM python:3.12-alpine

# Change these values to match your database configuration
ENV DB_TYPE=postgresql
ENV DB_USER=postgres
ENV DB_PASSWORD=postgres
ENV DB_HOST=host.docker.internal
ENV DB_PORT=5432
ENV DB_NAME=cookbook

RUN apk update \
    && apk add --no-cache postgresql-dev gcc python3-dev musl-dev

# Don't forget to place your pg_config binary in the indicated path, I used psql version 14.2
ENV PATH="./bin:${PATH}"

WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]