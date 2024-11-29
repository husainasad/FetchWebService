FROM python:3.11-slim
WORKDIR /FetchApp
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY FetchApp/. .
EXPOSE 8000
CMD ["fastapi", "run", "receipt_service.py", "--port", "8000"]