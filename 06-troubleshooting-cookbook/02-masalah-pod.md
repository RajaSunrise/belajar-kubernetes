
# Troubleshooting Masalah Umum Pod

Pods adalah unit kerja fundamental di Kubernetes, dan masalah pada Pods adalah salah satu hal yang paling sering dihadapi. Memahami berbagai status Pod dan cara mendiagnosis penyebabnya sangat penting.

**Alat Diagnostik Utama:**

1.  `kubectl get pods <nama-pod> -o wide -n <namespace>`: Melihat status, node, IP, dan waktu mulai.
2.  `kubectl describe pod <nama-pod> -n <namespace>`: **Sangat Penting!** Menampilkan detail konfigurasi, kondisi saat ini, dan (terutama) **Events** yang relevan di bagian bawah.
3.  `kubectl logs <nama-pod> [-c <nama-kontainer>] [--previous] -n <namespace>`: Melihat log kontainer (saat ini atau yang sebelumnya crash).
4.  `kubectl events -n <namespace> --sort-by='.lastTimestamp'`: Melihat semua events terbaru di namespace.

Mari kita bahas beberapa status/masalah Pod yang umum:

## 1. Status `Pending`

Pod telah diterima oleh API Server, tetapi belum dapat dijadwalkan ke Node atau salah satu kontainernya belum bisa dibuat.

**Kemungkinan Penyebab & Diagnosa:**

*   **Resource Tidak Cukup (Paling Umum):** Cluster tidak memiliki Node dengan CPU atau Memori yang cukup (sesuai `requests` Pod) untuk menjadwalkan Pod.
    *   **Diagnosa:** `kubectl describe pod <nama-pod>` -> Periksa bagian `Events`. Cari pesan seperti `FailedScheduling ... 0/X nodes are available: X Insufficient cpu/memory.`
    *   **Solusi:** Tambah kapasitas Node, kurangi `requests` Pod (jika terlalu tinggi), atur Pod Priority, atau periksa apakah Pod lain menggunakan terlalu banyak resource. Gunakan `kubectl top node` untuk melihat utilisasi Node.
*   **Node Selector / Affinity / Anti-Affinity Tidak Cocok:** Pod meminta Node dengan label tertentu (`nodeSelector`) atau aturan (anti-)affinity yang tidak dapat dipenuhi oleh Node yang tersedia.
    *   **Diagnosa:** `kubectl describe pod <nama-pod>` -> Periksa `Events` untuk pesan `FailedScheduling ... NodeSelector mismatch`, `didn't match node selector`, atau masalah (anti-)affinity. Periksa `spec.nodeSelector`, `spec.affinity` pada Pod dan label pada Node (`kubectl get nodes --show-labels`).
    *   **Solusi:** Sesuaikan selector/affinity Pod atau label Node.
*   **Taints dan Tolerations:** Pod tidak memiliki `toleration` yang diperlukan untuk dijadwalkan di Node yang memiliki `taint`.
    *   **Diagnosa:** `kubectl describe pod <nama-pod>` -> Periksa `Events` untuk pesan `FailedScheduling ... node(s) had taints that the pod didn't tolerate`. Periksa `spec.tolerations` Pod dan taints pada Node (`kubectl describe node <nama-node> | grep Taints`).
    *   **Solusi:** Tambahkan toleration yang sesuai ke Pod atau hapus taint dari Node (jika sesuai).
*   **PersistentVolumeClaim (PVC) Belum Terikat (Unbound):** Pod mencoba me-mount PVC yang masih dalam status `Pending`.
    *   **Diagnosa:** `kubectl describe pod <nama-pod>` -> Periksa `Events` untuk pesan `FailedScheduling ... persistentvolumeclaim "..." not found` atau terkait binding volume. Periksa status PVC: `kubectl get pvc <nama-pvc> -n <namespace>`. Jika `Pending`, lihat [Troubleshooting Storage](./04-masalah-storage.md).
    *   **Solusi:** Selesaikan masalah PVC (pastikan ada PV yang cocok atau StorageClass berfungsi).
*   **Batas ResourceQuota Terlampaui:** Namespace telah mencapai batas resource (CPU, memori, jumlah Pods) yang ditetapkan oleh ResourceQuota.
    *   **Diagnosa:** `kubectl describe pod <nama-pod>` -> Periksa `Events` untuk pesan terkait kuota (misalnya, `forbidden: exceeded quota`). Periksa ResourceQuota: `kubectl get resourcequota -n <namespace>` dan `kubectl describe resourcequota <nama-quota> -n <namespace>`.
    *   **Solusi:** Hapus resource yang tidak perlu di namespace, minta admin menaikkan kuota, atau sesuaikan request Pod.
