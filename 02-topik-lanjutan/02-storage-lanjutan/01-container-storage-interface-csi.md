# CSI (Container Storage Interface)

Seiring berkembangnya Kubernetes, kebutuhan untuk mendukung berbagai macam sistem penyimpanan (storage systems) dari vendor yang berbeda menjadi semakin penting. Awalnya, logika untuk berinteraksi dengan sistem penyimpanan ini (misalnya, cara membuat volume EBS di AWS, cara me-mount NFS share) **tertanam langsung di dalam kode inti Kubernetes** (khususnya Kubelet dan PersistentVolume Controller). Ini dikenal sebagai sistem volume "in-tree".

**Masalah dengan Volume In-Tree:**

*   **Sulit Dikembangkan & Dipelihara:** Menambahkan dukungan untuk sistem penyimpanan baru memerlukan perubahan pada kode inti Kubernetes, yang proses rilisnya lambat dan rumit. Vendor storage kesulitan untuk menambahkan fitur baru dengan cepat.
*   **Kode Bloat:** Kode Kubernetes menjadi semakin besar dengan logika spesifik vendor.
*   **Keamanan & Stabilitas:** Bug dalam driver volume in-tree dapat mempengaruhi stabilitas Kubelet atau komponen inti lainnya.
*   **Keterbatasan:** Sulit untuk mendukung fitur penyimpanan lanjutan yang mungkin hanya tersedia di sistem penyimpanan tertentu.

## Solusi: Container Storage Interface (CSI)

**CSI (Container Storage Interface)** adalah **standar industri** yang bertujuan untuk mengekspos sistem penyimpanan block dan file arbitrer ke sistem orkestrasi kontainer (CO - Container Orchestrator) seperti Kubernetes, Mesos, Cloud Foundry, dll., melalui satu set **API standar**.

**Tujuan Utama CSI:**

*   **Memisahkan Logika Storage dari CO:** Memungkinkan vendor storage untuk mengembangkan *driver* mereka secara independen dari siklus rilis Kubernetes (atau CO lainnya).
*   **Plugin Out-of-Tree:** Driver CSI berjalan sebagai aplikasi terpisah (biasanya Pods di Kubernetes), bukan bagian dari kode inti CO.
*   **Konsistensi:** Menyediakan antarmuka yang konsisten bagi CO untuk berinteraksi dengan berbagai sistem penyimpanan.
*   **Ekstensibilitas:** Memudahkan penambahan dukungan untuk sistem penyimpanan baru dan fitur-fitur canggih (seperti snapshot, cloning, perluasan volume, topologi).

## Arsitektur Driver CSI di Kubernetes

Sebuah driver CSI yang di-deploy di Kubernetes biasanya terdiri dari tiga komponen utama (yang seringkali berjalan sebagai Pods):

1.  **External Provisioner (Controller Plugin - Bagian 1):**
    *   Biasanya berjalan sebagai `Deployment` atau `StatefulSet` (1 atau lebih replika).
    *   **Tugas:** Mengawasi objek `PersistentVolumeClaim` (PVC). Ketika PVC baru dibuat yang meminta `StorageClass` yang menunjuk ke driver CSI ini, External Provisioner akan berkomunikasi dengan API sistem penyimpanan backend (melalui CSI Controller Plugin) untuk **membuat (provision)** volume baru. Ia juga menangani **penghapusan (deletion)** volume ketika PVC dihapus (jika `reclaimPolicy: Delete`).
    *   Berkomunikasi dengan API Server K8s dan CSI Controller Plugin.

2.  **External Attacher (Controller Plugin - Bagian 2):**
    *   Biasanya berjalan sebagai `Deployment` atau `StatefulSet`.
    *   **Tugas:** Mengawasi objek `VolumeAttachment` Kubernetes. Ketika sebuah Pod yang menggunakan PVC (yang terikat pada PV CSI) dijadwalkan ke sebuah Node, External Attacher akan memanggil CSI Controller Plugin untuk **melampirkan (attach)** volume fisik (misalnya, memasang disk EBS ke instance EC2) ke Node tersebut. Ia juga menangani **pelepasan (detach)** volume saat Pod tidak lagi membutuhkannya di Node itu.
    *   Berkomunikasi dengan API Server K8s dan CSI Controller Plugin.

3.  **CSI Driver Node Plugin (DaemonSet):**
    *   Berjalan sebagai `DaemonSet`, artinya ada **satu Pod di setiap Worker Node** yang relevan.
    *   **Tugas:** Mendaftar ke Kubelet di Node tersebut. Ketika Kubelet perlu me-mount volume untuk Pod, Kubelet akan memanggil CSI Node Plugin di Node yang sama untuk:
        *   **Memformat (jika perlu) dan Me-mount (mount)** volume (yang sudah di-attach oleh Attacher) ke direktori global di Node (`NodePublishVolume`).
        *   **Me-mount (bind mount)** dari direktori global Node ke direktori spesifik di dalam Pod (`NodeStageVolume`).
        *   Menangani **unmounting** saat Pod dihapus.
    *   Berkomunikasi langsung dengan Kubelet (melalui Unix Domain Socket) dan sistem operasi Node untuk operasi mounting.

