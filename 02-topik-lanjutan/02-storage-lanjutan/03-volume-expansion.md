# Perluasan Volume (Volume Expansion)

Seiring waktu, kebutuhan penyimpanan aplikasi dapat bertambah. Menghadapi PVC (PersistentVolumeClaim) yang hampir penuh adalah skenario umum. Daripada membuat volume baru yang lebih besar dan memigrasikan data secara manual (yang bisa rumit dan menyebabkan downtime), Kubernetes menyediakan kemampuan untuk **memperluas (expand)** ukuran PVC yang sudah ada secara *online* (tanpa perlu melepas volume dari Pod) atau *offline*.

**Penting:** Kemampuan untuk memperluas volume bergantung pada dua hal:

1.  **Dukungan dari Driver CSI:** Driver CSI yang menyediakan penyimpanan untuk PV yang terikat pada PVC Anda **harus** mendukung operasi perluasan volume. Tidak semua driver atau sistem penyimpanan mendukung ini.
2.  **Konfigurasi `StorageClass`:** Objek `StorageClass` yang digunakan untuk membuat PV (baik secara dinamis maupun statis) **harus** memiliki field `allowVolumeExpansion: true`. Jika tidak disetel ke `true`, Kubernetes tidak akan mengizinkan upaya perluasan pada PVC yang menggunakan StorageClass tersebut.

## Cara Kerja Volume Expansion

Ada dua mode utama perluasan:

**1. Perluasan Online (Online Expansion):**
   *   Volume diperluas **tanpa** perlu menghentikan atau me-restart Pod yang sedang menggunakannya.
   *   Ini adalah mode yang paling diinginkan karena tidak menyebabkan downtime aplikasi.
   *   Membutuhkan dukungan penuh dari driver CSI dan sistem penyimpanan backend.

**2. Perluasan Offline (Offline Expansion):**
   *   Memerlukan Pod yang menggunakan volume tersebut untuk **dihentikan dan dimulai ulang** agar perluasan filesystem dapat terjadi.
   *   Driver CSI mungkin hanya mendukung perluasan pada level block device saat volume tidak digunakan.
   *   Jika perluasan online tidak didukung atau gagal, ini mungkin menjadi fallback.

Kubernetes (melalui `PersistentVolumeController` dan Kubelet berkoordinasi dengan driver CSI) mencoba melakukan perluasan online terlebih dahulu jika didukung.

## Alur Kerja Memperluas PVC

1.  **Verifikasi Prasyarat:**
    *   Periksa `StorageClass` yang digunakan oleh PVC Anda: `kubectl get sc <nama-storageclass> -o yaml`. Pastikan `allowVolumeExpansion: true`.
    *   Periksa dokumentasi driver CSI Anda untuk memastikan ia mendukung perluasan volume (online atau offline).
2.  **Edit Objek PVC:**
    *   Ubah ukuran yang diminta dalam spesifikasi PVC. Anda **hanya bisa menambah ukuran**, tidak bisa menguranginya.
    *   Gunakan `kubectl edit pvc <nama-pvc> -n <namespace>`.
    *   Cari bagian `spec.resources.requests.storage` dan ubah nilainya ke ukuran baru yang lebih besar (misalnya, dari `10Gi` menjadi `20Gi`).
    *   Simpan perubahan.
3.  **Proses di Belakang Layar:**
    *   Kubernetes mendeteksi perubahan pada `spec.resources.requests.storage` PVC.
    *   Sebuah *kondisi* (`PersistentVolumeClaimResizing`) akan ditambahkan ke status PVC.
    *   Controller (biasanya `external-resizer` jika menggunakan CSI) memanggil driver CSI untuk memperluas volume fisik di backend storage.
    *   **Jika Perluasan Online Didukung:**
        *   Setelah volume fisik diperluas, Kubelet di Node tempat Pod berjalan akan diberi tahu.
        *   Kubelet (berkoordinasi dengan Node Plugin CSI) akan memicu perluasan *filesystem* di dalam volume yang sudah ter-mount ke Pod, secara online.
    *   **Jika Hanya Perluasan Offline Didukung:**
        *   Volume fisik diperluas, tetapi filesystem belum.
        *   Kondisi `FileSystemResizePending` mungkin ditambahkan ke status PVC.
        *   Anda perlu **me-restart Pod** yang menggunakan PVC tersebut. Saat Pod baru dimulai dan me-mount volume, Kubelet/Node Plugin CSI akan melakukan perluasan filesystem sebelum mount selesai.
4.  **Verifikasi Perluasan:**
    *   Periksa kembali ukuran PVC: `kubectl get pvc <nama-pvc> -n <namespace> -o yaml`. Lihat `status.capacity.storage`. Ukuran ini akan diperbarui setelah filesystem berhasil diperluas.
    *   Periksa kondisi PVC: `kubectl describe pvc <nama-pvc> -n <namespace>`. Cari event atau kondisi terkait perluasan.
    *   Masuk ke dalam Pod (`kubectl exec -it <pod-name> -- /bin/sh`) dan jalankan `df -h <mount-path>` untuk melihat ukuran filesystem yang terlihat oleh aplikasi.

## Contoh: Memperluas PVC

Misalkan kita punya PVC:

```yaml
# pvc-lama.yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: my-data
spec:
  accessModes: [ReadWriteOnce]
  storageClassName: gp3-expandable # Anggap SC ini punya allowVolumeExpansion: true
  resources:
    requests:
      storage: 10Gi
```

Kita ingin memperluasnya menjadi 20Gi:

```bash
# Edit PVC secara interaktif
kubectl edit pvc my-data

# Atau buat file patch (misal: patch-pvc.yaml):
# spec:
#   resources:
#     requests:
#       storage: 20Gi

# Terapkan patch:
# kubectl patch pvc my-data --patch-file patch-pvc.yaml

# Atau langsung patch dari command line:
kubectl patch pvc my-data -p '{"spec":{"resources":{"requests":{"storage":"20Gi"}}}}'
```

Setelah itu, pantau status PVC dan Pod:

```bash
# Lihat status PVC, perhatikan capacity dan conditions
kubectl get pvc my-data -o yaml

# Jika perluasan filesystem tertunda, restart Pod terkait
# kubectl delete pod <nama-pod-yang-menggunakan-pvc>
# (Deployment/StatefulSet akan membuat ulang Pod)

# Verifikasi ukuran di dalam Pod
# kubectl exec -it <nama-pod-baru> -- df -h /path/ke/mount
```

## Pertimbangan

*   **Dukungan Driver:** Fitur ini sangat bergantung pada driver CSI. Selalu periksa dokumentasi vendor.
*   **Irreversible:** Anda tidak dapat mengurangi ukuran PVC setelah diperluas melalui mekanisme ini.
*   **Perluasan Filesystem:** Langkah perluasan filesystem setelah volume fisik diperluas adalah krusial. Perluasan online lebih disukai. Jika offline, pastikan Anda me-restart Pod.
*   **Biaya:** Volume yang lebih besar biasanya berarti biaya storage yang lebih tinggi.

Volume expansion menyediakan cara yang nyaman untuk menyesuaikan kapasitas penyimpanan aplikasi Anda seiring pertumbuhan kebutuhan, seringkali dengan dampak minimal pada ketersediaan aplikasi jika perluasan online didukung.