*   **Masalah Jaringan CNI (Langka):** Plugin CNI gagal mengalokasikan IP untuk Pod.
    *   **Diagnosa:** Periksa log Kubelet di Node dan log Pod CNI (jika berjalan sebagai DaemonSet).
    *   **Solusi:** Debugging CNI (tergantung plugin yang digunakan).

## 2. Status `ContainerCreating` atau `Waiting`

Kubelet sedang mencoba membuat dan memulai kontainer, tetapi mengalami masalah.

**Kemungkinan Penyebab & Diagnosa:**

*   **Masalah Mounting Volume:** Gagal me-mount ConfigMap, Secret, atau PersistentVolume.
    *   **Diagnosa:** `kubectl describe pod <nama-pod>` -> Periksa `Events` untuk pesan `FailedMount` atau `FailedAttachVolume`. Detail error biasanya disertakan. Contoh: Secret/ConfigMap tidak ditemukan, masalah izin akses PV, masalah driver CSI.
    *   **Solusi:** Pastikan ConfigMap/Secret/PVC ada di namespace yang benar, periksa izin akses PV, periksa log driver CSI/storage provisioner.
*   **Masalah Container Runtime:** Daemon container runtime (Docker, containerd) di Node mengalami masalah saat membuat kontainer.
    *   **Diagnosa:** Periksa log Kubelet (`journalctl -u kubelet`) dan log container runtime (`journalctl -u containerd` atau `journalctl -u docker`) di Node tempat Pod dijadwalkan.
    *   **Solusi:** Restart container runtime, periksa konfigurasi runtime, atau debug masalah Node.
*   **Alokasi Resource Jaringan Gagal:** Plugin CNI gagal menyiapkan network namespace atau mengalokasikan IP.
    *   **Diagnosa:** Seperti di atas, periksa log Kubelet dan CNI.
    *   **Solusi:** Debugging CNI.
*   **Menunggu Init Container:** Jika Pod memiliki Init Containers, Pod akan tetap `Waiting` atau `PodInitializing` sampai *semua* Init Containers berhasil selesai.
    *   **Diagnosa:** `kubectl describe pod <nama-pod>` -> Lihat status Init Containers. `kubectl logs <nama-pod> -c <nama-init-container>` untuk melihat lognya.
    *   **Solusi:** Debug masalah pada Init Container (lihat lognya).

## 3. Status `ImagePullBackOff` atau `ErrImagePull`

Kubelet tidak dapat menarik (pull) image kontainer yang ditentukan dalam spesifikasi Pod.

**Kemungkinan Penyebab & Diagnosa:**

*   **Nama Image atau Tag Salah:** Kesalahan pengetikan pada nama image atau tag tidak ada di registry.
    *   **Diagnosa:** `kubectl describe pod <nama-pod>` -> Periksa field `Image:` kontainer dan `Events` untuk pesan `Failed to pull image ... : rpc error: code = NotFound desc = ... not found`.
    *   **Solusi:** Perbaiki nama image/tag di manifest Pod/Deployment Anda. Pastikan image/tag tersebut ada di registry.
*   **Masalah Koneksi Registry:** Node tidak dapat mencapai container registry (masalah jaringan, DNS, atau firewall).
    *   **Diagnosa:** `kubectl describe pod <nama-pod>` -> `Events` mungkin menunjukkan timeout atau error koneksi. Coba `docker pull <nama-image>:<tag>` atau `crictl pull <nama-image>:<tag>` langsung dari Node (via `minikube ssh` atau SSH biasa) untuk menguji konektivitas.
    *   **Solusi:** Perbaiki masalah jaringan/DNS/firewall antara Node dan registry.
*   **Registry Memerlukan Autentikasi (Image Pribadi):** Image berada di registry pribadi dan Pod tidak memiliki kredensial yang benar.
    *   **Diagnosa:** `kubectl describe pod <nama-pod>` -> `Events` menunjukkan error autentikasi atau `manifest unknown`.
    *   **Solusi:** Buat objek `Secret` tipe `kubernetes.io/dockerconfigjson` dengan kredensial registry Anda. Referensikan Secret ini dalam `spec.imagePullSecrets` pada Pod (atau ServiceAccount default jika ingin berlaku untuk semua Pods di namespace). Pastikan Secret ada di namespace yang sama dengan Pod.
