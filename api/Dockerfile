FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
    && groupadd --gid 10001 appuser \
    && useradd --create-home --uid 10001 --gid 10001 appuser

COPY app ./app
USER appuser

ENV PYTHONDONTWRITEBYTECODE=1 \
    HOME=/tmp

EXPOSE 8080
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
