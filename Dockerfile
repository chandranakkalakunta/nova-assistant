# Use slim image ✅ (already doing this)
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies first
# (rarely changes = cached!)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first
# (only rebuilds if requirements change!)
COPY requirements.txt .

# Remove --no-cache-dir for faster builds
# Add --upgrade pip first
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copy application code LAST
# (changes most often = last layer!)
COPY app.py .
COPY nova.py .
COPY tools.py .
COPY observability.py .

# Expose port
EXPOSE 8080

# Run Streamlit
CMD ["streamlit", "run", "app.py", \
     "--server.port=8080", \
     "--server.address=0.0.0.0", \
     "--server.headless=true"]
