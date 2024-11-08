FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire Django project into the container
COPY . /app/

# Expose the default Django port
EXPOSE 8000

# Command to run Django server (consider using Gunicorn for production)
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
