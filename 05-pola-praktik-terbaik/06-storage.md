# Praktik Terbaik: Penyimpanan (Storage) di Kubernetes

Mengelola penyimpanan data persisten adalah kebutuhan umum untuk banyak aplikasi stateful yang berjalan di Kubernetes. Platform ini menyediakan abstraksi yang kuat (Volumes, PV, PVC, StorageClass), tetapi ada beberapa praktik terbaik yang perlu diikuti untuk memastikan keandalan, performa, dan pengelolaan yang efisien.

**1. Gunakan PersistentVolumes (PV) dan PersistentVolumeClaims (PVC) untuk Data Persisten**
   *   **Hindari `hostPath` untuk data aplikasi:** Volume `hostPath` mengikat Pod ke Node tertentu, membuatnya tidak portabel, menimbulkan risiko keamanan, dan sulit dikelola. Gunakan `hostPath` hanya untuk kasus yang sangat spesifik (misalnya, akses ke log sistem oleh agen DaemonSet) dan dengan sangat hati-hati. Volume `emptyDir` bersifat fana dan hilang saat Pod dihapus.
   *   **Abstraksi PV/PVC:** Manfaatkan PV (sumber daya cluster yang mewakili penyimpanan fisik) dan PVC (permintaan penyimpanan namespaced oleh aplikasi) sebagai cara standar untuk mengelola siklus hidup penyimpanan secara independen dari Pods.

**2. Manfaatkan Dynamic Provisioning dengan StorageClasses**
   *   Membuat PV secara manual (static provisioning) bisa membosankan dan lambat.
   *   Definisikan `StorageClass` untuk setiap *jenis* penyimpanan yang tersedia di cluster Anda (misalnya, SSD cepat, HDD lambat, NFS). StorageClass menunjuk ke *provisioner* (biasanya driver CSI) yang tahu cara membuat volume fisik secara otomatis.
   *   Aplikasi kemudian hanya perlu membuat PVC yang merujuk ke `storageClassName` yang diinginkan, dan Kubernetes akan secara dinamis membuat PV yang sesuai dan mengikatnya ke PVC.
   *   Tetapkan StorageClass *default* di cluster Anda untuk menyederhanakan kasus penggunaan umum.

**3. Pilih `accessModes` yang Tepat untuk PVC Anda**
   *   Pahami mode akses yang didukung oleh backend storage Anda dan pilih yang paling sesuai untuk aplikasi Anda:
        *   **`ReadWriteOnce` (RWO):** Paling umum untuk volume block storage (disk cloud). Volume hanya dapat di-mount sebagai read-write oleh **satu Node tunggal** pada satu waktu. Cocok untuk database tunggal atau komponen stateful yang tidak memerlukan akses bersamaan dari banyak Pods.
        *   **`ReadOnlyMany` (ROX):** Volume dapat di-mount sebagai read-only oleh **banyak Node** secara bersamaan. Berguna untuk berbagi data konfigurasi atau aset statis ke banyak replika aplikasi.
        *   **`ReadWriteMany` (RWX):** Volume dapat di-mount sebagai read-write oleh **banyak Node** secara bersamaan. Memerlukan sistem file jaringan bersama (seperti NFS, CephFS, GlusterFS) sebagai backend. Cocok untuk aplikasi yang memerlukan akses file bersama (misalnya, CMS, beberapa sistem build CI).
        *   **`ReadWriteOncePod` (RWOP):** (Fitur CSI lebih baru) Volume hanya dapat di-mount sebagai read-write oleh **satu Pod tunggal** pada satu waktu, bahkan jika Pod tersebut dipindahkan antar Node. Lebih ketat dari RWO.

