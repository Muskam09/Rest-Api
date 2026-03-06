FROM python:3.12-slim

WORKDIR /app

# Запобігаємо створенню .pyc файлів та буферизації stdout/stderr
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Запускаємо сервер
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8001", "main:app"]