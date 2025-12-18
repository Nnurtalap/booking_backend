FROM python:3.12.1

WORKDIR /booking

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN chmod +x /booking/docker/*.sh

# CMD убираем — управляем только через docker-compose
CMD ["sh", "-c", "gunicorn app.main:app --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT"]
