FROM mcr.microsoft.com/playwright/python:v1.40.0-jammy

WORKDIR /app

# Install system dependencies if any additional ones are needed
# (The base image already has python, pip, and browsers)

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Create a startup script
RUN echo "#!/bin/bash" > start.sh && \
    echo "if [ \"\$1\" = 'worker' ]; then" >> start.sh && \
    echo "  celery -A app.worker.celery_app worker --loglevel=info" >> start.sh && \
    echo "elif [ \"\$1\" = 'beat' ]; then" >> start.sh && \
    echo "  celery -A app.worker.celery_app beat --loglevel=info" >> start.sh && \
    echo "else" >> start.sh && \
    echo "  alembic upgrade head" >> start.sh && \
    echo "  uvicorn app.main:app --host 0.0.0.0 --port 80" >> start.sh && \
    echo "fi" >> start.sh && \
    chmod +x start.sh

# Default command (can be overridden in Azure)
CMD ["./start.sh", "api"]
