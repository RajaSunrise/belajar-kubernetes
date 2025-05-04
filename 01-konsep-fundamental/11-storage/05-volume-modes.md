# Mode Volume: Filesystem vs. Block

Saat mendefinisikan `PersistentVolume` (PV) dan meminta penyimpanan melalui `PersistentVolumeClaim` (PVC), Anda dapat menentukan **bagaimana** volume tersebut akan disajikan ke Pod. Ini dikontrol oleh field `volumeMode`.

Ada dua mode volume utama:

## 1. `Filesystem` (Default)

*   **Deskripsi:** Ini adalah mode **default** jika `volumeMode` tidak ditentukan. Ketika volume dengan mode `Filesystem` di-mount ke dalam Pod, Kubelet akan **membuat filesystem** pada perangkat penyimpanan block (jika belum ada) sebelum me-mount-nya ke direktori (`mountPath`) yang ditentukan di dalam kontainer.
*   **Cara Kerja:**
    1.  PV merepresentasikan perangkat block (misalnya, disk EBS, GCE PD, iSCSI LUN).
    2.  Saat Pod dijadwalkan dan perlu me-mount PVC yang terikat ke PV ini:
        *   Kubelet (atau driver CSI) memastikan perangkat block terpasang ke Node.
        *   Kubelet memeriksa apakah perangkat tersebut sudah memiliki filesystem (sesuai `fsType` yang mungkin ditentukan di PV atau StorageClass).
        *   Jika **belum** ada filesystem, Kubelet akan **memformat** perangkat tersebut dengan filesystem yang ditentukan (misalnya, `ext4`, `xfs`). **Perhatian:** Ini akan menghapus data yang ada jika perangkat sudah berisi data tetapi tidak ada filesystem yang dikenali.
        *   Kubelet kemudian **me-mount** filesystem tersebut ke direktori sementara di Node host.
        *   Akhirnya, direktori mount di Node host tersebut diikat (bind mount) ke `mountPath` di dalam kontainer Pod.
*   **Akses di Kontainer:** Aplikasi di dalam kontainer melihat dan berinteraksi dengan volume sebagai **direktori biasa** dalam filesystem-nya.
*   **Kasus Penggunaan:** Mode yang paling umum digunakan untuk hampir semua kasus penggunaan penyimpanan persisten, seperti menyimpan file data aplikasi, log persisten, aset web, dll.

**Contoh Definisi (Implisit Default):**

```yaml
# --- PV ---
apiVersion: v1
kind: PersistentVolume
metadata:
  name: my-filesystem-pv
spec:
  capacity: { storage: 10Gi }
  accessModes: [ "ReadWriteOnce" ]
  # volumeMode: Filesystem # <-- Default, bisa dihilangkan
  storageClassName: "standard"
  csi: # Contoh CSI
    driver: pd.csi.storage.gke.io
    volumeHandle: projects/gcp-project/zones/us-central1-c/disks/my-data-disk
    fsType: ext4 # Opsional: tentukan filesystem

# --- PVC ---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: my-filesystem-pvc
spec:
  accessModes: [ "ReadWriteOnce" ]
  resources: { requests: { storage: 10Gi } }
  storageClassName: "standard"
  # volumeMode: Filesystem # <-- Default, bisa dihilangkan

# --- Pod ---
apiVersion: v1
kind: Pod
metadata:
  name: my-app-pod
spec:
  containers:
  - name: my-app
    image: my-app-image
    volumeMounts:
    - mountPath: "/app/data" # Volume akan terlihat sbg direktori di sini
      name: my-storage
  volumes:
  - name: my-storage
    persistentVolumeClaim:
      claimName: my-filesystem-pvc
```

## 2. `Block`

*   **Deskripsi:** Mode ini menyajikan volume penyimpanan sebagai **perangkat block mentah (raw block device)** langsung ke dalam Pod, **tanpa filesystem** di atasnya.
*   **Cara Kerja:**
    1.  PV merepresentasikan perangkat block.
    2.  Saat Pod me-mount PVC yang terikat ke PV mode `Block`:
        *   Kubelet memastikan perangkat block terpasang ke Node.
        *   Kubelet membuat **symlink** di dalam kontainer (pada `volumeDevices.devicePath` yang ditentukan) yang menunjuk ke perangkat block di Node host (misalnya, `/dev/sdb`).
    *   **Tidak ada proses format atau mounting filesystem** yang dilakukan oleh Kubelet.
