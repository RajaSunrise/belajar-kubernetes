# app/main.py
from flask import Flask
import os
import socket

app = Flask(__name__)

@app.route('/')
def hello():
    # Mencoba membaca versi dari environment variable, default ke v1.0
    app_version = os.environ.get('APP_VERSION', 'v1.0')

    html = f"""
    <!DOCTYPE html>
    <html>
    <head> <title>Hello K8s!</title> </head>
    <body>
        <h1>Hello Kubernetes!</h1>
        <p>Served by Pod: <span style='color:blue;'>{socket.gethostname()}</span></p>
        <p>Version: <span style='color:green;'>{app_version}</span></p>
    </body>
    </html>
    """
    return html

if __name__ == "__main__":
    # Port 5000 diekspos oleh Flask secara default
    # Jalankan di 0.0.0.0 agar bisa diakses dari luar kontainer
    app.run(host='0.0.0.0', port=5000)
