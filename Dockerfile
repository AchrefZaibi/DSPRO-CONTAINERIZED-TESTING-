FROM python:3.11-slim

WORKDIR /app

COPY .. /app/

RUN pip install .

CMD ["python", "nes_container_manager/tests/run_test.py"]
