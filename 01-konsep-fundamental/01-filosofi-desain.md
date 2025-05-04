# Filosofi Desain Inti Kubernetes

Sebelum menyelam ke dalam objek-objek spesifik seperti Pods dan Services, penting untuk memahami beberapa prinsip dan filosofi dasar yang mendasari desain Kubernetes. Memahami *mengapa* Kubernetes dirancang seperti ini akan membantu Anda menggunakan platform ini dengan lebih efektif.

## 1. Model Deklaratif vs. Imperatif

Ini adalah konsep paling fundamental di Kubernetes.

*   **Imperatif:** Anda memberi tahu sistem *langkah demi langkah bagaimana* mencapai suatu tujuan. Contoh: "Jalankan kontainer A, lalu jalankan kontainer B, lalu ekspos port 80." Perintah `kubectl run`, `kubectl create`, `kubectl expose` (tanpa file YAML) adalah contoh pendekatan imperatif. Cocok untuk tugas cepat atau eksperimen, tetapi sulit untuk direproduksi dan dikelola dalam skala besar.
*   **Deklaratif:** Anda **mendeklarasikan (menyatakan)** *state akhir yang diinginkan* dalam file konfigurasi (biasanya YAML), dan menyerahkan kepada sistem (Kubernetes) untuk mencari cara terbaik mencapai dan mempertahankan state tersebut. Contoh: "Saya ingin ada 3 replika aplikasi web versi 1.2 yang berjalan, dapat diakses melalui Service di port 80." Perintah `kubectl apply -f my-app.yaml` adalah contoh pendekatan deklaratif.

**Kubernetes sangat mengedepankan model deklaratif.** Anda menulis file manifest YAML yang mendeskripsikan objek (Deployment, Service, ConfigMap, dll.) dan state yang Anda inginkan (`spec`), lalu Anda menerapkannya ke cluster.

**Keuntungan Model Deklaratif:**

*   **Idempoten:** Menerapkan konfigurasi yang sama berkali-kali akan menghasilkan state akhir yang sama.
*   **Manajemen Konfigurasi sebagai Kode (Infrastructure as Code - IaC):** File YAML dapat disimpan dalam sistem kontrol versi (seperti Git), memungkinkan pelacakan perubahan, kolaborasi tim, dan rollback yang mudah (GitOps).
*   **Self-Healing & Resilient:** Kubernetes terus menerus memantau state aktual cluster dan membandingkannya dengan state yang diinginkan (dideklarasikan dalam file YAML). Jika ada perbedaan (misalnya, Pod crash), Kubernetes akan secara otomatis mengambil tindakan untuk kembali ke state yang diinginkan.
*   **Abstraksi:** Anda fokus pada *apa* yang Anda inginkan, bukan *bagaimana* Kubernetes mencapainya di balik layar.

## 2. Arsitektur Berbasis API (API-Centric)

Seluruh fungsionalitas Kubernetes diekspos melalui **RESTful API** yang disediakan oleh **`kube-apiserver`**.

*   **Semua adalah Objek API:** Setiap sumber daya di Kubernetes (Pods, Nodes, Services, Deployments, dll.) adalah objek API yang dapat dimanipulasi melalui endpoint API standar (CRUD - Create, Read, Update, Delete).
*   **Sumber Kebenaran Tunggal (`etcd`):** State yang diinginkan dan state aktual dari semua objek disimpan secara persisten di `etcd`, database key-value terdistribusi. API Server adalah satu-satunya komponen yang berkomunikasi langsung dengan `etcd`.
*   **Interaksi Konsisten:** Semua komponen (Kubelet, Scheduler, Controller Manager), pengguna (`kubectl`), dan alat pihak ketiga berinteraksi dengan cluster melalui API Server yang sama. Ini memastikan konsistensi dan memungkinkan ekstensibilitas.

## 3. Loop Kontrol (Reconciliation Loops)

Inti dari cara kerja Kubernetes adalah konsep **loop kontrol** (juga dikenal sebagai *reconciliation loop* atau *control loop*).

*   **Controller:** Proses-proses yang berjalan di `kube-controller-manager` (dan juga di `kubelet`, `kube-proxy`) secara terus menerus:
    1.  **Mengamati (Watch):** Memantau state *diinginkan* (dari `spec` objek yang relevan di API Server).
    2.  **Memeriksa (Check):** Memeriksa state *aktual* sistem (misalnya, jumlah Pod yang benar-benar berjalan).
    3.  **Bertindak (Act):** Jika state aktual berbeda dari state yang diinginkan, controller mengambil tindakan (misalnya, membuat Pod baru, menghapus Pod lama, memperbarui aturan jaringan) untuk **merekonsiliasi** perbedaan tersebut dan menggerakkan sistem *menuju* state yang diinginkan.
*   **Contoh:** ReplicaSet Controller mengamati `spec.replicas` dan `status.readyReplicas`. Jika jumlahnya tidak cocok, ia akan membuat atau menghapus Pods.
*   **Level-Triggered (Idealnya):** Banyak controller dirancang untuk menjadi *level-triggered* (bereaksi terhadap state keseluruhan) daripada *edge-triggered* (bereaksi hanya terhadap perubahan). Ini membuat sistem lebih tangguh terhadap event yang terlewat.

## 4. Immutability (Prinsip Aplikasi Ideal)

Meskipun Kubernetes memungkinkan pembaruan pada beberapa objek, filosofi cloud-native mendorong perlakuan **kontainer sebagai immutable (tidak dapat diubah)**.

*   Alih-alih memperbarui aplikasi di dalam kontainer yang sedang berjalan, Anda membangun **image kontainer baru** dengan versi aplikasi yang baru.
*   Anda kemudian memberi tahu Kubernetes (misalnya, melalui pembaruan Deployment) untuk **mengganti** Pods lama (yang menjalankan image lama) dengan Pods baru (yang menjalankan image baru).
*   **Keuntungan:** Deployment lebih dapat diprediksi, konsisten, dan mudah untuk di-rollback. Mencegah "configuration drift".

## 5. Desain Terdistribusi & Terdesentralisasi

Kubernetes dirancang dari awal untuk berjalan di banyak mesin (Nodes) dan tahan terhadap kegagalan.

*   **Control Plane HA:** Komponen Control Plane dapat direplikasi di beberapa mesin untuk ketersediaan tinggi.
*   **Worker Nodes:** Beban kerja (Pods) didistribusikan di banyak Worker Nodes. Kegagalan satu Worker Node tidak seharusnya menjatuhkan seluruh aplikasi (jika dikonfigurasi dengan replikasi yang benar).
*   **Komunikasi Berbasis API:** Komponen berkomunikasi melalui API Server, mengurangi ketergantungan langsung antar komponen.

Memahami prinsip-prinsip ini akan membantu Anda memahami mengapa Kubernetes terasa berbeda dari sistem manajemen infrastruktur tradisional dan bagaimana memanfaatkannya secara maksimal.
