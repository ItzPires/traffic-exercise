FROM python:3.11

WORKDIR /api

COPY api/requirements.txt .

RUN apt-get update && apt-get install -y netcat-openbsd

RUN apt-get install -y libgdal-dev gdal-bin

RUN pip install --no-cache-dir -r requirements.txt

COPY ./api/ .

COPY docker/test/entrypoint.sh .
RUN chmod +x entrypoint.sh

EXPOSE 8000

ENV DEBUG=True

CMD ["./entrypoint.sh"]