*   **Batas Rate Registry Terlampaui:** Terlalu banyak tarikan dari registry publik seperti Docker Hub dalam waktu singkat.
    *   **Diagnosa:** Error mungkin menyebutkan `TOOMANYREQUESTS` atau sejenisnya.
    *   **Solusi:** Autentikasi ke registry (bahkan untuk image publik dapat meningkatkan batas), gunakan mirror registry lokal, atau optimalkan frekuensi penarikan image.

## 4. Status `CrashLoopBackOff`

Kontainer dimulai, berjalan sebentar, lalu crash (keluar dengan kode error non-zero). Kubelet mencoba me-restartnya sesuai `restartPolicy`, tetapi kontainer terus menerus crash dalam satu putaran (loop).

**Kemungkinan Penyebab & Diagnosa:**

*   **Error Aplikasi Saat Startup:** Kode aplikasi Anda mengalami error fatal segera setelah dimulai.
    *   **Diagnosa:** **Penting:** Periksa log dari *restart sebelumnya*! `kubectl logs --previous <nama-pod> [-c <nama-kontainer>] -n <namespace>`. Log ini seringkali berisi stack trace atau pesan error yang menyebabkan crash. `kubectl describe pod <nama-pod>` juga akan menunjukkan `Exit Code` dari kontainer terakhir yang crash.
    *   **Solusi:** Perbaiki bug di kode aplikasi Anda berdasarkan pesan error log.
*   **Kesalahan Konfigurasi Aplikasi:** Aplikasi tidak dapat memulai karena konfigurasi yang salah (misalnya, file konfigurasi yang di-mount hilang/salah format, variabel environment yang dibutuhkan tidak ada/salah).
    *   **Diagnosa:** Periksa log (`--previous`) untuk pesan error terkait konfigurasi. Verifikasi ConfigMaps/Secrets yang di-mount atau disuntikkan sebagai env vars (`kubectl exec <pod> -- env`, periksa file yang di-mount).
    *   **Solusi:** Perbaiki konfigurasi di ConfigMap/Secret atau definisi Pod.
*   **Masalah Dependensi:** Aplikasi gagal terhubung ke dependensi penting saat startup (misalnya, database, service lain).
    *   **Diagnosa:** Periksa log (`--previous`) untuk error koneksi. Gunakan `kubectl exec` dari Pod yang crash untuk mencoba `ping` atau `curl` ke dependensi. Pastikan Service dependensi berjalan dan dapat dijangkau.
    *   **Solusi:** Pastikan dependensi siap sebelum aplikasi dimulai (gunakan Init Containers atau mekanisme retry di aplikasi), perbaiki masalah jaringan/Service dependensi.
*   **Liveness Probe Salah Konfigurasi:** Liveness probe gagal secara keliru (mungkin terlalu cepat/sensitif atau memeriksa endpoint yang salah) dan menyebabkan Kubelet membunuh dan me-restart kontainer yang sebenarnya sehat.
    *   **Diagnosa:** `kubectl describe pod <nama-pod>` -> Periksa `Events` untuk pesan `Liveness probe failed...`. Periksa konfigurasi `livenessProbe`. Coba jalankan perintah/cek probe secara manual via `kubectl exec`.
    *   **Solusi:** Sesuaikan pengaturan probe (delay, period, timeout, threshold) atau perbaiki endpoint/perintah probe.
*   **Masalah Resource (Kurang Umum Menyebabkan Loop Cepat):** Meskipun OOMKill lebih umum, terkadang kekurangan CPU atau Memori bisa menyebabkan crash jika aplikasi tidak menanganinya dengan baik.
    *   **Diagnosa:** Periksa log (`--previous`), periksa penggunaan resource (`kubectl top pod`), periksa `describe pod` untuk `Exit Code`.
    *   **Solusi:** Tingkatkan `requests`/`limits` atau optimalkan aplikasi.

## 5. Status Error Lainnya (mis: `OOMKilled`, `ContainerCannotRun`, `DeadlineExceeded`)

