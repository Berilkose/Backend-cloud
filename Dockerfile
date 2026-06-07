FROM python:3.12-slim

WORKDIR /app

# Gerekli Linux bağımlılıklarını kuruyoruz
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Bağımlılıkları kopyalayıp yüklüyoruz
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Tüm proje dosyalarını container içine atıyoruz
COPY . .

EXPOSE 8000

# Gunicorn ile Django projesini 8000 portundan ayağa kaldırıyoruz
CMD ["gunicorn", "backend_local_proj.wsgi:application", "--chdir", "backend_local_proj", "--bind", "0.0.0.0:8000"]