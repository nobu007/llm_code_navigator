FROM python:3.10

WORKDIR /app/backend

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "-m", "app:app"]
