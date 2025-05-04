# Volume Snapshots: Mencadangkan dan Mengkloning Data Volume

Dalam banyak kasus penggunaan, terutama untuk aplikasi stateful seperti database, kemampuan untuk membuat salinan *point-in-time* dari data volume persisten sangat penting untuk:

*   **Backup:** Membuat cadangan data untuk pemulihan jika terjadi kegagalan, kerusakan data, atau bencana.
*   **Cloning:** Membuat salinan volume untuk tujuan development, testing, atau membuat lingkungan baru dengan data yang sama.
*   **Rollback:** Kembali ke keadaan data sebelumnya.

Kubernetes menyediakan API standar untuk mengelola **Volume Snapshots** melalui mekanisme **CSI (Container Storage Interface)**.

**Penting:** Fitur Volume Snapshot bergantung sepenuhnya pada **dukungan dari driver CSI** yang Anda gunakan. Tidak semua driver CSI mengimplementasikan fungsionalitas snapshot. Jika driver CSI Anda tidak mendukungnya, Anda tidak akan dapat menggunakan API Volume Snapshot Kubernetes untuk volume yang disediakan oleh driver tersebut.

## Objek API Volume Snapshot

Fitur Volume Snapshot memperkenalkan beberapa objek API baru di Kubernetes (biasanya dalam grup API `snapshot.storage.k8s.io`):

1.  **`VolumeSnapshotClass` (Cluster-scoped):**
    *   Mirip dengan `StorageClass`, tetapi untuk snapshot.
    *   Mendefinisikan "kelas" snapshot yang tersedia.
    *   **`driver`**: Menentukan nama driver CSI yang akan menangani pembuatan snapshot untuk kelas ini. Ini harus cocok dengan driver CSI yang menyediakan PV asli.
    *   **`deletionPolicy`**: Menentukan apa yang terjadi pada snapshot fisik di backend storage ketika objek `VolumeSnapshot` dihapus:
        *   `Delete` (Default): Snapshot fisik di backend akan dihapus.
        *   `Retain`: Snapshot fisik di backend tetap ada. Objek `VolumeSnapshotContent` perlu dihapus manual.
    *   `parameters` (Opsional): Parameter spesifik vendor untuk pembuatan snapshot.

2.  **`VolumeSnapshot` (Namespaced):**
    *   Ini adalah **permintaan** untuk membuat snapshot dari `PersistentVolumeClaim` (PVC) yang sudah ada. Objek ini berada di namespace yang sama dengan PVC sumber.
    *   **`volumeSnapshotClassName`**: Menentukan `VolumeSnapshotClass` yang akan digunakan untuk membuat snapshot.
    *   **`source`**: Menentukan sumber data, yaitu:
        *   `persistentVolumeClaimName`: Nama PVC yang datanya ingin Anda snapshot.
    *   Ketika `VolumeSnapshot` dibuat, controller snapshot (bagian dari driver CSI atau komponen eksternal) akan memicu pembuatan snapshot sebenarnya di backend storage.

3.  **`VolumeSnapshotContent` (Cluster-scoped):**
    *   Mirip dengan `PersistentVolume` (PV), ini merepresentasikan **snapshot fisik** yang sebenarnya di backend storage.
    *   Biasanya dibuat **secara otomatis** oleh controller snapshot setelah snapshot fisik berhasil dibuat sebagai respons terhadap objek `VolumeSnapshot` (ini disebut *dynamic provisioning* snapshot).
    *   Berisi detail tentang snapshot (ID snapshot di backend, status, dll.) dan referensi kembali ke `VolumeSnapshot` yang memintanya.
    *   Memiliki `volumeSnapshotRef` (menunjuk ke `VolumeSnapshot`) dan `sourceVolumeHandle` (ID PV sumber).
    *   Juga memiliki `deletionPolicy` yang diwarisi dari `VolumeSnapshotClass`.

## Alur Kerja Membuat Snapshot

1.  **Pastikan Prasyarat:**
    *   Driver CSI yang mendukung snapshot sudah terinstal.
    *   Komponen `external-snapshotter` (controller dan CRDs snapshot) sudah terinstal di cluster.
    *   `VolumeSnapshotClass` yang menunjuk ke driver CSI tersebut sudah dibuat oleh admin.
    *   Anda memiliki `PersistentVolumeClaim` (PVC) yang ingin Anda snapshot, yang disediakan oleh driver CSI yang sama.
2.  **Buat Objek `VolumeSnapshot`:**
    *   Anda membuat manifest YAML untuk `VolumeSnapshot`.
    *   Tentukan `volumeSnapshotClassName` yang sesuai.
    *   Tentukan `source.persistentVolumeClaimName` dengan nama PVC sumber.
    *   Terapkan manifest: `kubectl apply -f my-snapshot-request.yaml`
3.  **Proses di Belakang Layar:**
    *   Controller snapshot mendeteksi `VolumeSnapshot` baru.
    *   Controller memanggil driver CSI untuk membuat snapshot fisik dari volume yang terkait dengan PVC sumber di backend storage.
    *   Setelah snapshot fisik siap, controller membuat objek `VolumeSnapshotContent` yang merepresentasikan snapshot tersebut.
    *   Controller mengikat `VolumeSnapshot` ke `VolumeSnapshotContent`.
