# Troubleshooting Masalah Control Plane (Utama untuk Self-Hosted)

Control Plane adalah "otak" dari cluster Kubernetes Anda, terdiri dari komponen-komponen kritis seperti `kube-apiserver`, `etcd`, `kube-scheduler`, dan `kube-controller-manager`. Masalah pada salah satu komponen ini dapat berdampak signifikan pada fungsionalitas seluruh cluster.

**Penting:** Troubleshooting Control Plane secara mendalam biasanya hanya relevan jika Anda menjalankan **cluster Kubernetes self-hosted** (misalnya, dibangun dengan `kubeadm`, Kubespray, RKE, atau dari awal). Jika Anda menggunakan **layanan Kubernetes terkelola (managed Kubernetes)** seperti GKE, EKS, atau AKS, penyedia cloud **mengelola Control Plane untuk Anda**, dan Anda umumnya tidak memiliki akses langsung atau kebutuhan untuk men-debug komponen-komponennya. Jika Anda mencurigai masalah Control Plane pada cluster terkelola, Anda harus menghubungi dukungan penyedia cloud Anda.

Namun, memahami potensi masalah Control Plane tetap berguna bahkan pada cluster terkelola untuk mengidentifikasi apakah suatu masalah berasal dari aplikasi Anda atau dari platform.

**Komponen Utama & Potensi Masalah (Self-Hosted):**

1.  **`kube-apiserver`:**
    *   **Peran:** Pintu gerbang utama API, validasi, otentikasi, otorisasi, komunikasi dengan etcd.
    *   **Potensi Masalah:** Tidak berjalan/crash, tidak dapat dihubungi (masalah jaringan/firewall), masalah sertifikat TLS, kelebihan beban (terlalu banyak request), masalah koneksi ke etcd.
    *   **Diagnosa:**
        *   Periksa status Pod/proses API Server (`kubectl get pods -n kube-system` jika berjalan sebagai Pod, atau `systemctl status kube-apiserver` jika sebagai service host).
        *   Periksa **log API Server**. Cari pesan error terkait autentikasi, otorisasi, koneksi etcd, atau pemrosesan request.
        *   Periksa penggunaan resource (CPU/Memori) pada node tempat API Server berjalan.
        *   Verifikasi sertifikat TLS yang digunakan oleh API Server dan klien (`kubectl`).
        *   Periksa konektivitas jaringan ke API Server dari node lain dan dari luar cluster (jika perlu).

2.  **`etcd`:**
    *   **Peran:** Database key-value terdistribusi yang menyimpan *semua* state cluster. **Komponen paling kritis.**
    *   **Potensi Masalah:** Cluster etcd kehilangan kuorum (mayoritas node etcd tidak tersedia), performa lambat (disk I/O bottleneck), korupsi data, kehabisan ruang disk, masalah jaringan antar node etcd.
    *   **Diagnosa:**
        *   Periksa status Pods/proses etcd di semua node etcd.
        *   Periksa **log etcd**. Cari pesan error terkait kuorum, leader election, masalah disk, atau request yang lambat.
        *   Gunakan `etcdctl` (alat CLI etcd) untuk memeriksa kesehatan cluster (misalnya, `etcdctl endpoint health`, `etcdctl endpoint status`). Ini mungkin perlu dijalankan dari dalam Pod etcd atau dengan sertifikat yang benar.
        *   Pantau metrik etcd (melalui Prometheus jika diekspos) untuk latensi, throughput, ukuran database.
        *   Pantau penggunaan disk dan performa I/O pada node etcd.
    *   **Penting:** Lakukan backup etcd secara teratur! Kehilangan data etcd berarti kehilangan state cluster.

