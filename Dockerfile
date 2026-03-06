FROM python:3.12-slim

WORKDIR /app

# Запобігаємо створенню .pyc файлів та буферизації stdout/stderr
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Запускаємо сервер
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]