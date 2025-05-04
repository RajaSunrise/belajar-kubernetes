# Volumes: Menyediakan Penyimpanan untuk Kontainer

Kontainer di Kubernetes (dan Docker) secara inheren bersifat **sementara (ephemeral)**. Ketika sebuah kontainer berhenti dan dimulai ulang, semua file yang dibuat di dalam filesystem-nya akan **hilang**. Selain itu, seringkali kita perlu **berbagi file** antara beberapa kontainer yang berjalan dalam satu Pod yang sama.

Untuk mengatasi masalah ini, Kubernetes menggunakan konsep **Volume**.

## Apa itu Volume Kubernetes?

Sebuah Volume Kubernetes adalah **direktori** (yang mungkin berisi data) yang **dapat diakses oleh kontainer-kontainer di dalam sebuah Pod**.

*   **Sumber Data:** Bagaimana direktori itu terbentuk, media penyimpanannya (disk Node, memori, penyimpanan jaringan, dll.), dan isinya ditentukan oleh **tipe Volume** yang digunakan.
*   **Siklus Hidup Terikat Pod (Umumnya):** Volume dibuat ketika Pod dibuat dan memiliki siklus hidup yang sama dengan Pod yang melingkupinya. **Data dalam Volume akan bertahan melewati restart kontainer** di dalam Pod tersebut. Namun, ketika Pod itu sendiri dihapus, data dalam Volume **mungkin akan hilang**, tergantung pada tipe Volume. (Pengecualian utama adalah `persistentVolumeClaim`).
*   **Berbagi Antar Kontainer:** Semua kontainer dalam Pod dapat me-mount Volume yang sama (bahkan di path mount yang berbeda jika diinginkan), memungkinkan mereka berbagi file dan data secara efisien.

## Mendefinisikan dan Menggunakan Volume

Penggunaan Volume melibatkan dua langkah dalam definisi Pod:

1.  **Mendefinisikan Volume di Level Pod:** Di bawah `spec.volumes`, Anda mendeklarasikan Volume yang akan tersedia untuk Pod tersebut. Anda memberikan `name` pada Volume dan menentukan `type` Volume beserta konfigurasinya.
2.  **Me-mount Volume ke Kontainer:** Di bawah `spec.containers[].volumeMounts`, Anda menentukan Volume mana (berdasarkan `name` dari langkah 1) yang ingin Anda pasang (mount) ke dalam filesystem kontainer, dan di `mountPath` mana di dalam kontainer.

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: volume-demo-pod
spec:
  containers:
  - name: container-1
    image: busybox
    command: ["/bin/sh", "-c", "echo 'Data dari Kontainer 1' > /data/c1.txt; sleep 3600"]
    volumeMounts: # Langkah 2: Mount volume 'shared-data' ke '/data'
    - name: shared-data
      mountPath: /data
  - name: container-2
    image: busybox
    command: ["/bin/sh", "-c", "while true; do cat /data/c1.txt; sleep 5; done"]
    volumeMounts: # Langkah 2: Mount volume 'shared-data' ke '/data' juga
    - name: shared-data
      mountPath: /data

  volumes: # Langkah 1: Definisikan volume bernama 'shared-data'
  - name: shared-data
    emptyDir: {} # Tipe volume: emptyDir (direktori sementara)
