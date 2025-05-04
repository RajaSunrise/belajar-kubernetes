# PersistentVolumes (PV): Abstraksi Sumber Daya Penyimpanan Cluster

Kita telah membahas `Volumes` sebagai cara untuk menyediakan direktori penyimpanan ke Pods. Namun, banyak tipe Volume (seperti `emptyDir`) memiliki siklus hidup yang terikat pada Pod – datanya hilang saat Pod dihapus. Untuk aplikasi stateful yang membutuhkan data untuk **bertahan (persist)** lebih lama dari siklus hidup Pod individual, Kubernetes menyediakan mekanisme lain: **PersistentVolume (PV)** dan **PersistentVolumeClaim (PVC)**.

## Apa itu PersistentVolume (PV)?

**PersistentVolume (PV)** adalah **sepotong penyimpanan (piece of storage)** di dalam cluster yang telah disediakan (provisioned) oleh administrator atau secara dinamis menggunakan [StorageClasses](./04-storageclasses.md). PV adalah **sumber daya di dalam cluster**, sama seperti Node adalah sumber daya komputasi cluster.

**Analog:** Anggap PV seperti "hard disk", "Network Attached Storage (NAS) share", atau "Logical Unit Number (LUN)" yang tersedia untuk digunakan oleh cluster, tetapi diabstraksi dari implementasi spesifiknya.

**Karakteristik Utama PV:**

1.  **Siklus Hidup Independen:** Siklus hidup PV **terpisah** dari Pod mana pun yang mungkin menggunakannya. Data pada PV dapat bertahan meskipun Pod yang menggunakannya dihapus atau dijadwal ulang.
2.  **Abstraksi Implementasi:** Definisi PV menyembunyikan detail implementasi penyimpanan yang mendasarinya (apakah itu disk AWS EBS, GCE Persistent Disk, Azure Disk, NFS share, Ceph, dll.) dari pengguna yang akan mengkonsumsinya (melalui PVC).
3.  **Cluster-Scoped:** PV adalah objek **tingkat cluster**, artinya **tidak terikat pada Namespace** tertentu.
4.  **Disediakan (Provisioned):** PV dapat disediakan dengan dua cara:
    *   **Statis (Static Provisioning):** Administrator cluster secara manual membuat sejumlah PV terlebih dahulu. PV ini membawa detail infrastruktur penyimpanan nyata yang sudah ada. Administrator perlu mengetahui detail penyimpanan tersebut (misalnya, ID volume EBS, alamat server NFS).
    *   **Dinamis (Dynamic Provisioning):** Ketika tidak ada PV statis yang cocok dengan permintaan `PersistentVolumeClaim` (PVC), cluster dapat secara otomatis membuat (memprovisikan) PV baru sesuai permintaan, menggunakan `StorageClass`. Ini adalah metode yang lebih umum di lingkungan cloud.

## Atribut Penting dalam Spesifikasi PV (`spec`)

Definisi YAML sebuah PV mencakup beberapa field penting:

*   **`capacity`:** Menentukan ukuran penyimpanan volume. Saat ini hanya `storage` yang didukung. Contoh: `capacity: { storage: 10Gi }`.
*   **`volumeMode`:** Menentukan apakah volume akan digunakan sebagai `Filesystem` (default, diformat dengan filesystem dan di-mount ke direktori Pod) atau `Block` (disajikan sebagai perangkat block mentah ke Pod tanpa filesystem).
*   **`accessModes`:** Menentukan **bagaimana volume dapat di-mount** oleh Node(s)/Pod(s). Ini adalah **kemampuan** yang didukung oleh volume fisik, bukan penegakan akses tulis aplikasi. Nilai yang mungkin (bisa lebih dari satu):
    *   `ReadWriteOnce` (RWO): Volume dapat di-mount sebagai read-write oleh **satu Node tunggal** pada satu waktu. Cocok untuk block storage (EBS, GCE PD, Azure Disk).
    *   `ReadOnlyMany` (ROX): Volume dapat di-mount sebagai read-only oleh **banyak Node** secara bersamaan.
    *   `ReadWriteMany` (RWX): Volume dapat di-mount sebagai read-write oleh **banyak Node** secara bersamaan. Cocok untuk shared file systems (NFS, CephFS, GlusterFS).
    *   `ReadWriteOncePod` (RWOP) (Lebih baru): Volume dapat di-mount sebagai read-write oleh **satu Pod tunggal** pada satu waktu (bahkan jika Pod pindah Node). Membutuhkan dukungan driver CSI.
    *   **Penting:** PV hanya dapat terikat ke PVC yang meminta mode akses yang *kompatibel* (terkandung dalam `accessModes` PV).