*   **Akses di Kontainer:** Aplikasi di dalam kontainer mendapatkan akses langsung ke perangkat block (misalnya, `/dev/my-raw-disk`). Aplikasi bertanggung jawab penuh untuk berinteraksi langsung dengan perangkat block tersebut (misalnya, menggunakan system calls seperti `open`, `read`, `write`, `ioctl` pada device path).
*   **Kasus Penggunaan:**
    *   **Database Kinerja Tinggi:** Beberapa database (seperti Oracle, atau yang dioptimalkan khusus) dapat memperoleh kinerja I/O yang lebih baik dengan mengelola penyimpanannya sendiri langsung di perangkat block mentah, melewati overhead filesystem kernel.
    *   **Aplikasi Sadar Penyimpanan (Storage-Aware):** Aplikasi yang dirancang untuk mengelola tata letak data mereka sendiri di tingkat block.
    *   **Sistem File Kustom:** Menjalankan sistem file kustom di atas perangkat block dari dalam kontainer.
*   **Peringatan:** Mode ini jauh lebih kompleks untuk digunakan oleh aplikasi. Aplikasi harus dirancang secara eksplisit untuk bekerja dengan perangkat block mentah. Kesalahan dalam mengelola perangkat block dapat dengan mudah menyebabkan kerusakan data.

**Contoh Definisi:**

```yaml
# --- PV ---
apiVersion: v1
kind: PersistentVolume
metadata:
  name: my-block-pv
spec:
  capacity: { storage: 100Gi }
  accessModes: [ "ReadWriteOnce" ]
  volumeMode: Block # <-- Mode Block ditentukan
  storageClassName: "high-iops-block"
  csi:
    driver: ebs.csi.aws.com
    volumeHandle: vol-0abcdef1234567890

# --- PVC ---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: my-block-pvc
spec:
  accessModes: [ "ReadWriteOnce" ]
  resources: { requests: { storage: 100Gi } }
  storageClassName: "high-iops-block"
  volumeMode: Block # <-- Mode Block HARUS cocok dgn PV

# --- Pod ---
apiVersion: v1
kind: Pod
metadata:
  name: my-db-pod-raw
spec:
  containers:
  - name: high-perf-db
    image: my-custom-db-image
    # Tidak ada 'volumeMounts' untuk mode Block
    volumeDevices: # Gunakan 'volumeDevices' sebagai gantinya
    - name: my-raw-storage # Nama volume (harus cocok dgn 'volumes')
      devicePath: /dev/xvdz # Path perangkat yg akan dibuat di dlm kontainer
                           # Ini akan jadi symlink ke perangkat block host
  volumes:
  - name: my-raw-storage # Nama volume
    persistentVolumeClaim:
      claimName: my-block-pvc
```
Di dalam kontainer `high-perf-db`, aplikasi sekarang dapat membuka dan berinteraksi langsung dengan perangkat `/dev/xvdz`.

## Ringkasan

| Fitur               | `Filesystem` (Default)                 | `Block`                                       |
|---------------------|----------------------------------------|-----------------------------------------------|
| **Penyajian ke Pod** | Direktori yang di-mount               | Perangkat block mentah (via device path)      |
| **Filesystem**      | Dibuat/Dikelola oleh Kubelet/CSI       | Tidak ada (Aplikasi mengelola jika perlu)   |
| **Akses Aplikasi**  | Operasi file standar (read, write)    | Operasi block device mentah (ioctl, dll.)   |
| **Kompleksitas App**| Rendah                                 | Tinggi (Membutuhkan desain aplikasi khusus) |
| **Use Case Umum**  | Mayoritas aplikasi, data file        | Database kinerja tinggi, aplikasi storage-aware |

Pilih `volumeMode` yang sesuai dengan kebutuhan aplikasi Anda. Untuk sebagian besar kasus, `Filesystem` adalah pilihan yang tepat dan jauh lebih mudah digunakan. Gunakan `Block` hanya jika aplikasi Anda secara spesifik dirancang untuk dan mendapat manfaat dari akses block device mentah.