4.  **Verifikasi:**
    *   Periksa status `VolumeSnapshot`: `kubectl get volumesnapshot <nama-snapshot> -n <namespace>`
    *   Cari field `status.readyToUse: true` dan `status.boundVolumeSnapshotContentName` yang terisi.
    *   (Opsional) Periksa `VolumeSnapshotContent`: `kubectl get volumesnapshotcontent <nama-vsc>`

## Alur Kerja Memulihkan dari Snapshot (Provision Volume Baru)

Cara paling umum untuk menggunakan snapshot adalah membuat PVC *baru* yang datanya dipulihkan dari snapshot tersebut.

1.  **Pastikan Snapshot Siap:** Pastikan `VolumeSnapshot` yang ingin Anda gunakan berstatus `readyToUse: true`.
2.  **Buat PVC Baru dari Snapshot:**
    *   Buat manifest YAML untuk `PersistentVolumeClaim` baru.
    *   **Penting:** Tambahkan field `spec.dataSource`:
        *   `name`: Nama objek `VolumeSnapshot` sumber.
        *   `kind`: `VolumeSnapshot`
        *   `apiGroup`: `snapshot.storage.k8s.io`
    *   Pastikan `storageClassName` di PVC baru ini sama dengan `StorageClass` dari PVC *asli* yang di-snapshot (atau StorageClass lain yang kompatibel dan didukung oleh driver CSI yang sama).
    *   `resources.requests.storage` harus setidaknya sebesar volume asli.
    *   Terapkan manifest PVC baru: `kubectl apply -f my-restored-pvc.yaml`
3.  **Proses di Belakang Layar:**
    *   External Provisioner (dari driver CSI) mendeteksi PVC baru dengan `dataSource`.
    *   Provisioner memanggil driver CSI untuk membuat volume fisik *baru* dan mengisi datanya dari snapshot yang ditentukan.
    *   Provisioner membuat objek `PV` baru untuk volume yang dipulihkan ini.
    *   PVC baru terikat ke PV baru.
4.  **Gunakan PVC Baru:** Setelah PVC baru berstatus `Bound`, Anda dapat menggunakannya di Pod baru seperti PVC biasa. Pod ini akan dimulai dengan data dari snapshot.

## Contoh YAML

```yaml
# 1. VolumeSnapshotClass (Dibuat oleh Admin)
apiVersion: snapshot.storage.k8s.io/v1
kind: VolumeSnapshotClass
metadata:
  name: csi-aws-ebs-snapclass # Nama kelas snapshot
driver: ebs.csi.aws.com # Driver CSI yang menangani snapshot
deletionPolicy: Delete # Hapus snapshot fisik saat VolumeSnapshot dihapus
# Parameter spesifik vendor (jika ada)
# parameters:
#   key: value
---
# 2. VolumeSnapshot (Dibuat oleh User)
apiVersion: snapshot.storage.k8s.io/v1
kind: VolumeSnapshot
metadata:
  name: my-db-snapshot-20231027
  namespace: database-prod
spec:
  volumeSnapshotClassName: csi-aws-ebs-snapclass # Merujuk ke kelas di atas
  source:
    persistentVolumeClaimName: my-database-pvc # Nama PVC yang akan di-snapshot
---
# 3. PVC Baru untuk Memulihkan dari Snapshot (Dibuat oleh User)
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: my-restored-db-pvc
  namespace: database-prod
spec:
  storageClassName: ebs-gp3-sc # Gunakan StorageClass asli atau yang kompatibel
  dataSource: # Tentukan sumber data adalah snapshot
    name: my-db-snapshot-20231027 # Nama VolumeSnapshot sumber
    kind: VolumeSnapshot
    apiGroup: snapshot.storage.k8s.io
  accessModes:
    - ReadWriteOnce # Harus cocok atau kompatibel dengan sumber
  resources:
    requests:
      storage: 10Gi # Harus >= ukuran volume asli
```

## Pertimbangan

*   **Konsistensi Aplikasi:** Membuat snapshot dari volume yang sedang aktif ditulis oleh aplikasi (seperti database) mungkin menghasilkan snapshot yang tidak konsisten secara aplikasi. Praktik terbaik seringkali melibatkan:
    *   **Meng-quiesce** aplikasi (menghentikan sementara penulisan).
    *   **Membekukan filesystem** (jika didukung OS dan driver CSI).
    *   Mengambil snapshot.
    *   Melepaskan aplikasi/filesystem.
    *   Beberapa driver CSI atau solusi backup mungkin memiliki mekanisme untuk membantu mengotomatiskan ini.
*   **Biaya:** Penyimpanan snapshot biasanya dikenakan biaya oleh penyedia storage. Kebijakan `deletionPolicy: Retain` dapat menyebabkan akumulasi biaya jika `VolumeSnapshotContent` tidak dibersihkan.
*   **Dukungan Driver:** Pastikan driver CSI Anda mendukung snapshot dan fitur pemulihan yang Anda butuhkan.

Volume Snapshots adalah fitur penting untuk manajemen data aplikasi stateful di Kubernetes, menyediakan mekanisme standar untuk backup dan cloning volume persisten.
