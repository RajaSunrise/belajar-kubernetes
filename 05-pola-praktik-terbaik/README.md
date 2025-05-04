# Bagian Lima: Pola dan Praktik Terbaik Kubernetes

Menjalankan aplikasi di Kubernetes lebih dari sekadar mengetahui cara membuat objek YAML. Untuk membangun sistem yang benar-benar tangguh, efisien, aman, dan mudah dikelola, penting untuk mengikuti **pola dan praktik terbaik** yang telah terbukti efektif oleh komunitas Kubernetes yang luas.

Bagian ini menyajikan kumpulan rekomendasi dan panduan di berbagai area kunci, membantu Anda menghindari jebakan umum dan memanfaatkan Kubernetes secara optimal. Menerapkan praktik-praktik ini akan menghasilkan aplikasi dan cluster yang lebih baik dalam jangka panjang.

## Area Praktik Terbaik yang Dicakup

1.  **[Desain Aplikasi Cloud-Native](./01-desain-aplikasi.md):**
    *   Mengadaptasi prinsip Twelve-Factor App untuk Kubernetes.
    *   Pentingnya proses stateless dan disposability.
    *   Implementasi health checks (probes: liveness, readiness, startup) yang efektif.
    *   Penanganan graceful shutdown (SIGTERM).

2.  **[Manajemen Konfigurasi dan Secrets](./02-manajemen-konfigurasi.md):**
    *   Memisahkan konfigurasi dari image.
    *   Kapan menggunakan ConfigMap vs Secret.
    *   Metode injeksi: Environment variables vs Volume file mounts (dan keamanannya).
    *   Mengelola konfigurasi secara deklaratif (GitOps).
    *   Mengamankan secrets di Git (SOPS, External Secrets).
    *   Pentingnya RBAC ketat untuk Secrets.

3.  **[Keamanan](./03-keamanan.md):**
    *   Menerapkan Prinsip Hak Akses Minimum dengan RBAC.
    *   Menggunakan Network Policies untuk segmentasi jaringan.
    *   Mengamankan Pods dan Kontainer dengan Security Contexts (runAsNonRoot, readOnlyRootFilesystem, drop capabilities).
    *   Menegakkan standar dengan Pod Security Admission (PSA).
    *   Mengamankan supply chain kontainer (scan image, sign image).
    *   Menjaga Kubernetes tetap terbarui.
    *   Mengaktifkan Audit Logging.

4.  **[Manajemen Sumber Daya (CPU & Memori)](./04-manajemen-resource.md):**
    *   Pentingnya *selalu* menentukan `requests` dan `limits`.
    *   Memahami kelas Quality of Service (QoS): Guaranteed, Burstable, BestEffort.
    *   Menetapkan nilai request/limit yang masuk akal melalui observasi dan tuning.
    *   Menggunakan LimitRanges untuk default dan batasan.
    *   Menggunakan ResourceQuotas untuk kontrol namespace.

5.  **[Observability (Monitoring, Logging, Tracing)](./05-observability.md):**
    *   Mengadopsi stack monitoring standar (Prometheus, Grafana).
    *   Men-deploy exporter esensial (node-exporter, kube-state-metrics).
    *   Instrumentasi aplikasi untuk metrik kustom.
    *   Menyiapkan alerting yang dapat ditindaklanjuti (Alertmanager).
    *   Menerapkan logging terpusat (log ke stdout/stderr, format terstruktur, agen DaemonSet, backend terpusat).
    *   Mempertimbangkan distributed tracing untuk microservices (OpenTelemetry, Jaeger/Tempo).
    *   Menjaga konsistensi dalam pelabelan dan tagging.

6.  **[Penyimpanan (Storage)](./06-storage.md):**
    *   Menggunakan PV/PVC untuk data persisten, hindari `hostPath`.
    *   Memanfaatkan Dynamic Provisioning (StorageClass).
    *   Memilih `accessModes` yang tepat.
    *   Memilih `persistentVolumeReclaimPolicy` dengan bijak (Retain vs Delete).
    *   Mengimplementasikan strategi backup dan restore (Volume Snapshots, Velero).
    *   Memantau penggunaan storage.
    *   Menggunakan `volumeBindingMode: WaitForFirstConsumer` untuk topologi.

7.  **[Konvensi Penamaan dan Pelabelan](./07-penamaan-labeling.md):**
    *   Menerapkan pola penamaan objek yang deskriptif dan konsisten.
    *   Menggunakan label standar Kubernetes (`app.kubernetes.io/...`).
    *   Menambahkan label kustom yang relevan (environment, team, tier).
    *   Menjaga konsistensi label antar objek terkait.
    *   Memahami perbedaan antara Labels dan Annotations.
    *   Mendokumentasikan konvensi Anda.

Menerapkan praktik terbaik ini mungkin memerlukan upaya awal, tetapi investasi tersebut akan menghasilkan sistem Kubernetes yang lebih stabil, aman, efisien, dan lebih mudah dikelola dalam jangka panjang. Gunakan bagian ini sebagai referensi dan daftar periksa saat merancang dan mengoperasikan aplikasi Anda di Kubernetes.
