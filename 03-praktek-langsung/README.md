# Bagian Tiga: Praktik Langsung (Hands-On Labs)

Selamat datang di bagian praktik dari panduan belajar Kubernetes ini! Teori adalah fondasi yang penting, tetapi pemahaman sejati dan keterampilan praktis diperoleh dengan mencoba langsung. Di bagian ini, Anda akan menemukan serangkaian lab langkah demi langkah yang dirancang untuk memandu Anda melalui tugas-tugas umum dan fundamental dalam mengelola aplikasi di Kubernetes.

Setiap direktori lab berisi `README.md` dengan instruksi detail, tujuan pembelajaran, prasyarat, file manifest YAML yang relevan, dan langkah-langkah verifikasi serta pembersihan.

**Tujuan Bagian Ini:**

*   Memberikan pengalaman langsung menggunakan `kubectl` dan manifest YAML.
*   Memperkuat pemahaman tentang konsep inti (Pods, Deployments, Services, StatefulSets, ConfigMaps, Secrets, Ingress, dll.).
*   Membangun kepercayaan diri dalam men-deploy, mengelola, dan memecahkan masalah aplikasi dasar di Kubernetes.
*   Menunjukkan alur kerja umum dalam siklus hidup aplikasi Kubernetes.

**Prasyarat Umum:**

Sebelum memulai lab, pastikan Anda telah menyelesaikan **Bagian Nol: Persiapan Lingkungan**:
*   `kubectl` sudah terinstal dan berfungsi.
*   Anda memiliki akses ke cluster Kubernetes yang berjalan (disarankan lingkungan lokal seperti Minikube, Kind, K3s, atau Docker Desktop untuk lab ini).
*   Pemahaman dasar tentang konsep Kubernetes yang relevan (sebaiknya tinjau Bagian Satu: Konsep Fundamental).
*   Docker terinstal (diperlukan untuk beberapa lab yang melibatkan pembangunan image).
*   Helm v3 terinstal (diperlukan untuk Lab 05).

**Daftar Lab:**

1.  **[Lab 01: Deploy, Expose, dan Scale Aplikasi Web Stateless](./01-deploy-stateless-app/README.md)**
    *   Fokus: `Deployment`, `Service` (ClusterIP), Scaling, Rolling Updates, Rollback. Kasus penggunaan paling umum.
2.  **[Lab 02: Deploy Aplikasi Stateful (Database) dengan StatefulSet](./02-deploy-stateful-app/README.md)**
    *   Fokus: `StatefulSet`, `Headless Service`, `volumeClaimTemplates`, identitas stabil, penyimpanan persisten per Pod.
3.  **[Lab 03: Menggunakan ConfigMaps dan Secrets untuk Konfigurasi Aplikasi](./03-konfigurasi-secret/README.md)**
    *   Fokus: Membuat `ConfigMap` & `Secret`, menyuntikkannya sebagai environment variables dan volume files.
4.  **[Lab 04: Mengekspos Aplikasi ke Dunia Luar dengan Ingress](./04-expose-app-ingress/README.md)**
    *   Fokus: Menggunakan `Ingress` dan `Ingress Controller` untuk routing HTTP/S, terminasi TLS.
5.  **[Lab 05: Setup Monitoring Dasar dengan Prometheus & Grafana (via Helm)](./05-setup-monitoring-sederhana/README.md)**
    *   Fokus: Instalasi stack monitoring menggunakan Helm, mengakses UI Prometheus & Grafana, melihat dashboard dasar.

Disarankan untuk mengerjakan lab secara berurutan, karena beberapa konsep dibangun di atas lab sebelumnya. Jangan ragu untuk bereksperimen dan mencoba variasi dari langkah-langkah yang diberikan. Selamat mencoba!
