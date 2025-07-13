FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY backend/src/ ./src/

# Set Python path
ENV PYTHONPATH=/app/src

# Run the application
# Use shell form to expand $PORT environment variable
CMD python -m uvicorn api:app --host 0.0.0.0 --port ${PORT:-8000}