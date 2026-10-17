# Python dependencies belong to the image; application source is editable in Compose.
FROM python:3.14-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app/backend
COPY backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ ./
COPY data/ /app/data/

EXPOSE 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