**4. Pilih `persistentVolumeReclaimPolicy` dengan Bijak**
   *   Kebijakan ini pada PV menentukan apa yang terjadi pada volume fisik saat PVC yang terikat padanya dihapus.
   *   **`Retain` (Default untuk PV Statis):** Volume fisik **tidak dihapus**. PV masuk ke status `Released`. Data tetap ada. **Paling aman untuk data produksi penting.** Memerlukan intervensi manual oleh admin untuk membersihkan dan menggunakan kembali PV.
   *   **`Delete` (Default untuk PV Dinamis via StorageClass):** Volume fisik (misalnya, disk EBS/GCE) **dihapus** secara otomatis saat PVC dihapus. **Data hilang permanen!** Nyaman untuk development/testing atau data yang dapat dibuat ulang, tetapi berbahaya untuk data produksi jika tidak ada backup.
   *   **`Recycle` (Deprecated):** Jangan digunakan. Tidak aman.
   *   **Rekomendasi:** Gunakan `Retain` untuk data produksi yang tidak tergantikan, meskipun memerlukan pembersihan manual. Gunakan `Delete` dengan hati-hati untuk data sementara atau jika Anda memiliki strategi backup/restore yang solid. Selalu periksa `reclaimPolicy` pada StorageClass Anda!

**5. Pertimbangkan Kebutuhan Performa Storage**
   *   Gunakan StorageClass yang berbeda untuk menawarkan tingkatan performa yang berbeda (misalnya, IOPS tinggi berbasis SSD vs throughput tinggi berbasis HDD).
   *   Aplikasi dapat meminta kelas yang sesuai melalui `storageClassName` di PVC mereka.
   *   Pahami karakteristik performa dari backend storage Anda.

**6. Implementasikan Strategi Backup dan Restore**
   *   Penyimpanan persisten bukan berarti data aman dari kerusakan, penghapusan tidak sengaja, atau bencana.
   *   Manfaatkan fitur **Volume Snapshots** (jika didukung oleh driver CSI Anda) untuk membuat snapshot point-in-time dari PV. Ini adalah cara Kubernetes-native untuk backup.
   *   Integrasikan dengan alat backup level aplikasi (misalnya, `pg_dump` untuk PostgreSQL) atau solusi backup Kubernetes pihak ketiga (seperti Velero) yang dapat mencadangkan tidak hanya data PV tetapi juga state objek Kubernetes lainnya.
   *   Uji prosedur restore Anda secara berkala!

**7. Monitor Penggunaan dan Kesehatan Storage**
   *   Gunakan Prometheus dan `kube-state-metrics` untuk memantau metrik terkait PV dan PVC (status Bound/Pending/Lost, kapasitas total/tersedia).
   *   Gunakan `node-exporter` untuk memantau penggunaan disk dan I/O pada Node host.
   *   Pantau metrik spesifik dari driver CSI atau sistem penyimpanan backend Anda jika memungkinkan.
   *   Siapkan alert untuk kondisi seperti PVC yang tidak bisa terikat (Pending terlalu lama) atau volume yang hampir penuh.

**8. Gunakan `volumeBindingMode: WaitForFirstConsumer` untuk Topologi**
   *   Pada StorageClass Anda, set `volumeBindingMode: WaitForFirstConsumer` (bukan `Immediate` default).
   *   Ini menunda binding dan provisioning PV sampai Pod pertama yang menggunakan PVC tersebut **dijadwalkan** ke Node.
   *   **Manfaat:** Memastikan PV dibuat di zona ketersediaan (availability zone) atau domain topologi yang sama dengan Node tempat Pod akan berjalan. Sangat penting untuk storage yang bersifat zona (seperti disk cloud standar) atau storage lokal Node untuk menghindari masalah Pod tidak bisa start karena volume tidak dapat di-attach.

**9. Bersihkan PVC yang Tidak Digunakan**
   *   PVC yang tidak lagi digunakan (misalnya, aplikasi dihapus tetapi PVC tidak) masih dapat mengkonsumsi kuota atau bahkan sumber daya penyimpanan fisik (jika `reclaimPolicy: Retain`).
   *   Audit dan bersihkan PVC yatim secara berkala.

Mengelola storage di Kubernetes memerlukan pemahaman tentang abstraksi yang disediakan dan praktik terbaik untuk memastikan persistensi, ketersediaan, performa, dan efisiensi biaya data aplikasi stateful Anda.
