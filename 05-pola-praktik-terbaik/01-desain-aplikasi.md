# Praktik Terbaik: Desain Aplikasi Cloud-Native di Kubernetes

Menjalankan aplikasi di Kubernetes bukan hanya tentang memindahkannya ke dalam kontainer. Untuk memanfaatkan sepenuhnya kekuatan platform seperti skalabilitas, ketahanan, dan pengelolaan otomatis, aplikasi Anda sebaiknya dirancang dengan prinsip-prinsip **cloud-native** dalam pikiran. Ini seringkali selaras dengan metodologi **[The Twelve-Factor App](https://12factor.net/)**.

Berikut adalah beberapa praktik terbaik desain aplikasi kunci untuk Kubernetes:

**1. Kemas Aplikasi dan Dependensinya dalam Kontainer (I. Codebase)**
   *   Setiap aplikasi (microservice) harus memiliki codebase tunggal yang dilacak dalam sistem kontrol versi (seperti Git).
   *   Semua dependensi (library, runtime) harus dideklarasikan secara eksplisit (misalnya, `requirements.txt` untuk Python, `package.json` untuk Node.js, `pom.xml` untuk Maven) dan dikemas bersama aplikasi di dalam **image kontainer**.
   *   Hindari dependensi pada alat atau library yang ada di sistem host Node. Image harus *self-contained*. Gunakan **multi-stage builds** di Dockerfile Anda untuk menjaga ukuran image tetap kecil dan aman.

**2. Konfigurasi Melalui Lingkungan (III. Config)**
   *   **Pisahkan konfigurasi** (URL database, kredensial API, pengaturan fitur, dll.) dari kode aplikasi dan image kontainer.
   *   Gunakan mekanisme Kubernetes seperti **ConfigMaps** (untuk data non-sensitif) dan **Secrets** (untuk data sensitif) untuk menyuntikkan konfigurasi ke dalam Pod saat runtime.
   *   Suntikkan konfigurasi ini sebagai **environment variables** atau **volume file**. Env vars umum digunakan, tetapi volume file lebih aman untuk secrets dan memungkinkan pembaruan tanpa restart Pod (meskipun aplikasi perlu membaca ulang file).
   *   Hindari menyimpan konfigurasi langsung di kode atau image.

**3. Perlakukan Layanan Pendukung sebagai Sumber Daya Terlampir (IV. Backing Services)**
   *   Perlakukan database, sistem antrian pesan (message queues), layanan caching, sistem SMTP, dll., sebagai **layanan terlampir (attached resources)** yang dikonsumsi melalui URL atau kredensial yang disimpan dalam konfigurasi (ConfigMap/Secret).
   *   Aplikasi Anda tidak boleh terikat erat pada layanan pendukung spesifik. Idealnya, Anda bisa menukar database (misalnya, dari PostgreSQL lokal ke RDS) hanya dengan mengubah konfigurasi, tanpa mengubah kode aplikasi.
   *   Gunakan **Services** Kubernetes untuk menemukan layanan pendukung lain yang berjalan di dalam cluster.

**4. Proses Stateless (VI. Processes)**
   *   Jalankan aplikasi Anda sebagai satu atau lebih **proses stateless** yang tidak berbagi state (share-nothing).
   *   Setiap **state persisten** yang diperlukan harus disimpan di **layanan pendukung stateful** (seperti database atau penyimpanan objek eksternal) atau **volume persisten (PersistentVolumes)** yang terpasang ke Pod (terutama jika menggunakan StatefulSets).
   *   Proses stateless memungkinkan penskalaan horizontal (menambah/mengurangi replika) dengan mudah, karena setiap instance Pod identik dan dapat diganti. Data sesi (jika ada) sebaiknya disimpan di cache terpusat seperti Redis atau Memcached.

**5. Ekspor Layanan melalui Port Binding (VII. Port Binding)**
   *   Aplikasi Anda harus *self-contained* dan mengekspor layanannya (misalnya, HTTP API) melalui port jaringan tertentu.
   *   Deklarasikan port ini menggunakan `EXPOSE` di Dockerfile dan `ports.containerPort` di manifest Kubernetes (Deployment, Pod).
   *   Jangan bergantung pada injeksi web server (seperti Nginx atau Apache) ke dalam kontainer aplikasi Anda secara default (kecuali itu adalah bagian inti dari aplikasi atau sebagai reverse proxy sidecar). Kubernetes akan menangani routing ke port ini melalui **Services**.

**6. Maksimalkan Ketahanan dengan Proses Sekali Pakai (IX. Disposability)**
   *   Proses (kontainer/Pods) harus **sekali pakai (disposable)**, artinya mereka dapat dimulai atau dihentikan dengan cepat.
   *   Ini memfasilitasi penskalaan elastis, deployment cepat, dan pemulihan dari crash.
   *   Aplikasi harus berusaha untuk **meminimalkan waktu startup**. Gunakan teknik seperti lazy loading atau pre-computation jika memungkinkan.
   *   Aplikasi harus **menangani sinyal terminasi (`SIGTERM`)** dengan anggun (graceful shutdown). Ketika Kubernetes perlu menghentikan Pod (misalnya, saat update atau scaling down), ia mengirimkan `SIGTERM` terlebih dahulu. Aplikasi Anda harus menangkap sinyal ini dan menyelesaikan pekerjaan yang sedang berlangsung (misalnya, menyelesaikan request yang sedang diproses, menutup koneksi database) sebelum keluar dalam batas waktu `terminationGracePeriodSeconds`. Jika tidak keluar tepat waktu, Kubernetes akan mengirim `SIGKILL`, yang dapat menyebabkan data hilang atau state tidak konsisten.

**7. Pertahankan Kesetaraan Dev/Prod (X. Dev/prod parity)**
   *   Usahakan agar lingkungan development, staging, dan production semirip mungkin.
   *   Menggunakan kontainer (Docker) dan orkestrasi (Kubernetes lokal seperti Kind/Minikube) selama pengembangan membantu mencapai ini.
   *   Gunakan sistem CI/CD untuk memastikan proses build dan deploy konsisten di semua lingkungan.

**8. Perlakukan Log sebagai Aliran Peristiwa (XI. Logs)**
   *   **Jangan** buat aplikasi Anda khawatir tentang penyimpanan atau routing file log.
   *   Konfigurasikan aplikasi untuk menulis aliran event log yang tidak ter-buffer ke **standard output (`stdout`)** dan **standard error (`stderr`)**.
   *   Biarkan lingkungan eksekusi (Container Runtime) dan infrastruktur logging Kubernetes (seperti Fluentd/Fluent Bit DaemonSet yang mengirim ke Elasticsearch/Loki) menangani pengumpulan, agregasi, dan penyimpanan log. (Lihat Arsitektur Logging).

**9. Jalankan Tugas Admin/Manajemen sebagai Proses Sekali Jalan (XII. Admin processes)**
   *   Tugas administratif atau pemeliharaan (seperti migrasi database, cleanup skrip) harus dijalankan sebagai proses sekali jalan (one-off processes), terpisah dari proses aplikasi utama yang berjalan lama.
   *   Gunakan **Kubernetes Jobs** atau **CronJobs** untuk menjalankan tugas-tugas ini. Jalankan mereka di lingkungan yang identik dengan aplikasi utama (menggunakan image yang sama atau serupa).

**Tambahan Praktik Terbaik Spesifik Kubernetes:**

*   **Implementasikan Health Checks (Probes):** Ini **KRUSIAL** untuk Kubernetes agar tahu cara mengelola aplikasi Anda.
    *   **`livenessProbe`:** Memberitahu Kubelet apakah kontainer Anda masih hidup/berfungsi. Jika probe gagal beberapa kali, Kubelet akan **me-restart kontainer**. Gunakan ini untuk mendeteksi deadlock atau state internal yang tidak dapat dipulihkan. *Hati-hati:* Jangan membuat liveness probe terlalu sensitif atau bergantung pada layanan eksternal, karena bisa menyebabkan restart loop yang tidak perlu.
    *   **`readinessProbe`:** Memberitahu Endpoint Controller (dan Kubelet) apakah kontainer Anda siap untuk **menerima lalu lintas jaringan**. Jika probe gagal, IP Pod akan **dihapus sementara** dari endpoint Service (dan tidak akan menerima traffic baru). Gunakan ini untuk memeriksa dependensi (misalnya, koneksi database siap) atau jika aplikasi perlu pemanasan (warm-up).
    *   **`startupProbe` (K8s 1.18+):** Berguna untuk aplikasi yang membutuhkan waktu startup lama. Ini menonaktifkan liveness dan readiness probe sampai startup probe berhasil, mencegah Kubelet membunuh aplikasi terlalu dini.
    *   Pilih mekanisme probe yang tepat (HTTP GET, TCP Socket, Exec command) dan konfigurasikan `initialDelaySeconds`, `periodSeconds`, `timeoutSeconds`, `failureThreshold`, `successThreshold` dengan benar.

*   **Tentukan Resource Requests dan Limits:** Selalu tentukan `resources.requests` (CPU, Memori) dan `resources.limits` untuk setiap kontainer. Ini membantu penjadwalan, menentukan QoS, dan mencegah satu kontainer menghabiskan semua resource Node. (Lihat Manajemen Resource).

Dengan merancang aplikasi Anda mengikuti prinsip-prinsip ini, Anda akan membangun sistem yang lebih tangguh, scalable, dan lebih mudah dikelola di platform dinamis seperti Kubernetes.
