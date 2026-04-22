FROM python:3.11-bullseye

WORKDIR /app

# 1️⃣ Dependències del sistema (IMPORTANT)
RUN apt-get update && apt-get install -y \
    wkhtmltopdf \
    && rm -rf /var/lib/apt/lists/*

# 2️⃣ Dependències Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 3️⃣ Codi de l’aplicació
COPY app.py .
COPY Dedicacions.py .
COPY genDeds.py .

# 4️⃣ Templates
COPY templates ./templates

# 5️⃣ Carpetes de treball
RUN mkdir -p uploads output

EXPOSE 5000

CMD ["python", "app.py"]