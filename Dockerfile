FROM python:3.11

WORKDIR /api

COPY api/requirements.txt .

RUN apt-get update && apt-get install -y netcat-openbsd

RUN pip install --no-cache-dir -r requirements.txt

COPY ./api/ .

EXPOSE 8000

ENV DEBUG=True

CMD ["./entrypoint.sh"]