*   **`storageClassName`:** Nama [StorageClass](./04-storageclasses.md) tempat PV ini berasal. PV dengan kelas tertentu hanya akan terikat ke PVC yang meminta kelas tersebut (atau PVC tanpa kelas jika PV tidak punya kelas dan tidak ada SC default). Penting untuk dynamic provisioning dan pencocokan statis.
*   **`persistentVolumeReclaimPolicy`:** Menentukan apa yang terjadi pada PV (dan volume fisik di backend) ketika `PersistentVolumeClaim` (PVC) yang terikat padanya **dihapus**. Pilihan:
    *   **`Retain` (Default untuk PV Statis):** PV **tidak** dihapus. Ia masuk ke status `Released`. Data pada volume fisik tetap utuh. Administrator perlu membersihkan data secara manual (jika perlu) dan kemudian menghapus objek PV atau mengeditnya agar dapat digunakan kembali oleh PVC lain. **Paling aman untuk data produksi.**
    *   **`Delete` (Default untuk PV Dinamis via StorageClass):** Baik objek PV Kubernetes *maupun* sumber daya penyimpanan fisik di infrastruktur backend (misalnya, disk EBS/GCE/Azure) akan **dihapus**. **Data hilang!** Gunakan dengan hati-hati, tetapi nyaman untuk dynamic provisioning di mana volume mudah dibuat ulang.
    *   **`Recycle` (Deprecated):** Mencoba melakukan pembersihan dasar pada volume (misalnya, `rm -rf /volume/*`). **Tidak aman** dan tidak direkomendasikan lagi. Jangan digunakan.
*   **Plugin Volume Spesifik:** Bagian ini berisi detail konfigurasi untuk tipe penyimpanan yang sebenarnya. Contoh:
    *   `nfs: { path: /exports/data, server: 192.168.1.100 }`
    *   `awsElasticBlockStore: { volumeID: vol-xxxxxxxx, fsType: ext4 }`
    *   `csi: { driver: ..., volumeHandle: ..., ... }` (Untuk driver CSI)
    *   Dan banyak lagi (`gcePersistentDisk`, `azureDisk`, `azureFile`, `cephfs`, `iscsi`, dll.)

## Siklus Hidup (Fase) PV

Sebuah PV dapat berada dalam salah satu fase berikut:

*   **`Available`:** Sumber daya bebas yang belum terikat ke PVC. Siap untuk diklaim.
*   **`Bound`:** PV telah terikat ke sebuah PVC.
*   **`Released`:** PVC yang terikat padanya telah dihapus, tetapi sumber daya PV belum diambil kembali oleh cluster (biasanya karena `reclaimPolicy: Retain`). PV tidak tersedia untuk klaim lain.
*   **`Failed`:** PV gagal dalam proses provisioning otomatis atau mengalami kesalahan lain.

## Contoh YAML PV (Static Provisioning - NFS)

Ini adalah contoh administrator membuat PV secara manual yang menunjuk ke NFS share yang sudah ada.

```yaml
# nfs-pv-static.yaml
apiVersion: v1
kind: PersistentVolume
metadata:
  name: my-nfs-data-pv # Nama unik untuk PV di cluster
  # labels: # Bisa tambahkan label utk memfilter/memilih PV
  #   storage-type: nfs-shared
spec:
  capacity:
    storage: 50Gi # Kapasitas volume ini
  volumeMode: Filesystem # Mode volume (default)
  accessModes:
    # Mode akses yang didukung oleh NFS share ini
    - ReadWriteMany # RWX umum untuk NFS
    - ReadOnlyMany  # ROX juga mungkin
  persistentVolumeReclaimPolicy: Retain # Jaga data & PV jika PVC dihapus
  storageClassName: "slow-nfs-storage" # Nama kelas (opsional, utk pencocokan PVC)
  mountOptions: # Opsi mount NFS (opsional)
    - hard
    - nfsvers=4.1
  nfs: # Detail spesifik plugin volume NFS
    path: /mnt/shared/my-app-data # Path di server NFS
    server: 10.10.0.50 # Alamat IP server NFS
    # readOnly: false # Defaultnya false
```

**Penting:** Pengguna biasa (developer) biasanya **tidak** berinteraksi langsung dengan PV. Mereka berinteraksi dengan **PersistentVolumeClaim (PVC)**, yang merupakan *permintaan* untuk menggunakan PV. PV adalah tanggung jawab administrator cluster atau sistem provisioning dinamis.

PV menyediakan abstraksi penting yang memisahkan detail penyediaan penyimpanan dari kebutuhan konsumsi penyimpanan oleh aplikasi, memungkinkan pengelolaan storage yang lebih fleksibel dan portabel di Kubernetes.
