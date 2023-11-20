FROM python:3.11.5-slim
WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY . /app
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]