*   **`OOMKilled` (Reason di `describe pod`):** Kontainer menggunakan memori melebihi `limits.memory`.
    *   **Diagnosa:** `kubectl describe pod <nama-pod>` -> Lihat `Last State` -> `Reason: OOMKilled`. `kubectl top pod` (jika sempat terekam). Profil penggunaan memori aplikasi.
    *   **Solusi:** Tingkatkan `limits.memory` (dan mungkin `requests.memory`), optimalkan penggunaan memori aplikasi (deteksi memory leak).
*   **`ContainerCannotRun` (Reason di `describe pod`):** Container runtime tidak dapat menjalankan kontainer karena error (seringkali terkait error pada entrypoint/command image).
    *   **Diagnosa:** `kubectl describe pod <nama-pod>` -> Periksa `Message` di status kontainer. Periksa Dockerfile atau konfigurasi `command`/`args` di manifest.
    *   **Solusi:** Perbaiki image atau command/args di manifest.
*   **`DeadlineExceeded` (untuk Job):** Job berjalan lebih lama dari `activeDeadlineSeconds` yang ditentukan.
    *   **Diagnosa:** `kubectl describe job <nama-job>`.
    *   **Solusi:** Tingkatkan `activeDeadlineSeconds` atau optimalkan durasi Job.

## 6. Pod Stuck di `Terminating`

Pod diperintahkan untuk berhenti (misalnya saat delete, update, atau node drain), tetapi tidak kunjung hilang.

**Kemungkinan Penyebab & Diagnosa:**

*   **Aplikasi Tidak Menangani SIGTERM:** Proses utama di dalam kontainer tidak merespons sinyal `SIGTERM` yang dikirim oleh Kubelet dan tidak keluar dalam batas waktu `terminationGracePeriodSeconds` (default 30 detik). Kubelet akhirnya mengirim `SIGKILL`.
    *   **Diagnosa:** Amati berapa lama Pod stuck. Coba `kubectl exec` (jika masih bisa) untuk melihat status proses.
    *   **Solusi:** Modifikasi aplikasi untuk menangani `SIGTERM` dan melakukan graceful shutdown. Tingkatkan `terminationGracePeriodSeconds` jika aplikasi memang butuh waktu lebih lama untuk shutdown.
*   **Masalah Finalizer:** Objek Pod memiliki `finalizer` yang mencegah penghapusannya sampai kondisi tertentu terpenuhi (misalnya, volume dilepas, sumber daya eksternal dibersihkan oleh controller). Controller yang bertanggung jawab atas finalizer mungkin bermasalah.
    *   **Diagnosa:** `kubectl get pod <nama-pod> -o yaml` -> Cari field `metadata.finalizers`. Identifikasi controller mana yang menambahkannya. Periksa log controller tersebut.
    *   **Solusi:** Selesaikan masalah pada controller. Sebagai langkah terakhir (hati-hati!), Anda bisa menghapus finalizer secara manual (`kubectl patch pod <nama-pod> -p '{"metadata":{"finalizers":null}}'`), tetapi ini bisa meninggalkan sumber daya terkait (seperti volume) dalam state tidak konsisten.
*   **Masalah Unmount Volume:** Kubelet gagal melepaskan (unmount) volume dari Node (terutama untuk PV).
    *   **Diagnosa:** Periksa log Kubelet di Node untuk error terkait unmount. Periksa status driver CSI atau sistem storage.
    *   **Solusi:** Debugging masalah storage/CSI di Node.
*   **Node Tidak Responsif (`Unknown` state):** Jika Node tempat Pod berjalan menjadi tidak responsif, Control Plane mungkin tidak dapat mengkonfirmasi bahwa Pod telah berhenti.
    *   **Diagnosa:** Periksa status Node (`kubectl get nodes`).
    *   **Solusi:** Selesaikan masalah Node. Jika Node tidak bisa dipulihkan, Anda mungkin perlu menghapus Pod secara paksa (`kubectl delete pod <nama-pod> --grace-period=0 --force`). **Peringatan:** Menghapus paksa Pod dari Node yang tidak responsif, terutama untuk StatefulSet, bisa berbahaya dan menyebabkan potensi pelanggaran stateful (misalnya, dua Pod mencoba mengklaim volume yang sama). Lakukan ini hanya jika Anda memahami risikonya.

Memahami berbagai state Pod dan menggunakan `kubectl describe`, `kubectl logs`, dan `kubectl events` secara efektif adalah kunci untuk mendiagnosis sebagian besar masalah pada level Pod di Kubernetes.
