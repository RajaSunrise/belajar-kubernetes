# Langkah 3 (Opsi A): Instalasi dan Penggunaan Minikube

Minikube adalah alat yang populer dan mapan untuk menjalankan cluster Kubernetes *node tunggal* secara lokal di mesin Anda. Ini sangat bagus untuk belajar, pengembangan, dan pengujian sehari-hari.

**Bagaimana Minikube Bekerja?**

Minikube membuat sebuah lingkungan (biasanya VM atau kontainer Docker) di mesin Anda dan kemudian menginstal serta mengkonfigurasi semua komponen Kubernetes (API Server, Scheduler, etcd, Kubelet, dll.) di dalam lingkungan tersebut.

## Prasyarat

1.  **Sumber Daya Sistem:** Minimal 2 CPU core, 2GB RAM (disarankan 4GB+), dan 20GB ruang disk kosong.
2.  **Koneksi Internet:** Untuk mengunduh Minikube, image Kubernetes, dan image kontainer.
3.  **Container atau Virtual Machine Manager (Driver):** Minikube memerlukan *driver* untuk membuat lingkungan K8s. Pilihan umum:
    *   **Docker (Direkomendasikan jika sudah terinstal):** Menggunakan Docker Desktop atau Docker Engine di Linux. Biasanya lebih cepat dan ringan daripada VM.
    *   **VirtualBox:** Hypervisor lintas platform gratis (perlu diinstal terpisah).
    *   **Hyper-V:** Hypervisor bawaan Windows 10 Pro/Enterprise/Education.
    *   **KVM:** Hypervisor bawaan Linux.
    *   **VMware Fusion/Workstation:** Hypervisor komersial (perlu lisensi).
    *   **Podman:** Alternatif Docker (dukungan mungkin bervariasi).
    *   Lihat [Dokumentasi Driver Minikube](https://minikube.sigs.k8s.io/docs/drivers/) untuk daftar lengkap.

## Langkah 1: Instalasi Minikube

Metode instalasi bervariasi. Selalu periksa **[Halaman Rilis Minikube Resmi](https://minikube.sigs.k8s.io/docs/start/)** untuk instruksi terbaru.

*   **macOS (via Homebrew):**
    ```bash
    brew install minikube
    ```
*   **Linux (Unduh Binary):**
    ```bash
    curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
    sudo install minikube-linux-amd64 /usr/local/bin/minikube
    rm minikube-linux-amd64 # Opsional
    ```
*   **Windows (Unduh Binary atau via Package Manager):**
    *   Unduh `minikube-windows-amd64.exe` dari halaman rilis, ganti nama menjadi `minikube.exe`, dan tambahkan ke PATH Anda.
    *   **Chocolatey:** `choco install minikube`
    *   **Winget:** `winget install minikube`

**Verifikasi Instalasi Minikube:**
```bash
minikube version
```

## Langkah 2: Memulai Cluster Minikube

Perintah dasarnya adalah `minikube start`. Anda bisa menambahkan flag untuk menyesuaikan cluster:

```bash
# Memulai cluster dengan driver default (Minikube akan mencoba mendeteksi)
# minikube start

# Memulai dengan driver spesifik (contoh: Docker)
minikube start --driver=docker

# Memulai dengan alokasi resource spesifik
minikube start --driver=docker --cpus=4 --memory=8192mb # 4 CPU, 8GB RAM

# Memulai dengan versi Kubernetes spesifik
# minikube start --kubernetes-version=v1.26.3

# Memulai dengan dukungan multi-node (eksperimental)
# minikube start --nodes 3 -p my-multinode-cluster
```

Proses `start` akan:
1.  Mengunduh image/komponen yang diperlukan.
2.  Membuat VM atau kontainer sesuai driver yang dipilih.
3.  Menyediakan dan memulai komponen Kubernetes di dalamnya.
4.  Mengkonfigurasi `kubectl` Anda (biasanya otomatis) untuk menunjuk ke cluster Minikube yang baru dibuat.

Proses ini mungkin memakan waktu beberapa menit saat pertama kali dijalankan.

## Langkah 3: Berinteraksi dengan Cluster

Setelah `minikube start` selesai, `kubectl` Anda seharusnya sudah dikonfigurasi. Anda bisa langsung menggunakan perintah `kubectl`:

```bash
# Periksa apakah kubectl menunjuk ke konteks minikube
kubectl config current-context
# Output: minikube (atau nama profil jika Anda menggunakan -p)

# Lihat node cluster (akan ada satu node bernama 'minikube')
kubectl get nodes

# Lihat pods di namespace kube-system (komponen internal)
kubectl get pods -n kube-system
```

## Perintah Minikube Berguna Lainnya

*   **Melihat Status Cluster:**
    ```bash
    minikube status
    ```
*   **Mengakses Service (Penting untuk Web Apps):** Minikube menyediakan cara mudah untuk mendapatkan URL service tipe `NodePort` atau `LoadBalancer`.
    ```bash
    # Jika Anda punya Service bernama 'my-web-service'
    minikube service my-web-service
    # Ini akan membuka URL Service di browser Anda atau mencetak URL-nya.

    # Mendapatkan URL tanpa membuka browser
    minikube service my-web-service --url
    ```
*   **Mengakses Dashboard Kubernetes:**
    ```bash
    minikube dashboard
    # Ini akan membuka Dashboard web K8s di browser Anda.
    ```
*   **Mengelola Addons:** Minikube punya banyak addons (seperti ingress, metrics-server) yang mudah diaktifkan/dinonaktifkan.
    ```bash
    minikube addons list # Lihat addons yang tersedia & statusnya
    minikube addons enable ingress # Aktifkan addon ingress
    minikube addons disable metrics-server # Nonaktifkan addon metrics-server
    ```
*   **SSH ke dalam Node Minikube:** Untuk debugging tingkat lanjut.
    ```bash
    minikube ssh
    ```
*   **Melihat Log Minikube:**
    ```bash
    minikube logs
    ```
*   **Menghentikan Cluster (Menyimpan State):**
    ```bash
    minikube stop
    # VM/kontainer dihentikan, tapi state disimpan. Start berikutnya lebih cepat.
    ```
*   **Menghapus Cluster (Menghapus Semua Data):**
    ```bash
    minikube delete
    # Ini akan menghapus VM/kontainer dan semua data di dalamnya.
    # Gunakan ini jika ingin memulai dari awal atau membersihkan resource.

    # Menghapus profil cluster spesifik (jika menggunakan -p)
    # minikube delete -p my-multinode-cluster
    ```
*   **Mengkonfigurasi Default (CPU, Memori, dll.):**
    ```bash
    minikube config set memory 6144 # Set memori default ke 6GB
    minikube config set cpus 4      # Set CPU default ke 4
    ```

Minikube adalah cara yang andal dan fleksibel untuk memulai perjalanan Kubernetes Anda di lingkungan lokal. Jangan ragu untuk menjelajahi berbagai perintah dan addon-nya.
