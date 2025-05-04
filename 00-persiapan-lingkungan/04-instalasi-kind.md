# Langkah 3 (Opsi B): Instalasi dan Penggunaan Kind

Kind (Kubernetes IN Docker) adalah alat untuk menjalankan cluster Kubernetes lokal dengan cepat menggunakan *kontainer Docker* sebagai nodenya. Ini sangat populer untuk pengembangan, pengujian (terutama CI/CD), dan eksperimen multi-node lokal karena kecepatannya dan penggunaan resource yang relatif rendah.

**Bagaimana Kind Bekerja?**

Kind men-deploy setiap node Kubernetes (baik control-plane maupun worker) sebagai sebuah kontainer Docker. Ini menggunakan `kubeadm` di belakang layar untuk menginisialisasi cluster di dalam kontainer-kontainer tersebut.

## Prasyarat

1.  **Docker:** Anda **harus** memiliki Docker terinstal dan berjalan di sistem Anda (Docker Engine di Linux atau Docker Desktop di macOS/Windows). Kind bergantung sepenuhnya pada Docker.
2.  **Sumber Daya Sistem:** Tergantung jumlah node, tetapi umumnya lebih ringan dari Minikube berbasis VM. Setidaknya 2 CPU dan 4GB RAM direkomendasikan untuk memulai.

## Langkah 1: Instalasi Kind

Selalu periksa **[Dokumentasi Instalasi Kind Resmi](https://kind.sigs.k8s.io/docs/user/quick-start/#installation)** untuk metode terbaru.

*   **Via GO (jika Go terinstal):**
    ```bash
    go install sigs.k8s.io/kind@v0.20.0 # Ganti v0.20.0 dengan versi terbaru
    # Pastikan direktori $GOPATH/bin ada di PATH Anda
    ```
*   **Unduh Binary (Direkomendasikan untuk banyak pengguna):**
    *   **Linux:**
      ```bash
      # Ganti amd64 dengan arm64 jika perlu
      curl -Lo ./kind https://kind.sigs.k8s.io/dl/v0.20.0/kind-linux-amd64
      chmod +x ./kind
      sudo mv ./kind /usr/local/bin/kind
      ```
    *   **macOS:**
      ```bash
      # Ganti amd64 dengan arm64 jika perlu
      curl -Lo ./kind https://kind.sigs.k8s.io/dl/v0.20.0/kind-darwin-amd64
      chmod +x ./kind
      sudo mv ./kind /usr/local/bin/kind
      ```
    *   **Windows (PowerShell):**
      ```powershell
      curl.exe -Lo kind-windows-amd64.exe https://kind.sigs.k8s.io/dl/v0.20.0/kind-windows-amd64
      Move-Item .\kind-windows-amd64.exe c:\some-dir-in-your-PATH\kind.exe
      ```

**Verifikasi Instalasi Kind:**
```bash
kind version
```

## Langkah 2: Membuat Cluster Kind

Membuat cluster node tunggal (1 control-plane) sangat mudah:

```bash
# Membuat cluster dengan nama default 'kind'
kind create cluster

# Membuat cluster dengan nama spesifik
kind create cluster --name belajar-k8s
```

Proses `create cluster` akan:
1.  Menarik image node Kind yang diperlukan (berisi komponen K8s).
2.  Membuat kontainer Docker untuk node control-plane.
3.  Menggunakan `kubeadm` di dalam kontainer untuk bootstrap cluster.
4.  Menulis konfigurasi `kubectl` ke file `~/.kube/config` dan mengatur konteks baru (mis: `kind-belajar-k8s`).

Startup biasanya sangat cepat (seringkali kurang dari satu menit).

## Langkah 3: Berinteraksi dengan Cluster

Setelah cluster dibuat, `kubectl` Anda akan otomatis dikonfigurasi untuk menunjuk ke cluster Kind tersebut.

```bash
# Periksa konteks kubectl saat ini
kubectl config current-context
# Output: kind-belajar-k8s (atau nama cluster Anda)

# Lihat node (akan ada satu node control-plane)
kubectl get nodes

# Lihat pods sistem
kubectl get pods -n kube-system
```

## Fitur Kind yang Berguna

*   **Menentukan Versi Kubernetes:** Gunakan flag `--image` untuk menentukan image node Kind yang berisi versi K8s spesifik. Cari tag image di [Kind Releases](https://github.com/kubernetes-sigs/kind/releases).
    ```bash
    kind create cluster --name k8s-1-26 --image kindest/node:v1.26.3
    ```
*   **Membuat Cluster Multi-node:** Gunakan file konfigurasi YAML.
    Buat file `kind-multinode-config.yaml`:
    ```yaml
    # kind-multinode-config.yaml
    kind: Cluster
    apiVersion: kind.x-k8s.io/v1alpha4 # Gunakan versi API terbaru dari docs Kind
    nodes:
    - role: control-plane # Node control plane (bisa lebih dari satu untuk HA)
    - role: worker        # Node worker pertama
    - role: worker        # Node worker kedua
    ```
    Buat cluster menggunakan file konfigurasi:
    ```bash
    kind create cluster --name multi-node --config kind-multinode-config.yaml
    # Verifikasi node setelah selesai: kubectl get nodes
    ```
*   **Melihat Daftar Cluster Kind:**
    ```bash
    kind get clusters
    ```
*   **Menghapus Cluster:**
    ```bash
    # Hapus cluster default ('kind')
    kind delete cluster

    # Hapus cluster dengan nama spesifik
    kind delete cluster --name belajar-k8s
    ```
    Penghapusan juga sangat cepat karena hanya perlu menghentikan dan menghapus kontainer Docker.
*   **Memuat Image Docker Lokal ke Cluster:** Ini sangat berguna agar cluster Kind dapat menggunakan image yang baru Anda bangun secara lokal tanpa perlu mendorongnya ke registry.
    ```bash
    # Bangun image Docker Anda secara lokal
    docker build -t my-local-app:v1 .

    # Muat image ke cluster Kind Anda
    kind load docker-image my-local-app:v1 --name belajar-k8s # Sesuaikan nama cluster
    # Sekarang Anda bisa menggunakan 'my-local-app:v1' di manifest K8s Anda
    ```
*   **Mendapatkan Kubeconfig:** Jika Anda perlu menggunakan kubeconfig di tempat lain atau jika tidak otomatis terkonfigurasi.
    ```bash
    kind export kubeconfig --name belajar-k8s
    # Ini akan mencetak kubeconfig ke stdout. Anda bisa mengarahkannya ke file
    # atau mengatur variabel environment KUBECONFIG.
    ```

Kind adalah pilihan fantastis untuk lingkungan pengembangan Kubernetes lokal yang cepat, ringan, dan fleksibel, terutama jika Anda membutuhkan kemampuan multi-node atau integrasi CI/CD.
