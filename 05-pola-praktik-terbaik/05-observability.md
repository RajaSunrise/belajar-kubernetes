# Praktik Terbaik: Observability (Monitoring, Logging, Tracing)

Observability adalah kemampuan untuk memahami state internal suatu sistem hanya dengan memeriksa output eksternalnya (metrik, log, trace). Di lingkungan terdistribusi dan dinamis seperti Kubernetes, observability bukan lagi "nice-to-have", melainkan **kebutuhan mutlak** untuk operasi yang andal, debugging, dan optimalisasi performa.

Tiga pilar utama observability adalah:

1.  **Metrics (Metrik):** Pengukuran numerik dari waktu ke waktu (time series) yang mewakili kesehatan, utilisasi, atau performa sistem/aplikasi (misalnya, penggunaan CPU, latensi request, jumlah error).
2.  **Logs (Log):** Catatan peristiwa diskrit yang terjadi dari waktu ke waktu, memberikan konteks terperinci tentang apa yang terjadi pada titik waktu tertentu.
3.  **Traces (Pelacakan):** Representasi perjalanan sebuah permintaan tunggal saat melintasi berbagai layanan dalam sistem terdistribusi, menunjukkan latensi dan dependensi.

Berikut adalah praktik terbaik untuk menerapkan observability di Kubernetes:

**Metrik & Monitoring:**

1.  **Gunakan Prometheus & Grafana (Standar De-Facto):** Adopsi Prometheus untuk pengumpulan metrik time-series dan alerting, serta Grafana untuk visualisasi dashboard. Manfaatkan `kube-prometheus-stack` Helm chart untuk instalasi awal yang mudah.
2.  **Deploy Exporter Esensial:**
    *   **`node-exporter` (DaemonSet):** Mengumpulkan metrik OS dan perangkat keras dari setiap Node.
    *   **`kube-state-metrics` (Deployment):** Mengkonversi state objek API Kubernetes menjadi metrik (jumlah Pods ready, status Deployment, dll.). Krusial untuk memantau kesehatan cluster.
    *   **Metrics Server:** Diperlukan untuk metrik resource dasar yang digunakan oleh HPA dan `kubectl top`.
