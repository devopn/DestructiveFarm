FROM python:3.12-slim

WORKDIR /app

COPY server/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY server/ /app/server/

CMD ["bash", "server/start_server.sh"]