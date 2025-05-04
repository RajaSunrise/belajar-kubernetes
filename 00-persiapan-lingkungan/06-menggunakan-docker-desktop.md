# Langkah 3 (Opsi D): Menggunakan Kubernetes di Docker Desktop

Jika Anda sudah menggunakan Docker Desktop di Windows atau macOS, mengaktifkan cluster Kubernetes bawaannya adalah cara yang **paling mudah dan cepat** untuk mendapatkan lingkungan Kubernetes lokal node tunggal.

**Bagaimana Ini Bekerja?**

Docker Desktop mengelola sebuah Virtual Machine (di balik layar) untuk menjalankan daemon Docker. Ketika Anda mengaktifkan fitur Kubernetes, Docker Desktop akan mengunduh image dan komponen Kubernetes yang diperlukan dan menjalankannya di dalam VM yang sama (atau VM terpisah, tergantung versi). Ini menyediakan cluster Kubernetes node tunggal yang siap pakai.

## Prasyarat

1.  **Docker Desktop Terinstal:** Pastikan Anda memiliki versi Docker Desktop yang relatif baru terinstal di Windows atau macOS Anda. Periksa [persyaratan sistem Docker Desktop](https://docs.docker.com/desktop/install/windows-install/ / https://docs.docker.com/desktop/install/mac-install/).
2.  **Sumber Daya Sistem:** Docker Desktop (dan cluster K8s di dalamnya) dapat memakan cukup banyak RAM dan CPU. Pastikan mesin Anda memiliki sumber daya yang memadai (disarankan minimal 8GB RAM, lebih banyak lebih baik). Anda bisa mengatur alokasi resource di pengaturan Docker Desktop.
3.  **Lisensi Docker Desktop:** Ingatlah bahwa Docker Desktop mungkin tidak gratis untuk penggunaan komersial di perusahaan besar. Periksa [ketentuan lisensi Docker](https://www.docker.com/pricing/) terbaru.

## Langkah 1: Aktifkan Kubernetes di Pengaturan

Prosesnya sangat sederhana:

1.  Buka **Docker Desktop**.
2.  Klik ikon **Settings** (roda gigi).
3.  Navigasi ke bagian **Kubernetes**.
4.  Centang kotak **"Enable Kubernetes"**.
5.  (Opsional) Anda mungkin melihat opsi lain seperti "Show system containers" atau "Enable Kubernetes metrics".
6.  Klik tombol **"Apply & Restart"**.

Docker Desktop sekarang akan:
*   Mengunduh image Kubernetes yang diperlukan (mungkin perlu beberapa saat tergantung koneksi internet).
*   Memulai komponen Control Plane dan Kubelet sebagai kontainer di dalam lingkungan Docker Desktop.
*   Mengkonfigurasi `kubectl` Anda secara otomatis untuk menggunakan konteks baru bernama `docker-desktop`.

Anda dapat melihat statusnya di bagian Kubernetes di Settings atau ikon Docker di system tray/menu bar Anda (seringkali berwarna hijau ketika K8s berjalan).

## Langkah 2: Verifikasi Cluster

Setelah Docker Desktop menunjukkan Kubernetes berjalan (ikon hijau), buka terminal atau PowerShell Anda:

```bash
# Periksa konteks kubectl saat ini (seharusnya docker-desktop)
kubectl config current-context
# Output: docker-desktop

# Verifikasi node (akan ada satu node bernama 'docker-desktop')
kubectl get nodes
# OUTPUT (Contoh):
# NAME             STATUS   ROLES           AGE   VERSION
# docker-desktop   Ready    control-plane   5m    v1.27.2 # Versi akan bervariasi

# Lihat pods sistem
kubectl get pods -n kube-system
```

Jika perintah ini berhasil, cluster Kubernetes Anda di Docker Desktop sudah siap digunakan!

## Mengelola Cluster Docker Desktop

*   **Menghentikan/Memulai Ulang Kubernetes:** Anda dapat menonaktifkan dan mengaktifkan kembali Kubernetes melalui Pengaturan Docker Desktop jika Anda perlu menghemat resource atau me-restart cluster.
*   **Reset Cluster:** Di Pengaturan -> Kubernetes, ada tombol "Reset Kubernetes Cluster". Ini akan menghapus semua beban kerja dan konfigurasi yang telah Anda deploy dan mengembalikan cluster ke keadaan awal (seperti setelah instalasi baru). Berguna jika terjadi masalah serius atau ingin memulai dari awal.
*   **Mengalokasikan Resource:** Di Pengaturan -> Resources -> Advanced, Anda dapat menyesuaikan jumlah CPU dan Memori yang dialokasikan Docker Desktop untuk VM-nya. Menambah resource ini dapat meningkatkan performa cluster K8s, tetapi akan menggunakan lebih banyak resource host Anda.

## Kelebihan dan Kekurangan

*   **Kelebihan:**
    *   Sangat mudah diatur jika sudah menggunakan Docker Desktop.
    *   Integrasi yang baik dengan alur kerja Docker.
    *   Tidak perlu menginstal alat tambahan (selain Docker Desktop itu sendiri).
*   **Kekurangan:**
    *   Hanya node tunggal, tidak cocok untuk menguji skenario multi-node.
    *   Bisa memakan banyak resource sistem.
    *   Kurang fleksibel/dapat dikonfigurasi dibandingkan Minikube, Kind, atau K3s.
    *   Tergantung pada lisensi Docker Desktop.
    *   Kadang-kadang update Docker Desktop dapat menyebabkan masalah sementara pada cluster K8s bawaan.

Docker Desktop adalah titik awal yang sangat baik bagi pemula atau bagi mereka yang hanya memerlukan lingkungan K8s node tunggal sederhana untuk pengembangan dan pengujian dasar.
