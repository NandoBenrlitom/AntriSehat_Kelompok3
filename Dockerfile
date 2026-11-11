FROM python:3.11-slim AS base
WORKDIR /app
COPY requirements.txt .

FROM base AS deps
RUN pip install --no-cache-dir -r requirements.txt

# Target Jenkins untuk menjalankan Pytest
FROM deps AS test
COPY . .
CMD ["pytest", "-v"]

# Target Production
FROM deps AS production
COPY . .
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]