**Komponen Tambahan (Opsional tapi Umum):**

*   **External Resizer:** Mengawasi permintaan perluasan ukuran PVC dan memanggil CSI Controller Plugin untuk memperluas volume.
*   **External Snapshotter:** Mengelola pembuatan dan penghapusan snapshot volume melalui API Snapshot CSI.
*   **Liveness Probe:** Sidecar yang memeriksa kesehatan komponen driver CSI.

**Alur Kerja CSI (Sederhana):**

1.  Admin men-deploy Driver CSI (Provisioner, Attacher, Node Plugin DaemonSet).
2.  Admin membuat `StorageClass` yang mereferensikan `provisioner` CSI ini.
3.  User membuat `PVC` meminta `StorageClass` tersebut.
4.  **External Provisioner** melihat PVC, memanggil `CreateVolume` pada CSI Controller Plugin, yang membuat volume di backend storage. Provisioner membuat objek `PV` yang merepresentasikan volume ini. PVC terikat ke PV.
5.  User membuat `Pod` yang menggunakan `PVC`.
6.  Kubernetes Scheduler menempatkan `Pod` di `Node-A`.
7.  **External Attacher** melihat Pod dijadwalkan, memanggil `ControllerPublishVolume` pada CSI Controller Plugin, yang me-attach volume fisik ke `Node-A`. Attacher membuat objek `VolumeAttachment`.
8.  **Kubelet** di `Node-A` melihat Pod perlu volume. Ia memanggil `NodeStageVolume` dan `NodePublishVolume` pada **CSI Driver Node Plugin** yang berjalan di `Node-A`.
9.  Node Plugin me-mount volume ke direktori Pod.
10. Pod dimulai dan dapat menggunakan volume.
11. (Saat Pod dihapus): Proses dibalik (unmount, detach, delete volume - jika reclaim policy Delete).

## Menggunakan Volume CSI

Dari sudut pandang pengguna (pembuat Pod/PVC), penggunaan volume CSI mirip dengan volume in-tree, tetapi melalui `StorageClass`:

1.  Pastikan Driver CSI dan `StorageClass` yang sesuai sudah ada di cluster.
2.  Buat `PersistentVolumeClaim` yang mereferensikan `storageClassName` dari StorageClass CSI tersebut.
3.  Gunakan PVC tersebut dalam definisi `volume` Pod Anda seperti biasa (`persistentVolumeClaim.claimName`).

```yaml
# Contoh StorageClass menggunakan driver CSI (mis: aws-ebs-csi-driver)
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: ebs-gp3-sc
provisioner: ebs.csi.aws.com # Nama provisioner CSI
parameters:
  type: gp3 # Parameter spesifik untuk driver EBS CSI
  fsType: ext4
volumeBindingMode: WaitForFirstConsumer # Praktik baik untuk EBS
reclaimPolicy: Delete
allowVolumeExpansion: true
---
# Contoh PVC menggunakan StorageClass di atas
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: my-app-data-pvc
spec:
  accessModes:
    - ReadWriteOnce
  storageClassName: ebs-gp3-sc # Merujuk ke StorageClass CSI
  resources:
    requests:
      storage: 50Gi
---
# Contoh Pod menggunakan PVC
apiVersion: v1
kind: Pod
# ... metadata ...
spec:
  containers:
    # ... container spec ...
    volumeMounts:
      - mountPath: "/data"
        name: app-storage
  volumes:
    - name: app-storage
      persistentVolumeClaim:
        claimName: my-app-data-pvc # Menggunakan PVC yang akan di-provision oleh CSI
```

## Migrasi dari In-Tree ke CSI

Kubernetes secara aktif memindahkan fungsionalitas volume in-tree ke driver CSI out-of-tree. Fitur **CSI Migration** diaktifkan secara default di versi K8s modern. Ini secara transparan mengarahkan API volume in-tree (misalnya, saat Anda menggunakan `awsElasticBlockStore` atau `gcePersistentDisk` langsung di PV/StorageClass) ke driver CSI yang sesuai di belakang layar, memungkinkan transisi yang mulus tanpa perlu mengubah definisi Volume/PVC/StorageClass yang ada. Namun, praktik terbaik adalah menggunakan provisioner CSI secara eksplisit di StorageClass baru.

CSI adalah masa depan (dan sekarang) dari integrasi penyimpanan di Kubernetes, memberikan fleksibilitas, ekstensibilitas, dan pemeliharaan yang lebih baik dibandingkan mekanisme volume in-tree sebelumnya.
