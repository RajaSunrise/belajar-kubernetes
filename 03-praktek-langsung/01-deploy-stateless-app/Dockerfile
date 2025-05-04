# Dockerfile
# Gunakan image dasar Python yang ringan
FROM python:3.9-slim

# Tetapkan direktori kerja di dalam kontainer
WORKDIR /app

# Salin file requirements dan aplikasi
# Buat file requirements.txt berisi satu baris: Flask==2.3.2 (atau versi terbaru)
COPY requirements.txt requirements.txt
COPY app/ app/

# Instal dependensi
RUN pip install --no-cache-dir -r requirements.txt

# Ekspos port yang digunakan aplikasi
EXPOSE 5000

# Perintah untuk menjalankan aplikasi saat kontainer dimulai
CMD ["python", "app/main.py"]
