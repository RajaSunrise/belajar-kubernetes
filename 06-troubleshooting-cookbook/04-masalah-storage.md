# Troubleshooting Masalah Penyimpanan (Storage) Kubernetes

Masalah terkait penyimpanan persisten (PersistentVolumes, PersistentVolumeClaims, StorageClasses) dapat menyebabkan Pod gagal start (`Pending`, `ContainerCreating`) atau aplikasi gagal berfungsi karena tidak dapat membaca/menulis data.

**Alat Diagnostik Utama:**

*   `kubectl get pvc <nama-pvc> -n <namespace>`: Melihat status PVC (Pending, Bound, Lost).
*   `kubectl describe pvc <nama-pvc> -n <namespace>`: **Penting!** Menampilkan detail PVC, termasuk Events yang sering menunjukkan alasan kegagalan binding.
*   `kubectl get pv <nama-pv>`: Melihat status PV (Available, Bound, Released, Failed).
*   `kubectl describe pv <nama-pv>`: Melihat detail PV, termasuk `ClaimRef` (PVC mana yang terikat) dan Events.
*   `kubectl get storageclass <nama-sc>`: Melihat status StorageClass.
*   `kubectl describe storageclass <nama-sc>`: Melihat detail StorageClass (Provisioner, Parameters, ReclaimPolicy, VolumeBindingMode).
*   `kubectl describe pod <nama-pod> -n <namespace>`: Periksa `Events` untuk pesan `FailedMount` atau `FailedAttachVolume`.
*   `kubectl logs ...`: Periksa log dari Pod driver CSI (jika menggunakan CSI) atau Pod aplikasi jika error terjadi saat runtime.
*   Log Kubelet di Node (`journalctl -u kubelet`): Sering berisi detail tentang operasi mounting/unmounting volume.

## Masalah 1: PVC Stuck dalam Status `Pending`

PVC telah dibuat, tetapi tidak dapat menemukan atau terikat ke PV yang sesuai. Pod yang mencoba menggunakan PVC ini juga akan tetap `Pending`.

**Kemungkinan Penyebab & Diagnosa:**

1.  **Tidak Ada PV yang Cocok (Static Provisioning):** Anda mengandalkan PV yang dibuat manual, tetapi tidak ada PV yang *Available* yang memenuhi persyaratan `accessModes`, `resources.requests.storage`, dan (jika ditentukan) `storageClassName` dari PVC.
    *   **Diagnosa:**
        *   `kubectl describe pvc <nama-pvc>` -> Periksa `Events`. Cari pesan seperti `no persistent volumes available for this claim` atau sejenisnya.
        *   `kubectl get pv`: Lihat daftar PV yang tersedia. Periksa kapasitas, access modes, dan storage class nya. Bandingkan dengan permintaan PVC.
    *   **Solusi:** Buat PV manual yang cocok dengan permintaan PVC, atau sesuaikan permintaan PVC agar cocok dengan PV yang tersedia.
2.  **StorageClass Salah atau Tidak Ada (Dynamic Provisioning):** PVC menentukan `storageClassName` yang tidak ada, atau tidak menentukan `storageClassName` tetapi tidak ada StorageClass *default* yang dikonfigurasi di cluster.
    *   **Diagnosa:**
        *   `kubectl describe pvc <nama-pvc>` -> Periksa `Events`. Cari pesan seperti `provisioning failed: storageclass "<nama>" not found`.
        *   `kubectl get storageclass`: Lihat daftar StorageClass yang ada. Periksa apakah ada yang ditandai `(default)`.
    *   **Solusi:** Perbaiki `storageClassName` di PVC, buat StorageClass yang diperlukan, atau tandai salah satu StorageClass yang ada sebagai default (`kubectl patch storageclass <nama-sc> -p '{"metadata": {"annotations":{"storageclass.kubernetes.io/is-default-class":"true"}}}'`).
3.  **Masalah Provisioner Dinamis:** StorageClass ada, tetapi provisioner yang ditentukannya (misalnya, driver CSI atau provisioner internal) gagal membuat volume fisik di backend storage.
    *   **Diagnosa:**
        *   `kubectl describe pvc <nama-pvc>` -> Periksa `Events`. Cari pesan error dari provisioner, misalnya `provisioning failed: ... <detail error dari backend storage>`.
        *   Periksa **log dari Pod provisioner** (seringkali Deployment/StatefulSet yang terkait dengan driver CSI, misalnya `ebs-csi-controller`, `gce-pd-csi-driver-controller`). Namespace bisa `kube-system` atau namespace terpisah.
        *   Periksa kuota atau limit di sisi backend storage (misalnya, batas jumlah disk EBS di akun AWS Anda).
    *   **Solusi:** Selesaikan masalah pada provisioner atau backend storage berdasarkan pesan error log. Periksa konfigurasi StorageClass `parameters`. Pastikan provisioner memiliki izin yang benar untuk membuat resource di backend.
