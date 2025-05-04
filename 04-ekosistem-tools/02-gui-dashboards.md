# GUI Dashboards & Terminal UIs (TUI) untuk Kubernetes

Meskipun `kubectl` adalah alat baris perintah yang kuat dan esensial, terkadang antarmuka visual dapat memberikan cara yang lebih intuitif untuk:

*   **Menjelajahi:** Menavigasi hierarki objek Kubernetes (Namespaces, Deployments, Pods, Services, dll.).
*   **Memvisualisasikan:** Melihat status cluster, penggunaan resource, dan hubungan antar objek secara grafis.
*   **Mengelola:** Melakukan tindakan dasar (melihat log, exec ke Pod, scale Deployment, edit YAML) melalui UI.
*   **Memantau:** Menampilkan metrik dan event secara real-time.

Ada beberapa pilihan populer untuk antarmuka grafis (GUI) dan antarmuka berbasis terminal (TUI) untuk Kubernetes:

## 1. Lens (The Kubernetes IDE)

*   **Jenis:** Aplikasi Desktop GUI (Standalone) - Open Source (dengan beberapa fitur berbayar opsional melalui langganan Lens Pro).
*   **Platform:** macOS, Windows, Linux.
*   **Deskripsi:** Lens menyebut dirinya sebagai "IDE Kubernetes". Ini adalah aplikasi desktop yang sangat komprehensif dan populer yang menyediakan antarmuka kaya fitur untuk mengelola satu atau banyak cluster Kubernetes.
*   **Fitur Utama:**
    *   **Manajemen Multi-Cluster:** Mudah beralih antara konteks kubeconfig yang berbeda.
    *   **Visualisasi Hierarki Objek:** Menampilkan objek berdasarkan Namespace, jenis, dan hubungannya.
    *   **Detail Objek Lengkap:** Menampilkan status, metadata, spec, event, dan YAML untuk setiap objek.
    *   **Metrik Real-time:** Mengintegrasikan (jika Metrics Server/Prometheus ada) dan menampilkan grafik penggunaan CPU, Memori, Jaringan secara real-time untuk Nodes dan Pods.
    *   **Aksi Cepat:** Edit YAML, lihat log (dengan streaming & filter), exec ke shell Pod, port-forward, scale Deployments/StatefulSets, hapus objek, semua dari dalam UI.
    *   **Manajemen Helm:** Menampilkan Helm releases, riwayat, dan values.
    *   **Dukungan CRD:** Menampilkan dan memungkinkan interaksi dasar dengan Custom Resources.
    *   **Ekstensibilitas:** Mendukung ekstensi untuk menambah fungsionalitas.
    *   **Lens Pro (Berbayar):** Menambahkan fitur seperti Lens Security (scan vulnerability), Lens Teamwork (berbagi akses cluster), dukungan prioritas.
