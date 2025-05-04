# Bagian Dua: Menyelami Topik Lanjutan Kubernetes

Selamat datang di bagian kedua dari perjalanan belajar Kubernetes Anda! Setelah menguasai [Konsep Fundamental](../01-konsep-fundamental/README.md), bagian ini akan membawa Anda menyelami area-area yang lebih kompleks dan fitur-fitur canggih yang membuat Kubernetes menjadi platform orkestrasi yang begitu kuat dan fleksibel.

Di sini, kita akan menjelajahi seluk-beluk jaringan internal dan eksternal, manajemen penyimpanan tingkat lanjut, berbagai lapisan keamanan, strategi penjadwalan yang canggih, pilar-pilar observability (monitoring, logging, tracing), cara mengelola sumber daya cluster secara efisien, serta teknik untuk mengelola aplikasi kompleks dan bahkan memperluas API Kubernetes itu sendiri.

Menguasai topik-topik ini akan membekali Anda dengan pengetahuan untuk merancang, membangun, dan mengoperasikan sistem yang tangguh, aman, scalable, dan observable di atas Kubernetes.

## Topik yang Dibahas

Berikut adalah area utama yang akan kita jelajahi di bagian ini:

1.  **[Networking Lanjutan](./01-networking-lanjutan/):** Memahami bagaimana komunikasi terjadi di dalam dan di luar cluster.
    *   Model Jaringan Fundamental & CNI (Container Network Interface)
    *   Mengekspos Layanan HTTP/S dengan Ingress Controllers
    *   Mengamankan Traffic Internal dengan Network Policies
    *   Cara Kerja DNS Internal Cluster (CoreDNS)
    *   Pengenalan Konsep Service Mesh (Istio, Linkerd)

2.  **[Storage Lanjutan](./02-storage-lanjutan/):** Mengelola data persisten dengan fitur yang lebih canggih.
    *   Standar CSI (Container Storage Interface)
    *   Backup dan Restore dengan Volume Snapshots
    *   Mengubah Ukuran Volume dengan Volume Expansion
    *   Penjadwalan Sadar Lokasi Penyimpanan (Storage Topology)

3.  **[Security](./03-security/):** Mengamankan cluster dan beban kerja Anda dari berbagai ancaman.
    *   Autentikasi (AuthN): Menjawab "Siapa Anda?" (Users, ServiceAccounts, OIDC)
    *   Otorisasi (AuthZ): Menjawab "Apa yang Boleh Anda Lakukan?" (RBAC)
    *   Detail Service Accounts sebagai Identitas Proses
    *   Mengontrol Privilege dengan Security Contexts
    *   Menegakkan Standar Keamanan Pod dengan Pod Security Admission (PSA)
    *   Praktik Terbaik Manajemen Secrets
    *   Ringkasan Keamanan Jaringan Berlapis

4.  **[Scheduling Lanjutan](./04-scheduling-lanjutan/):** Mengontrol penempatan Pod dengan presisi.
    *   Menarik Pod ke Node Tertentu (Node Selectors & Node Affinity)
    *   Mendorong Pod Menjauh dari Node (Taints & Tolerations)
    *   Menempatkan Pod Relatif Terhadap Pod Lain (Pod Affinity & Anti-Affinity)
    *   Menyebarkan Pod Secara Merata (Topology Spread Constraints)
    *   Prioritas Pod dan Penggusuran (Preemption)

5.  **[Observability](./05-observability/):** Mendapatkan wawasan tentang apa yang terjadi di dalam sistem Anda.
    *   Metrik Resource Dasar dengan Metrics Server (`kubectl top`)
    *   Monitoring Komprehensif dengan Prometheus (Scraping, PromQL, Alertmanager)
    *   Visualisasi Metrik dengan Grafana
    *   Arsitektur Logging Terpusat (EFK, PLG)
    *   Pengenalan Distributed Tracing (Jaeger, Tempo, OpenTelemetry)

6.  **[Manajemen Sumber Daya](./06-manajemen-sumber-daya/):** Mengontrol dan mengoptimalkan utilisasi cluster.
    *   Membatasi Penggunaan per Namespace dengan Resource Quotas
    *   Menetapkan Batas Default/Min/Max dengan Limit Ranges

7.  **[Package Management dengan Helm](./07-package-management-helm/):** Mengelola aplikasi Kubernetes sebagai paket (Charts).
    *   Pengenalan Konsep Helm (Chart, Release, Repository, Values)
    *   Struktur Direktori Helm Chart
    *   Dasar-dasar Templating Helm (Go template, Sprig, Objek Bawaan)
    *   Mengelola Dependensi (Subcharts)
    *   Menjalankan Aksi Kustom dengan Lifecycle Hooks

8.  **[Mengembangkan Kubernetes](./08-mengembangkan-kubernetes/):** Memperluas fungsionalitas inti platform.
    *   Menambah Tipe Objek Baru dengan Custom Resource Definitions (CRD)
    *   Mengotomatiskan Operasi Kompleks dengan Pola Operator

Setiap sub-direktori berisi penjelasan mendalam tentang konsep-konsep terkait, contoh konfigurasi YAML, dan praktik terbaik. Selamat menjelajahi kedalaman Kubernetes!
