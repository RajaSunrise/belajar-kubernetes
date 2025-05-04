# Bagian Enam: Troubleshooting Cookbook - Panduan Saat Menghadapi Masalah

Tidak peduli seberapa baik Anda merancang atau mengelola cluster Kubernetes Anda, masalah pasti akan muncul. Bagian ini berfungsi sebagai "cookbook" atau kumpulan resep untuk mendiagnosis dan menyelesaikan masalah umum yang sering dihadapi oleh praktisi Kubernetes.

Tujuannya adalah memberikan pendekatan sistematis dan langkah-langkah konkret untuk mengidentifikasi akar penyebab masalah, mulai dari Pod yang tidak berjalan hingga masalah jaringan atau performa yang kompleks.

## Area Troubleshooting yang Dicakup

Setiap file dalam direktori ini fokus pada kategori masalah tertentu:

1.  **[Metodologi Umum](./01-metodologi-umum.md):**
    *   Menjelaskan pendekatan langkah demi langkah yang sistematis untuk troubleshooting di Kubernetes.
    *   Menekankan pentingnya observasi, pengumpulan informasi (`kubectl get`, `events`), mempersempit lingkup, menggunakan `kubectl describe` secara ekstensif, memeriksa log, dan menguji konektivitas (`kubectl exec`, `port-forward`).

2.  **[Masalah Umum Pod](./02-masalah-pod.md):**
    *   Membahas state Pod yang bermasalah seperti `Pending`, `ContainerCreating`, `ImagePullBackOff`, `CrashLoopBackOff`, `OOMKilled`, dan Pod yang stuck di `Terminating`.
    *   Memberikan kemungkinan penyebab dan perintah diagnostik spesifik untuk setiap status.

3.  **[Masalah Jaringan](./03-masalah-jaringan.md):**
    *   Menangani masalah konektivitas Pod-ke-Pod, akses Service (ClusterIP), resolusi DNS (CoreDNS), akses eksternal melalui Ingress, dan debugging Network Policies.
    *   Menyarankan penggunaan alat jaringan standar melalui `kubectl exec`.

4.  **[Masalah Penyimpanan (Storage)](./04-masalah-storage.md):**
    *   Fokus pada masalah terkait PersistentVolumeClaims (PVC) yang `Pending`, error mounting volume (`FailedMount`, `FailedAttachVolume`), dan potensi kehilangan data.
    *   Menjelaskan cara mendiagnosis masalah PV, StorageClass, dan driver CSI.

5.  **[Masalah Control Plane (Utama untuk Self-Hosted)](./05-masalah-control-plane.md):**
    *   Memberikan panduan untuk mendiagnosis masalah pada komponen inti seperti API Server, etcd, Scheduler, dan Controller Manager (lebih relevan untuk cluster yang dikelola sendiri).
    *   Menyebutkan gejala umum dan cara memeriksa log serta status komponen.

6.  **[Masalah Performa](./06-masalah-performa.md):**
    *   Membahas pendekatan untuk mendiagnosis aplikasi yang lambat atau cluster yang tidak responsif.
    *   Meliputi investigasi bottleneck pada level aplikasi, Pod (CPU/Memori throttling, OOMKill), Node (CPU/Memori/Disk/Network), jaringan Kubernetes, dan storage.
    *   Menekankan penggunaan alat profiling dan metrik observability.

## Filosofi Troubleshooting

*   **Sistematis:** Jangan melompat ke kesimpulan. Ikuti langkah-langkah logis.
*   **Observasi:** Kumpulkan data sebanyak mungkin (`get`, `describe`, `logs`, `events`, metrik).
*   **Korelasikan:** Cari hubungan antara gejala, events, log, dan metrik.
*   **Isolasi:** Persempit area masalah.
*   **Uji Hipotesis:** Bentuk dugaan dan coba validasi dengan tes atau data lebih lanjut.
*   **Mulai dari yang Sederhana:** Periksa hal-hal mendasar terlebih dahulu (status, events, konfigurasi dasar) sebelum beralih ke diagnosis yang lebih kompleks.

Gunakan bagian ini sebagai referensi cepat ketika Anda menghadapi masalah. Setiap "resep" memberikan titik awal dan alat yang diperlukan untuk memulai investigasi Anda. Selamat berburu bug!
