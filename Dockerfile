FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Ajouter le répertoire racine au PYTHONPATH
ENV PYTHONPATH=/app

CMD ["python", "nes_container_manager/tests/run_test.py"]
