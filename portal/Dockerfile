
FROM python:3.11-bullseye

WORKDIR /app

# Copiem requirements i instal·lem dependències
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiem el codi de l'aplicació
COPY app.py .
COPY templates ./templates

EXPOSE 5000

CMD ["python", "app.py"]

