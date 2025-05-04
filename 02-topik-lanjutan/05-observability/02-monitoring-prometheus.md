# Monitoring dengan Prometheus: Standar De-Facto Kubernetes

Meskipun Metrics Server menyediakan metrik resource dasar (CPU/Memori) saat ini, untuk monitoring yang **komprehensif dan proaktif**, kita memerlukan solusi yang lebih kuat yang dapat:

*   Mengumpulkan berbagai jenis metrik (resource, aplikasi kustom, komponen K8s internal).
*   Menyimpan data metrik **historis** untuk analisis tren dan debugging.
*   Menyediakan bahasa kueri yang kuat untuk menganalisis data.
*   Memicu **peringatan (alerts)** berdasarkan kondisi metrik.

**Prometheus** adalah solusi open-source, proyek kelulusan CNCF, yang telah menjadi standar de-facto untuk monitoring dan alerting di ekosistem Kubernetes dan cloud-native.

## Arsitektur dan Konsep Utama Prometheus

Prometheus memiliki arsitektur modular:

1.  **Prometheus Server:** Komponen inti yang melakukan:
    *   **Service Discovery:** Menemukan target (endpoints) yang akan di-scrape metriknya. Di Kubernetes, ini biasanya dilakukan dengan mengawasi API Server untuk menemukan Pods, Services, Endpoints, Nodes, atau Ingresses yang memiliki anotasi atau konfigurasi tertentu.
    *   **Scraping:** Secara berkala (interval yang dapat dikonfigurasi), Prometheus Server menghubungi endpoint `/metrics` pada target yang ditemukan melalui HTTP. Target diharapkan mengekspos metrik dalam **format teks Prometheus** (format key-value sederhana dengan metadata label).
    *   **Storage (TSDB):** Menyimpan data metrik yang di-scrape dalam **Time Series Database (TSDB)** lokal yang efisien. Data disimpan sebagai sampel (timestamp, value) untuk setiap time series unik (kombinasi nama metrik dan label). Prometheus *bukan* dirancang untuk penyimpanan jangka panjang (long-term storage - LTS) secara default (biasanya menyimpan beberapa minggu/bulan), tetapi dapat diintegrasikan dengan solusi LTS eksternal (Thanos, Cortex, M3DB, dll.).
    *   **PromQL (Prometheus Query Language):** Menyediakan bahasa kueri fungsional yang sangat kuat untuk memilih, mengagregasi, dan memanipulasi data time series. Digunakan untuk membuat grafik, dashboard, dan aturan alerting.
    *   **Alerting:** Mengevaluasi **aturan alerting** (ditulis dalam PromQL) secara berkala. Jika suatu aturan terpenuhi (misalnya, latensi tinggi, disk hampir penuh), Prometheus akan mengirimkan alert ke **Alertmanager**.

2.  **Exporters:** Karena tidak semua aplikasi atau sistem mengekspos metrik dalam format Prometheus secara native, ada berbagai **exporters**. Ini adalah aplikasi/agen sidecar atau standalone yang:
    *   Mengumpulkan metrik dari sistem pihak ketiga (misalnya, database MySQL, server Redis, Node Linux, perangkat keras).
    *   Mengkonversi metrik tersebut ke format teks Prometheus.
    *   Mengekspos metrik tersebut pada endpoint HTTP `/metrics` agar dapat di-scrape oleh Prometheus Server.
    *   Contoh populer: `node-exporter` (metrik OS host), `kube-state-metrics` (metrik state objek K8s), `blackbox-exporter` (probe endpoint), berbagai database exporters.

3.  **Pushgateway (Opsional):** Untuk pekerjaan singkat (short-lived jobs) seperti tugas batch yang mungkin selesai sebelum Prometheus sempat men-scrape-nya. Job ini dapat *mendorong (push)* metrik terakhirnya ke Pushgateway, yang kemudian akan di-scrape oleh Prometheus. Digunakan dengan hati-hati.

4.  **Alertmanager:** Komponen terpisah yang menangani alerts yang dikirim oleh Prometheus Server.
    *   **Deduplikasi:** Mengelompokkan alert yang sama.
    *   **Grouping:** Mengelompokkan alert terkait (misalnya, semua alert dari cluster yang sama).
    *   **Silencing:** Membungkam alert sementara berdasarkan kriteria tertentu.
    *   **Inhibition:** Mencegah alert tertentu jika alert lain yang lebih kritis sudah aktif.
    *   **Routing:** Mengirim notifikasi ke berbagai penerima (receiver) seperti Slack, PagerDuty, Email, OpsGenie, Webhooks, dll., berdasarkan label alert.

5.  **Client Libraries:** Pustaka untuk berbagai bahasa pemrograman (Go, Java, Python, Ruby, dll.) yang memudahkan developer untuk **menginstrumentasi** kode aplikasi mereka agar mengekspos metrik kustom dalam format Prometheus.

## Prometheus di Kubernetes

