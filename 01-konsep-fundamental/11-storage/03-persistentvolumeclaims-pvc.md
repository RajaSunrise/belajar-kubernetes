# PersistentVolumeClaims (PVC)

PersistentVolumeClaim (PVC) adalah permintaan (*request*) untuk storage oleh pengguna (atau Pod). Ini mirip dengan bagaimana Pod mengonsumsi sumber daya CPU dan memori node. PVC memungkinkan pengguna untuk "mengklaim" sumber daya storage (PersistentVolume) tanpa perlu mengetahui detail infrastruktur storage yang mendasarinya.

## Mengapa Menggunakan PVC?

*   **Abstraksi untuk Pengguna:** Pengguna aplikasi (developer) tidak perlu peduli tentang bagaimana storage disediakan atau di mana lokasinya. Mereka hanya perlu meminta storage dengan spesifikasi tertentu (ukuran, mode akses).
*   **Pemisahan Peran:** Memisahkan tanggung jawab antara administrator cluster (yang menyediakan PV) dan pengguna aplikasi (yang mengonsumsi storage melalui PVC).
*   **Portabilitas:** Aplikasi yang didefinisikan dengan PVC lebih portabel antar cluster Kubernetes, selama cluster tujuan dapat memenuhi permintaan PVC tersebut (misalnya, melalui StorageClass).
*   **Manajemen Siklus Hidup:** PVC mengelola siklus hidup permintaan storage.

## Hubungan PVC dan PV

PVC dan PV memiliki hubungan *binding* (pengikatan):

1.  **Permintaan (PVC):** Pengguna membuat PVC yang mendefinisikan kebutuhan storage mereka (misalnya, 10GiB storage dengan mode akses ReadWriteOnce).
2.  **Pencocokan (Control Plane):** Control plane Kubernetes mencari PV yang tersedia yang memenuhi persyaratan dalam PVC (ukuran, mode akses, StorageClass, dll.).
3.  **Pengikatan (Binding):** Jika PV yang cocok ditemukan (atau dibuat secara dinamis oleh StorageClass), PV tersebut akan diikat (*bound*) ke PVC. PV tersebut menjadi eksklusif untuk PVC tersebut selama ikatan berlangsung.
4.  **Penggunaan (Pod):** Pod kemudian dapat me-mount PVC ini sebagai volume, memberinya akses ke storage yang disediakan oleh PV yang terikat.

Sebuah PVC hanya bisa diikat ke satu PV. Sebaliknya, sebuah PV juga hanya bisa diikat ke satu PVC (kecuali untuk beberapa mode akses seperti ReadOnlyMany atau ReadWriteMany, di mana beberapa Pod bisa menggunakan PVC yang sama).

## Contoh YAML PVC Sederhana

Berikut adalah contoh manifes YAML untuk PVC yang meminta 5GiB storage dengan mode akses ReadWriteOnce:

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: my-pvc # Nama PVC
spec:
  accessModes:
    - ReadWriteOnce # Mode akses yang diminta (hanya bisa di-mount oleh satu node)
  resources:
    requests:
      storage: 5Gi # Ukuran storage yang diminta
  # storageClassName: standard # Opsional: Nama StorageClass yang spesifik
  # selector: # Opsional: Untuk memilih PV dengan label tertentu
  #   matchLabels:
  #     disktype: ssd
```

**Penjelasan:**

*   `apiVersion: v1`: Menentukan versi API Kubernetes untuk objek PVC.
*   `kind: PersistentVolumeClaim`: Menentukan tipe objek adalah PVC.
*   `metadata.name`: Nama unik untuk PVC ini dalam namespace.
*   `spec`: Mendefinisikan spesifikasi permintaan storage.
    *   `accessModes`: Menentukan bagaimana volume dapat di-mount. Pilihan umum:
        *   `ReadWriteOnce` (RWO): Volume dapat di-mount sebagai read-write oleh satu node tunggal.
        *   `ReadOnlyMany` (ROX): Volume dapat di-mount sebagai read-only oleh banyak node.
        *   `ReadWriteMany` (RWX): Volume dapat di-mount sebagai read-write oleh banyak node.
        *   `ReadWriteOncePod` (RWOP): Volume dapat di-mount sebagai read-write oleh satu Pod tunggal. (Fitur Alpha/Beta)
    *   `resources.requests.storage`: Jumlah storage minimum yang diminta. Kubernetes akan mencari PV yang setidaknya sebesar ini.
    *   `storageClassName` (Opsional): Jika ditentukan, PVC hanya akan diikat ke PV dari StorageClass ini, atau StorageClass ini akan digunakan untuk provisi dinamis. Jika dihilangkan atau kosong, perilaku tergantung pada konfigurasi cluster (mungkin menggunakan StorageClass default).
    *   `selector` (Opsional): Memungkinkan Anda mempersempit pemilihan PV berdasarkan label pada PV.

## Siklus Hidup PVC

1.  **Pending:** PVC telah dibuat tetapi belum ada PV yang cocok dan terikat. Ini bisa terjadi jika tidak ada PV yang memenuhi syarat atau jika provisi dinamis sedang berlangsung.
2.  **Bound:** PVC telah berhasil diikat ke sebuah PV.
3.  **Lost:** PVC kehilangan ikatannya ke PV (misalnya, jika objek PV dihapus secara manual). Data pada volume mungkin masih ada, tetapi PVC tidak lagi terhubung.

Ketika sebuah Pod yang menggunakan PVC dihapus, PVC dan PV yang terikat tetap ada. Data pada volume juga tetap ada. Perilaku saat PVC dihapus tergantung pada *reclaim policy* dari PV yang terikat (`Retain`, `Delete`, atau `Recycle`).

## Menggunakan PVC dalam Pod

Pod mereferensikan PVC berdasarkan nama untuk menggunakannya sebagai volume:

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: my-pod
spec:
  containers:
    - name: my-container
      image: nginx
      volumeMounts:
      - mountPath: "/usr/share/nginx/html" # Path di dalam container
        name: my-storage # Nama volume, harus cocok dengan nama di bawah
  volumes:
    - name: my-storage # Nama volume
      persistentVolumeClaim:
        claimName: my-pvc # Nama PVC yang ingin digunakan
```

Dalam contoh ini, Pod `my-pod` akan me-mount volume yang disediakan oleh PVC `my-pvc` ke direktori `/usr/share/nginx/html` di dalam container `my-container`.

PVC adalah mekanisme kunci untuk mengelola stateful application di Kubernetes, memungkinkan aplikasi meminta dan menggunakan storage persisten secara fleksibel dan terabstraksi.
