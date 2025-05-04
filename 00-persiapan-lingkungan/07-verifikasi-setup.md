# Langkah 4: Verifikasi Setup Lingkungan Kubernetes Anda

Setelah Anda menginstal `kubectl` dan memilih serta memulai salah satu lingkungan Kubernetes lokal (Minikube, Kind, K3s, Docker Desktop, dll.), langkah terakhir sebelum mulai men-deploy aplikasi adalah **memverifikasi** bahwa semuanya terkonfigurasi dengan benar dan cluster Anda dalam keadaan sehat.

Verifikasi ini memastikan bahwa `kubectl` dapat berkomunikasi dengan API Server cluster yang benar dan bahwa komponen inti cluster berjalan sebagaimana mestinya.

## Perintah Verifikasi Kunci

Jalankan perintah-perintah berikut di terminal atau command prompt Anda:

**1. Periksa Konteks `kubectl` Saat Ini:**
   Pastikan `kubectl` menunjuk ke cluster lokal yang baru saja Anda siapkan.

   ```bash
   kubectl config current-context
   ```
   Outputnya harus sesuai dengan lingkungan yang Anda pilih (misalnya, `minikube`, `kind-belajar-k8s`, `k3s`, `docker-desktop`). Jika tidak, gunakan `kubectl config use-context <nama-konteks-yang-benar>` untuk beralih. Lihat [Langkah 5: Konfigurasi kubectl](./08-konfigurasi-kubectl.md) untuk detail lebih lanjut tentang konteks.

**2. Dapatkan Informasi Cluster Dasar:**
   Perintah ini menghubungi API Server dan menampilkan URL endpoint utama.

   ```bash
   kubectl cluster-info
   ```
   Outputnya akan terlihat seperti:
   ```
   Kubernetes control plane is running at https://127.0.0.1:54387
   CoreDNS is running at https://127.0.0.1:54387/api/v1/namespaces/kube-system/services/kube-dns:dns/proxy
   Metrics-server is running at https://127.0.0.1:54387/api/v1/namespaces/kube-system/services/https:metrics-server:/proxy

   To further debug and diagnose cluster problems, use 'kubectl cluster-info dump'.
   ```
   (URL dan port akan bervariasi). Jika perintah ini gagal, berarti `kubectl` tidak dapat menghubungi API Server cluster Anda. Periksa kembali status cluster lokal Anda (mis: `minikube status`, `docker ps` untuk Kind, `sudo systemctl status k3s`).

**3. Periksa Versi Client dan Server:**
   Verifikasi versi `kubectl` (Client) dan versi Kubernetes API Server (Server).

   ```bash
   kubectl version
   # Atau untuk output lebih detail:
   kubectl version --output=yaml
   ```
   Outputnya akan mencantumkan `Client Version` dan `Server Version`. Idealnya, versi client dan server tidak terlalu jauh berbeda (misalnya, berbeda satu atau dua versi minor). Perbedaan versi yang signifikan (version skew) terkadang dapat menyebabkan masalah kompatibilitas.

**4. Periksa Status Node (Sangat Penting):**
   Ini adalah salah satu pemeriksaan terpenting. Ini menunjukkan apakah mesin (virtual atau kontainer) yang menjalankan komponen Kubernetes (Worker Nodes dan/atau Control Plane) sudah siap.

   ```bash
   kubectl get nodes
   # Atau untuk informasi lebih detail (IP, OS, Runtime):
   kubectl get nodes -o wide
   ```
   Outputnya akan menampilkan daftar node dalam cluster Anda. Untuk lingkungan lokal node tunggal, Anda akan melihat satu node.
   ```
   NAME             STATUS   ROLES           AGE   VERSION
   docker-desktop   Ready    control-plane   15m   v1.27.2
   ```
   Perhatikan kolom `STATUS`. Status `Ready` menunjukkan bahwa node tersebut sehat dan siap menerima penjadwalan Pods. Status lain seperti `NotReady` atau `Unknown` mengindikasikan masalah pada node tersebut. Kolom `ROLES` menunjukkan peran node (misalnya, `control-plane`, `worker`, atau `<none>`).

**5. Lihat Namespace yang Ada:**
   Namespace adalah cara untuk mempartisi cluster. Perintah ini menunjukkan namespace dasar yang biasanya ada.

   ```bash
   kubectl get namespaces
   # Atau 'kubectl get ns'
   ```
   Outputnya akan mencakup setidaknya:
   ```
   NAME              STATUS   AGE
   default           Active   20m  # Namespace default untuk objek Anda
   kube-node-lease   Active   20m  # Untuk mekanisme lease node
   kube-public       Active   20m  # Dapat dibaca publik (jarang digunakan)
   kube-system       Active   20m  # Tempat komponen sistem K8s berjalan
   ```
   Melihat namespace ini adalah tanda lain bahwa cluster dasar berfungsi.

**6. Periksa Pods Sistem:**
   Banyak komponen inti Kubernetes berjalan sebagai Pods di namespace `kube-system`. Memeriksa statusnya dapat memberikan indikasi kesehatan cluster.

   ```bash
   kubectl get pods --namespace kube-system
   # Atau disingkat:
   kubectl get pods -n kube-system
   # Atau lihat SEMUA pods di SEMUA namespace:
   kubectl get pods -A # atau kubectl get pods --all-namespaces
   ```
   Anda akan melihat daftar Pods seperti `coredns-xxxxx`, `etcd-xxxxx`, `kube-apiserver-xxxxx`, `kube-controller-manager-xxxxx`, `kube-proxy-xxxxx`, `kube-scheduler-xxxxx` (nama dan jumlahnya akan bervariasi tergantung distribusi K8s Anda). Idealnya, semua Pods ini harus dalam status `Running` dan `READY` (misalnya, `1/1`). Jika ada yang `Pending`, `CrashLoopBackOff`, atau `Error`, itu mungkin menunjukkan masalah konfigurasi atau resource.

## Troubleshooting Jika Verifikasi Gagal

*   **`kubectl config current-context` salah:** Gunakan `kubectl config get-contexts` dan `kubectl config use-context <nama-konteks>` untuk beralih ke konteks yang benar.
*   **`kubectl cluster-info` atau `kubectl version` gagal terhubung ke server:** Pastikan cluster lokal Anda benar-benar berjalan (periksa status Minikube, Kind, K3s, Docker Desktop). Periksa apakah ada firewall yang memblokir koneksi.
*   **`kubectl get nodes` menunjukkan `NotReady`:** Ini bisa disebabkan oleh banyak hal. Periksa log Kubelet di node tersebut (`minikube ssh` lalu cari log Kubelet, atau `journalctl -u k3s` untuk K3s). Bisa jadi masalah jaringan CNI, masalah resource, atau komponen Kubelet itu sendiri.
*   **Pods di `kube-system` tidak `Running`:** Gunakan `kubectl describe pod <nama-pod> -n kube-system` untuk melihat Events dan detail status Pod tersebut. Gunakan `kubectl logs <nama-pod> -n kube-system` untuk melihat log kontainer di dalam Pod tersebut.

Jika semua perintah verifikasi di atas berjalan tanpa error dan menunjukkan status `Ready` atau `Running` di mana diharapkan, maka lingkungan Kubernetes lokal Anda sudah siap untuk digunakan! Anda bisa mulai men-deploy aplikasi pertama Anda.