*   **Kelebihan:** Sangat kaya fitur, antarmuka intuitif, visualisasi resource bagus, manajemen multi-cluster mudah.
*   **Kekurangan:** Bisa memakan resource desktop, beberapa fitur canggih memerlukan langganan Pro.
*   **Situs Web:** [k8slens.dev](https://k8slens.dev/)

## 2. k9s

*   **Jenis:** Aplikasi Terminal UI (TUI) - Open Source.
*   **Platform:** macOS, Windows, Linux (berjalan di dalam terminal Anda).
*   **Deskripsi:** k9s menyediakan antarmuka berbasis terminal yang sangat cepat dan efisien untuk menavigasi dan mengelola cluster Kubernetes Anda. Ini adalah favorit banyak engineer karena kecepatannya dan penggunaan resource yang rendah.
*   **Fitur Utama:**
    *   **Navigasi Cepat:** Beralih antar jenis resource (Pods, Services, Deployments, dll.) dan namespace menggunakan shortcut keyboard.
    *   **Informasi Real-time:** Menampilkan status objek dan penggunaan resource dasar (jika Metrics Server ada) secara real-time.
    *   **Aksi Cepat via Keyboard:** Lihat log (`l`), exec ke shell (`s`), describe (`d`), hapus (`Ctrl+d`), edit (`e`), port-forward (`Shift+f`), scale (`Ctrl+s`), lihat YAML (`y`) - semuanya dengan keystrokes.
    *   **Pemfilteran:** Memfilter objek berdasarkan label atau nama.
    *   **Tampilan Resource:** Menampilkan penggunaan CPU/Memori.
    *   **Dukungan CRD:** Dapat menampilkan Custom Resources.
    *   **Skins & Kustomisasi:** Dapat dikustomisasi tema warnanya.
    *   **XRay:** Menampilkan hubungan antar resource terkait (misalnya, Service -> Endpoints -> Pods).
    *   **Pulses:** Tampilan ringkasan kesehatan cluster.
*   **Kelebihan:** Sangat cepat, ringan, efisien, navigasi keyboard-centric, berjalan di terminal (bagus untuk SSH).
*   **Kekurangan:** Kurva belajar untuk shortcut keyboard, tidak se-visual GUI seperti Lens, visualisasi grafik terbatas.
*   **Situs Web:** [k9scli.io](https://k9scli.io/)

## 3. Kubernetes Dashboard (Web UI Resmi)

*   **Jenis:** Aplikasi Web GUI - Open Source (Proyek Kubernetes).
*   **Platform:** Berjalan sebagai aplikasi (Deployment) *di dalam* cluster Kubernetes Anda. Diakses melalui browser.
*   **Deskripsi:** Dashboard web resmi yang disediakan oleh proyek Kubernetes. Memberikan gambaran umum cluster dan kemampuan manajemen dasar.
*   **Fitur Utama:**
    *   Tampilan ringkasan cluster (Nodes, Namespaces, Workloads).
    *   Melihat detail objek (Deployments, Pods, Services, dll.).
    *   Membuat objek sederhana dari formulir UI atau dengan mengunggah/mengedit YAML.
    *   Melihat log Pod.
    *   Exec ke Pod.
    *   Tampilan penggunaan CPU/Memori dasar (jika Metrics Server ada).
*   **Kelebihan:** Proyek resmi, terintegrasi dengan baik, tidak perlu instalasi di desktop.
*   **Kekurangan:**
    *   **Keamanan Akses:** Mengamankan akses ke Dashboard bisa rumit. Anda perlu mengkonfigurasi metode autentikasi (misalnya, Kubeconfig, Token) dan otorisasi (RBAC) dengan benar. Mengeksposnya secara publik tanpa pengamanan yang tepat sangat berbahaya.
    *   Fiturnya tidak sekaya Lens atau secepat k9s.
    *   Perlu di-deploy dan dikelola di dalam cluster.
*   **Instalasi:** Biasanya diinstal menggunakan manifest YAML dari repositori resmi. Perlu membuat Service Account dan ClusterRoleBinding untuk memberikan akses yang sesuai. Akses biasanya melalui `kubectl proxy` atau Ingress.
*   **Situs Web:** [kubernetes.io/docs/tasks/access-application-cluster/web-ui-dashboard/](https://kubernetes.io/docs/tasks/access-application-cluster/web-ui-dashboard/)

## Pilihan Lain

*   **Octant:** Proyek open source VMware. Dashboard web developer-centric yang berjalan secara lokal, fokus pada visualisasi objek dan hubungan.
*   **Platform Kubernetes Komersial:** Platform seperti OpenShift (Red Hat), Tanzu (VMware), Rancher (SUSE) seringkali menyertakan dashboard UI bawaan mereka sendiri dengan fitur yang lebih terintegrasi.
*   **UI Cloud Provider:** GKE, EKS, AKS menyediakan UI web mereka sendiri di konsol cloud untuk mengelola cluster terkelola mereka.

## Mana yang Harus Dipilih?

*   **Untuk Pengalaman Desktop Kaya Fitur:** **Lens** adalah pilihan yang sangat solid dan populer, terutama jika Anda mengelola banyak cluster atau menginginkan visualisasi metrik terintegrasi.
*   **Untuk Efisiensi Terminal & Kecepatan:** **k9s** sangat direkomendasikan bagi pengguna yang nyaman dengan terminal dan menginginkan navigasi keyboard yang cepat serta overhead rendah.
*   **Untuk UI Bawaan Cluster:** **Kubernetes Dashboard** bisa berguna, tetapi pastikan Anda memahami dan mengkonfigurasi keamanannya dengan benar.

Banyak engineer menggunakan **kombinasi** dari `kubectl` dengan salah satu (atau kedua) Lens dan k9s untuk mendapatkan yang terbaik dari kedua dunia: kekuatan baris perintah dan kenyamanan visual. Mencoba beberapa alat ini adalah cara terbaik untuk menemukan mana yang paling sesuai dengan alur kerja Anda.