3.  **`kube-scheduler`:**
    *   **Peran:** Memilih Node yang sesuai untuk menjalankan Pods yang baru dibuat (status `Pending`).
    *   **Potensi Masalah:** Tidak berjalan/crash, tidak dapat terhubung ke API Server, bug dalam algoritma scheduling, masalah performa (lambat menjadwalkan Pods di cluster besar).
    *   **Diagnosa:**
        *   Periksa status Pod/proses Scheduler.
        *   Periksa **log Scheduler**. Cari pesan error terkait koneksi API Server atau evaluasi predikat/prioritas scheduling. Anda bisa meningkatkan level verbosity log untuk detail lebih lanjut.
        *   Jika Pods terus menerus `Pending`, periksa `Events` Pod (`kubectl describe pod ...`) untuk melihat alasan `FailedScheduling` yang dilaporkan oleh Scheduler.

4.  **`kube-controller-manager`:**
    *   **Peran:** Menjalankan berbagai controller (Node, ReplicaSet, Deployment, Namespace, ServiceAccount, Endpoint, dll.) yang mengawasi state cluster dan melakukan rekonsiliasi.
    *   **Potensi Masalah:** Tidak berjalan/crash, tidak dapat terhubung ke API Server, bug dalam logika controller tertentu, kelebihan beban (terlalu banyak objek untuk diawasi).
    *   **Diagnosa:**
        *   Periksa status Pod/proses Controller Manager.
        *   Periksa **log Controller Manager**. Cari pesan error terkait koneksi API Server, rekonsiliasi objek spesifik, atau controller tertentu. Anda bisa mengaktifkan/menonaktifkan controller individual melalui flag jika perlu debugging.
        *   Jika objek tidak berperilaku seperti yang diharapkan (misalnya, Deployment tidak membuat Pods, Endpoint tidak diperbarui), periksa log Controller Manager untuk error yang relevan dengan controller objek tersebut.

5.  **`cloud-controller-manager` (Jika Menggunakan Integrasi Cloud):**
    *   **Peran:** Menjalankan controller yang berinteraksi dengan API cloud provider (misalnya, untuk membuat LoadBalancer, mengelola Node dari sisi cloud).
    *   **Potensi Masalah:** Tidak berjalan/crash, masalah koneksi/autentikasi ke API cloud provider, bug dalam logika controller cloud.
    *   **Diagnosa:**
        *   Periksa status Pod/proses Cloud Controller Manager.
        *   Periksa **log Cloud Controller Manager**. Cari error terkait interaksi API cloud (misalnya, izin API kurang, kuota cloud terlampaui).
        *   Periksa kredensial dan izin yang digunakan oleh Cloud Controller Manager untuk mengakses API cloud provider.

**Gejala Umum Masalah Control Plane:**

*   Perintah `kubectl` lambat atau gagal.
*   Pods baru stuck di `Pending` tanpa alasan yang jelas di events Pod.
*   Objek tidak diperbarui atau dihapus dengan benar (misalnya, Deployment tidak membuat Pod baru, Service tidak mendapatkan Endpoints).
*   Nodes masuk ke state `NotReady` atau `Unknown` secara acak.
*   Cluster tidak stabil atau tidak responsif.

**Alat Diagnostik Tambahan (Self-Hosted):**

*   **Pemeriksaan Kesehatan Komponen:** `kubectl get componentstatuses` atau `kubectl get --raw /livez?verbose`, `/readyz?verbose`. (Status komponen bisa kurang andal tergantung implementasi).
*   **Metrik Control Plane:** Jika diekspos, pantau metrik dari API Server, Scheduler, Controller Manager, etcd menggunakan Prometheus/Grafana.
*   **Log Audit API Server:** Memberikan jejak terperinci dari semua permintaan ke API Server.

Troubleshooting Control Plane pada cluster self-hosted memerlukan pemahaman yang baik tentang arsitektur Kubernetes dan interaksi antar komponennya. Selalu periksa log dan status kesehatan masing-masing komponen secara sistematis. Untuk cluster terkelola, fokus pada gejala yang terlihat oleh aplikasi Anda dan laporkan ke penyedia cloud jika Anda mencurigai masalah platform.