```
Dalam contoh ini, kedua kontainer berbagi volume `emptyDir` bernama `shared-data` yang di-mount ke `/data`. Kontainer 1 menulis file, dan Kontainer 2 dapat membacanya. Jika salah satu kontainer restart, file `c1.txt` akan tetap ada. Jika Pod dihapus, volume `emptyDir` dan isinya akan hilang.

## Tipe-tipe Volume Umum

Kubernetes mendukung banyak tipe Volume. Berikut beberapa yang paling penting untuk dipahami di awal:

1.  **`emptyDir`:**
    *   **Deskripsi:** Membuat direktori **kosong** saat Pod ditugaskan ke sebuah Node.
    *   **Siklus Hidup:** Terikat erat pada Pod. Ketika Pod dihapus dari Node (karena alasan apa pun), data di `emptyDir` **hilang selamanya**. Bertahan melewati restart kontainer.
    *   **Media Penyimpanan:** Secara default menggunakan media penyimpanan Node (disk). Anda bisa mengatur `emptyDir.medium: Memory` agar menggunakan `tmpfs` (filesystem berbasis RAM), yang lebih cepat tetapi ukurannya terbatas oleh memori Node dan isinya hilang saat Node reboot (selain saat Pod dihapus).
    *   **Kasus Penggunaan:**
        *   Ruang sementara (scratch space) untuk aplikasi.
        *   Titik pemeriksaan (checkpoint) untuk komputasi panjang yang dapat dipulihkan.
        *   Berbagi file antar kontainer dalam satu Pod (seperti contoh di atas).

2.  **`hostPath` (GUNAKAN DENGAN SANGAT HATI-HATI!):**
    *   **Deskripsi:** Me-mount **file atau direktori dari filesystem Node host** langsung ke dalam Pod.
    *   **Peringatan & Risiko:**
        *   **Keamanan:** Memberikan akses ke filesystem host bisa sangat berbahaya. Pod bisa membaca data sensitif atau bahkan menulis/mengubah file sistem host jika tidak dikonfigurasi dengan benar (misalnya, tanpa `readOnly: true`). Kontainer yang ter-compromise dapat membahayakan seluruh Node.
        *   **Portabilitas:** Pod menjadi terikat pada struktur filesystem Node tertentu. Jika Pod dijadwalkan ulang ke Node lain yang tidak memiliki path tersebut, Pod akan gagal.
        *   **Manajemen Sulit:** Anda perlu memastikan path tersebut ada dan memiliki izin yang benar di semua Node tempat Pod mungkin berjalan.
    *   **Kasus Penggunaan (Terbatas & Perlu Kehati-hatian Ekstra):**
        *   Menjalankan agen monitoring/logging (seperti DaemonSet) yang perlu membaca log sistem Node (mis: `/var/log`).
        *   Mengakses Docker socket (`/var/run/docker.sock`) oleh Pod yang perlu berinteraksi dengan Docker daemon di host (misalnya, untuk membangun image di dalam cluster - praktik yang umumnya tidak disarankan).
        *   Konfigurasi tingkat Node oleh komponen sistem.
    *   **Selalu pertimbangkan alternatif** sebelum menggunakan `hostPath`. Jika harus, gunakan `readOnly: true` dan batasi akses seminimal mungkin. Pertimbangkan `securityContext` untuk lebih membatasi.
    ```yaml
    volumes:
    - name: host-logs
      hostPath:
        path: /var/log/syslog # Path di Node host
        type: FileOrCreate # Tipe path (File, Directory, FileOrCreate, DirectoryOrCreate, Socket)
    # ...
    volumeMounts:
    - name: host-logs
      mountPath: /host-syslog
      readOnly: true
    ```

3.  **`configMap`:**
    *   **Deskripsi:** Cara khusus untuk memproyeksikan data dari objek [ConfigMap](./10-konfigurasi-aplikasi/01-configmaps.md) sebagai file ke dalam Pod.
    *   **Kasus Penggunaan:** Menyediakan file konfigurasi untuk aplikasi.
    *   Data bersifat read-only secara default.

4.  **`secret`:**
    *   **Deskripsi:** Cara khusus untuk memproyeksikan data dari objek [Secret](./10-konfigurasi-aplikasi/02-secrets.md) sebagai file ke dalam Pod.
    *   **Kasus Penggunaan:** Menyediakan data sensitif (password, token, kunci TLS) sebagai file.
    *   Menggunakan `tmpfs` secara default, bersifat read-only sangat disarankan.

5.  **`downwardAPI`:**
    *   **Deskripsi:** Mengekspos metadata tentang Pod itu sendiri (seperti nama Pod, namespace, label, anotasi, resource requests/limits, IP Pod) sebagai file di dalam kontainer.
    *   **Kasus Penggunaan:** Memungkinkan aplikasi menyadari lingkungannya di Kubernetes tanpa perlu query ke API Server secara langsung.

6.  **`persistentVolumeClaim` (SANGAT PENTING untuk Data Persisten):**
    *   **Deskripsi:** Cara standar untuk me-mount **penyimpanan persisten** ke dalam Pod. Volume ini **bertahan hidup** melewati siklus hidup Pod.
    *   **Cara Kerja:** Pod merujuk ke `PersistentVolumeClaim` (PVC), yang merupakan permintaan storage. PVC ini kemudian terikat ke `PersistentVolume` (PV), yang merepresentasikan penyimpanan fisik sebenarnya (disk cloud, NFS, dll.).
    *   **Kasus Penggunaan:** Menyimpan data database, file yang diunggah pengguna, state aplikasi yang penting.
    *   Akan dibahas lebih detail di bagian PV dan PVC.
    ```yaml
    volumes:
    - name: my-persistent-storage
      persistentVolumeClaim:
        claimName: my-pvc-name # Nama PVC yang sudah dibuat & Bound
    ```

7.  **Volume Penyedia Cloud Spesifik (Legacy & Kurang Disarankan):**
    *   Seperti `awsElasticBlockStore`, `azureDisk`, `gcePersistentDisk`. Memungkinkan mounting langsung volume cloud.
    *   **Cara modern** untuk menggunakan storage cloud adalah melalui `persistentVolumeClaim` dengan `StorageClass` yang menggunakan driver CSI penyedia cloud tersebut.

8.  **Volume Penyimpanan Jaringan:**
    *   Seperti `nfs`, `iscsi`, `cephfs`, `glusterfs`. Memungkinkan mounting sistem file jaringan.
    *   Seringkali juga lebih baik dikelola melalui `persistentVolumeClaim`.

Memilih tipe Volume yang tepat sangat bergantung pada kebutuhan data aplikasi Anda: apakah data perlu bertahan setelah Pod hilang? Apakah perlu dibagikan antar kontainer? Apakah itu konfigurasi atau data sensitif? Apakah berasal dari host atau penyimpanan eksternal? Volume adalah blok bangunan fundamental untuk mengelola data dalam Pod Kubernetes.