Menjalankan Prometheus untuk memantau Kubernetes sangat umum. Pola deployment tipikal melibatkan:

1.  **Prometheus Server:** Di-deploy sebagai Deployment atau StatefulSet di dalam cluster.
2.  **Konfigurasi Service Discovery:** Prometheus dikonfigurasi untuk menggunakan service discovery Kubernetes (`kubernetes_sd_config`) untuk secara otomatis menemukan target scrape berdasarkan peran (`role: pod`, `role: endpoints`, `role: service`, `role: node`, `role: ingress`). Prometheus akan mencari anotasi spesifik (seperti `prometheus.io/scrape: "true"`, `prometheus.io/port`, `prometheus.io/path`) pada objek-objek ini untuk menentukan mana yang harus di-scrape.
3.  **`node-exporter`:** Di-deploy sebagai `DaemonSet` untuk mengumpulkan metrik OS dari setiap Node.
4.  **`kube-state-metrics` (KSM):** Di-deploy sebagai `Deployment`. KSM *tidak* mengumpulkan metrik resource, melainkan mendengarkan API Server dan mengubah *state* objek Kubernetes (jumlah deployment, pod yang ready, status node, dll.) menjadi metrik yang bisa di-scrape Prometheus. Sangat penting untuk memantau kesehatan cluster.
5.  **Alertmanager:** Di-deploy sebagai Deployment atau StatefulSet (seringkali dengan beberapa replika untuk HA).
6.  **Aplikasi dengan Sidecar Exporter:** Jika aplikasi Anda tidak mengekspos metrik Prometheus, Anda bisa menambahkan sidecar exporter ke Pod aplikasi tersebut.
7.  **Instrumentasi Aplikasi:** Aplikasi diinstrumentasi menggunakan client library untuk mengekspos metrik bisnis atau performa kustom.

## PromQL (Pengantar Singkat)

PromQL adalah jantung dari analisis data di Prometheus. Beberapa konsep dasar:

*   **Tipe Data:** Instant Vector (sekumpulan time series dengan satu sampel per series), Range Vector (sekumpulan time series dengan rentang sampel dari waktu ke waktu), Scalar (angka tunggal), String.
*   **Selector:**
    *   `http_requests_total`: Memilih semua series dengan nama metrik ini.
    *   `http_requests_total{job="api-server", handler="/login"}`: Memilih series dengan label spesifik.
    *   Operator Pencocokan Label: `=`, `!=`, `=~` (regex match), `!~` (regex not match).
*   **Fungsi Agregasi:** `sum()`, `avg()`, `max()`, `min()`, `count()`, `topk()`, `quantile()`.
*   **Fungsi Rate/Increase:** `rate(http_requests_total{job="api"}[5m])` (menghitung rata-rata tingkat permintaan per detik selama 5 menit terakhir), `increase(...)` (menghitung total peningkatan selama rentang waktu).
*   **Operator Biner:** Aritmatika (`+`, `-`, `*`, `/`, `%`, `^`), Perbandingan (`==`, `!=`, `>`, `<`, `>=`, `<=`), Logika (`and`, `or`, `unless`).

**Contoh Kueri:**
*   `sum(rate(container_cpu_usage_seconds_total{namespace="prod"}[5m])) by (pod)`: Menghitung total penggunaan CPU (dalam core) per Pod di namespace `prod` selama 5 menit terakhir.
*   `node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes * 100 < 10`: Mencari Node dengan memori tersedia kurang dari 10%.

## Instalasi (Umumnya via Helm)

Cara paling umum dan mudah untuk men-deploy Prometheus, Alertmanager, Grafana (untuk visualisasi), dan exporter penting (node-exporter, kube-state-metrics) di Kubernetes adalah menggunakan Helm chart **`kube-prometheus-stack`** (sebelumnya dikenal sebagai `prometheus-operator` chart, tetapi sekarang lebih dari itu).

Chart ini menggunakan **Prometheus Operator**, yang menyederhanakan manajemen konfigurasi Prometheus, Alertmanager, dan aturan alerting melalui Custom Resource Definitions (CRDs) seperti `Prometheus`, `Alertmanager`, `ServiceMonitor`, `PodMonitor`, `PrometheusRule`.

```bash
# Tambahkan repo Helm
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

# Instal chart (dengan nilai default atau kustomisasi via values.yaml)
helm install my-prom-stack prometheus-community/kube-prometheus-stack -n monitoring --create-namespace
```

## Kesimpulan

Prometheus menyediakan fondasi yang kuat untuk monitoring dan alerting di Kubernetes. Dengan model scraping, penyimpanan time series, PromQL yang ekspresif, dan Alertmanager, ia memungkinkan Anda mendapatkan wawasan mendalam tentang kesehatan dan performa cluster serta aplikasi Anda. Meskipun memiliki kurva belajar, investasi dalam memahami dan menerapkan Prometheus sangat berharga untuk operasi sistem yang andal.