4.  **VolumeBindingMode `WaitForFirstConsumer` dan Masalah Penjadwalan Pod:** Jika StorageClass menggunakan `volumeBindingMode: WaitForFirstConsumer`, provisioning PV ditunda sampai Pod yang menggunakan PVC dijadwalkan. Jika Pod *tidak bisa* dijadwalkan karena alasan lain (resource tidak cukup, taint, dll.), PVC akan tetap `Pending`.
    *   **Diagnosa:** `kubectl describe pvc <nama-pvc>` -> Events mungkin menunjukkan `waiting for first consumer to be created`. Kemudian, `kubectl describe pod <nama-pod-pengguna>` -> Periksa `Events` untuk melihat *mengapa* Pod gagal dijadwalkan.
    *   **Solusi:** Selesaikan masalah penjadwalan Pod terlebih dahulu (lihat [Troubleshooting Pod Pending](./02-masalah-pod.md#1-status-pending)). Setelah Pod bisa dijadwalkan, provisioning PV seharusnya dimulai.

## Masalah 2: Pod Stuck di `ContainerCreating` dengan Error `FailedMount` atau `FailedAttachVolume`

Pod telah dijadwalkan ke Node, tetapi Kubelet gagal me-mount volume yang ditentukan dalam Pod spec (terutama untuk PVC).

**Kemungkinan Penyebab & Diagnosa:**

1.  **Masalah Driver CSI / Plugin Volume di Node:** Komponen Node dari driver storage (misalnya, Pod DaemonSet `ebs-csi-node`, `nfs-client-provisioner`) mengalami masalah saat melakukan operasi mount di Node host.
    *   **Diagnosa:**
        *   `kubectl describe pod <nama-pod>` -> Periksa `Events` untuk detail error `FailedMount`. Pesan error seringkali berasal dari Kubelet atau driver.
        *   Periksa **log Kubelet** di Node tempat Pod dijadwalkan (`journalctl -u kubelet`). Cari pesan error terkait mounting volume dengan nama PVC/PV.
        *   Periksa **log Pod driver CSI/plugin Node** yang berjalan di Node tersebut (biasanya DaemonSet).
    *   **Solusi:** Debug masalah pada driver CSI/plugin di Node. Pastikan Pod driver berjalan, konfigurasinya benar, dan memiliki izin/kemampuan OS yang diperlukan untuk melakukan mount. Restart Pod driver atau Kubelet mungkin membantu.
2.  **Volume Sedang Digunakan oleh Node Lain (Khusus RWO):** PVC menggunakan `accessModes: ReadWriteOnce`, tetapi volume fisik (misalnya, disk EBS/GCE) masih ter-attach ke Node *lain* (mungkin dari Pod sebelumnya yang belum sepenuhnya dilepas). Kubernetes tidak dapat me-mount volume RWO ke lebih dari satu Node secara bersamaan.
    *   **Diagnosa:** `kubectl describe pod <nama-pod>` -> Events `FailedAttachVolume` atau `FailedMount` mungkin menyebutkan "Multi-Attach error" atau "volume is already exclusively attached to one node". Periksa `status.attachedVolumes` pada objek Node (`kubectl get node <nama-node> -o yaml`).
    *   **Solusi:** Tunggu beberapa saat hingga Kubernetes berhasil melepaskan volume dari Node lama. Jika stuck, Anda mungkin perlu secara manual melepaskan (detach) volume dari Node lama melalui API cloud provider atau alat storage backend. Pastikan Pod sebelumnya benar-benar dihentikan.
3.  **Masalah Jaringan ke Storage Backend (NFS, iSCSI, dll.):** Node tidak dapat mencapai server storage jaringan.
    *   **Diagnosa:** `describe pod` -> Events `FailedMount` mungkin menunjukkan timeout atau error koneksi. Coba lakukan mount secara manual atau uji konektivitas (`ping`, `telnet <nfs-server> 2049`) dari Node host ke server storage.
    *   **Solusi:** Perbaiki masalah konektivitas jaringan antara Node dan server storage. Periksa konfigurasi firewall.
4.  **Masalah Izin pada Volume Fisik:** Proses di dalam kontainer tidak memiliki izin yang benar untuk membaca/menulis ke direktori yang di-mount.
    *   **Diagnosa:** Ini biasanya terjadi *setelah* Pod `Running` tetapi aplikasi gagal. Periksa log aplikasi untuk error "Permission denied". Periksa `securityContext` Pod (`runAsUser`, `runAsGroup`, `fsGroup`). Periksa izin direktori di dalam kontainer (`kubectl exec <pod> -- ls -ld /path/to/mount`). Periksa opsi mount pada PV atau StorageClass.
    *   **Solusi:** Sesuaikan `fsGroup` di `securityContext.pod`, gunakan Init Container untuk `chown`/`chmod` direktori mount (jika memungkinkan), atau sesuaikan izin pada sistem file PV itu sendiri.
5.  **Node Kehabisan Ruang Disk (Untuk `emptyDir` non-memori):** Jika menggunakan `emptyDir` yang berbasis disk, Node mungkin kehabisan ruang.
    *   **Diagnosa:** `describe pod` -> Events mungkin menunjukkan `FailedMount ... no space left on device`. Periksa penggunaan disk Node (`df -h` via `kubectl exec` ke Pod lain di node atau SSH).
    *   **Solusi:** Bersihkan ruang disk di Node, atau pindahkan Pod ke Node lain. Gunakan `emptyDir.medium: Memory` jika sesuai.

## Masalah 3: Data Hilang Setelah Pod Dihapus/Restart

**Penyebab:** Anda kemungkinan besar menggunakan tipe volume yang *tidak persisten*, seperti `emptyDir` atau `hostPath` (jika Node dihapus/berubah). Atau, Anda menggunakan PVC dengan `persistentVolumeReclaimPolicy: Delete` dan PVC tersebut ikut terhapus.

**Solusi:**

*   Gunakan **PersistentVolumeClaim** untuk data yang perlu bertahan melewati siklus hidup Pod.
*   Pastikan PV yang digunakan (atau StorageClass yang membuatnya) memiliki `persistentVolumeReclaimPolicy: Retain` jika data tersebut sangat penting dan tidak boleh terhapus secara otomatis saat PVC dihapus.

Troubleshooting storage seringkali melibatkan pemeriksaan Events pada PVC dan Pod, serta log dari Kubelet dan komponen driver storage (CSI) di Node yang relevan. Memahami siklus hidup binding PVC dan kebijakan reclaim juga sangat penting.