3.  **Instrumentasi Aplikasi Anda:** Jangan hanya mengandalkan metrik infrastruktur. Instrumentasi kode aplikasi Anda (menggunakan client library Prometheus/OpenTelemetry) untuk mengekspos metrik bisnis atau performa kunci (misalnya, jumlah request per endpoint, tingkat error, latensi pemrosesan, ukuran antrian). Gunakan [RED Method](https://www.weave.works/blog/the-red-method-key-metrics-for-microservices-architecture/) (Rate, Errors, Duration) atau [USE Method](http://www.brendangregg.com/usemethod.html) (Utilization, Saturation, Errors) sebagai panduan.
4.  **Konfigurasi Service Discovery Prometheus:** Manfaatkan `kubernetes_sd_configs` agar Prometheus secara otomatis menemukan dan men-scrape target (Pods, Services, Endpoints) berdasarkan anotasi (misalnya, `prometheus.io/scrape: "true"`).
5.  **Buat Dashboard yang Bermakna (Grafana):** Jangan hanya menampilkan semua metrik. Buat dashboard yang fokus pada:
    *   **Key Performance Indicators (KPIs):** Metrik terpenting untuk kesehatan layanan/bisnis.
    *   **Korelasi:** Menampilkan metrik terkait bersamaan (misalnya, latensi, traffic, dan error untuk satu layanan).
    *   **Tampilan Berdasarkan Layanan/Tim:** Organisasikan dashboard secara logis.
    *   Manfaatkan dashboard komunitas pra-bangun sebagai titik awal.
6.  **Siapkan Alerting yang Dapat Ditindaklanjuti (Alertmanager):**
    *   Definisikan aturan alert (`PrometheusRule` CRD jika menggunakan Prometheus Operator) di Prometheus untuk kondisi kritis atau abnormal (berdasarkan metrik).
    *   Konfigurasikan Alertmanager untuk deduplikasi, grouping, silencing, dan routing alert ke tim/alat yang tepat (Slack, PagerDuty, dll.).
    *   Fokus pada alert yang **bermakna dan dapat ditindaklanjuti**. Terlalu banyak alert noise akan menyebabkan kelelahan alert (alert fatigue). Alert pada *gejala* (misalnya, latensi pengguna tinggi, tingkat error tinggi) seringkali lebih baik daripada alert pada *penyebab* (misalnya, CPU tinggi).

**Logging:**

1.  **Log ke `stdout`/`stderr`:** Aplikasi harus menulis log ke output standar, bukan file lokal di kontainer.
2.  **Gunakan Format Terstruktur (JSON):** Ini membuat parsing oleh agen logging jauh lebih mudah, andal, dan efisien. Sertakan konteks yang kaya (timestamp, level log, ID request, ID user, dll.) dalam struktur log.
3.  **Deploy Agen Logging sebagai DaemonSet:** Gunakan Fluentd, Fluent Bit (lebih ringan), Promtail (untuk Loki), atau Vector untuk mengumpulkan log dari semua Node secara efisien.
4.  **Enrich Log dengan Metadata Kubernetes:** Konfigurasikan agen untuk secara otomatis menambahkan label Pod, namespace, nama kontainer, dll., ke setiap entri log. Ini sangat penting untuk filtering dan korelasi.
5.  **Pilih Backend Logging Terpusat yang Sesuai:** Elasticsearch (pencarian kuat), Loki (hemat biaya, indeks label), atau layanan cloud. Pertimbangkan volume, retensi, biaya, dan kebutuhan kueri.
6.  **Gunakan Alat Visualisasi Log:** Kibana (untuk Elasticsearch) atau Grafana (untuk Loki dan lainnya) untuk mencari, memfilter, dan menganalisis log.

**Tracing (Terutama untuk Microservices):**

1.  **Adopsi OpenTelemetry (OTel):** Gunakan OTel sebagai standar untuk instrumentasi tracing (dan metrik/log di masa depan). Ini memberikan vendor neutrality.
2.  **Instrumentasi Kode Aplikasi (atau Gunakan Auto-instrumentation):** Tambahkan SDK OTel ke aplikasi Anda untuk membuat Spans, menyebarkan konteks (context propagation) antar layanan (penting!), dan mengirim trace ke backend. Manfaatkan instrumentasi otomatis yang disediakan oleh banyak framework.
3.  **Gunakan Kolektor (OpenTelemetry Collector):** Deploy OTel Collector (DaemonSet/Deployment) untuk menerima trace dari aplikasi, melakukan pemrosesan/sampling, dan mengekspor ke backend tracing pilihan Anda (Jaeger, Tempo, Zipkin, SaaS).
4.  **Integrasikan dengan Service Mesh (Opsional):** Service Mesh (Istio, Linkerd) dapat menyediakan tracing dasar (membuat Spans untuk traffic antar layanan) tanpa instrumentasi kode, meskipun instrumentasi masih diperlukan untuk detail di dalam layanan.
5.  **Pilih Backend Tracing:** Jaeger (populer, fitur lengkap), Tempo (skalabilitas, integrasi Grafana), Zipkin, atau solusi SaaS.
6.  **Korelasikan Traces dengan Logs dan Metrics:** Gunakan Trace ID yang disuntikkan ke log dan tag metrik untuk menghubungkan ketiga pilar observability, memungkinkan Anda melompat dari metrik anomali atau log error langsung ke trace permintaan yang relevan. Grafana sangat bagus dalam hal ini jika menggunakan Tempo/Loki/Prometheus.

**Umum:**

*   **Konsistensi:** Terapkan standar logging, metrik, dan tagging yang konsisten di seluruh layanan Anda.
*   **Otomatisasi:** Otomatiskan deployment dan konfigurasi komponen observability Anda (misalnya, menggunakan Helm atau GitOps).
*   **Mulai dari yang Penting:** Jangan mencoba memantau semuanya sekaligus. Fokus pada metrik dan log kunci terlebih dahulu, lalu perluas cakupan seiring waktu.

Observability yang solid adalah investasi penting yang akan terbayar berkali-kali lipat dalam bentuk peningkatan keandalan sistem, waktu pemulihan yang lebih cepat dari insiden, dan pemahaman yang lebih baik tentang perilaku aplikasi Anda di lingkungan Kubernetes yang kompleks.
