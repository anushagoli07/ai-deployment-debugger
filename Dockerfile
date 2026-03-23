FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Expose port 8080 for the API and 8502 for the Dashboard
EXPOSE 8080
EXPOSE 8502

# We will use a script to run both in the container or just the API
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
