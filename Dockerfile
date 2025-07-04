# Use a slim Python base
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the app
COPY . .

# Set environment variables (optional but good practice)
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Expose port (Flask default)
EXPOSE 5000

# Run using gunicorn (adjust Feelog:app if your entry is different)
CMD ["gunicorn", "-b", "0.0.0.0:5000", "Feelog:app"]
