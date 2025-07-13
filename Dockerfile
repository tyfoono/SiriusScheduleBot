FROM python:3.13

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .
COPY api.py .

COPY database.db /initial_db/

CMD ["python", "main.py"]
