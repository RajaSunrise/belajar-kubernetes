# Langkah 1: Instalasi `kubectl`

`kubectl` (diucapkan "kube control", "kube C T L", atau "kube cuttle") adalah alat baris perintah (Command Line Interface - CLI) utama untuk berinteraksi dengan cluster Kubernetes Anda. Dengan `kubectl`, Anda dapat:

*   Men-deploy aplikasi (membuat Deployments, Pods, dll.).
*   Memeriksa dan mengelola sumber daya cluster (melihat status Pods, Nodes, Services).
*   Melihat log aplikasi.
*   Mengeksekusi perintah di dalam kontainer.
*   Dan masih banyak lagi...

Pada dasarnya, `kubectl` berkomunikasi dengan API Server Kubernetes di Control Plane untuk menjalankan perintah Anda.

**Penting:** Metode instalasi dapat berubah. Selalu rujuk ke **[Dokumentasi Instalasi `kubectl` Resmi](https://kubernetes.io/docs/tasks/tools/install-kubectl/)** untuk instruksi terbaru dan terlengkap sesuai sistem operasi Anda.

Berikut adalah ringkasan metode instalasi umum untuk beberapa sistem operasi (verifikasi selalu dengan dokumentasi resmi):

## Instalasi di Linux

Ada beberapa cara umum:

**1. Unduh Binary Langsung (Direkomendasikan & Universal):**
   Cara ini paling umum dan tidak bergantung pada package manager spesifik distro.

   ```bash
   # 1. Unduh versi stabil terbaru (cek versi terbaru di dokumentasi!)
   # Ganti 'amd64' jika arsitektur Anda berbeda (mis: 'arm64')
   curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"

   # 2. (Opsional tapi direkomendasikan) Validasi checksum
   # Dapatkan file checksum
   curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl.sha256"
   # Validasi (output harus "kubectl: OK")
   echo "$(cat kubectl.sha256)  kubectl" | sha256sum --check

   # 3. Jadikan executable
   sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl

   # 4. Hapus file unduhan (opsional)
   # rm kubectl kubectl.sha256

   # 5. Verifikasi instalasi
   kubectl version --client
   ```

**2. Menggunakan Package Manager Distro:**
   *   **Debian/Ubuntu:**
     ```bash
     sudo apt-get update
     # Mungkin perlu menginstal paket prasyarat
     sudo apt-get install -y apt-transport-https ca-certificates curl
     # Tambahkan Google Cloud public signing key & repo Kubernetes
     # (Ikuti instruksi persis dari dokumentasi K8s resmi untuk langkah ini!)
     # ... langkah menambahkan key dan repo ...
     sudo apt-get update
     sudo apt-get install -y kubectl
     ```
   *   **CentOS/RHEL/Fedora:**
     ```bash
     # Tambahkan repo Kubernetes
     # (Ikuti instruksi persis dari dokumentasi K8s resmi!)
     # ... langkah menambahkan repo ...
     sudo yum install -y kubectl # atau dnf install -y kubectl
     ```

## Instalasi di macOS

**1. Unduh Binary Langsung:**
   Mirip dengan Linux, tetapi path unduhan berbeda.

   ```bash
   # Ganti 'amd64' jika menggunakan Apple Silicon ('arm64')
   ARCH="amd64" # atau "arm64"
   curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/darwin/${ARCH}/kubectl"

   # Validasi checksum (opsional)
   curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/darwin/${ARCH}/kubectl.sha256"
   echo "$(cat kubectl.sha256)  kubectl" | shasum -a 256 --check

   # Jadikan executable
   chmod +x ./kubectl

   # Pindahkan ke direktori dalam PATH Anda
   sudo mv ./kubectl /usr/local/bin/kubectl
   sudo chown root:wheel /usr/local/bin/kubectl # Atur kepemilikan

   # Verifikasi
   kubectl version --client
   ```

**2. Menggunakan Homebrew (Populer):**
   ```bash
   brew install kubectl

   # Verifikasi
   kubectl version --client
   ```

## Instalasi di Windows

**1. Unduh Binary Langsung:**
   ```powershell
   # Unduh versi stabil terbaru (jalankan di PowerShell sebagai Admin jika perlu)
   $kubectlVersion = (Invoke-WebRequest -Uri "https://dl.k8s.io/release/stable.txt").Content.Trim()
   Invoke-WebRequest -Uri "https://dl.k8s.io/release/$kubectlVersion/bin/windows/amd64/kubectl.exe" -OutFile "kubectl.exe"

   # Pindahkan ke direktori dalam PATH Anda
   # Buat direktori jika belum ada (contoh: C:\kubectl)
   # New-Item -Path 'C:\' -Name 'kubectl' -ItemType Directory -Force
   # Move-Item -Path ".\kubectl.exe" -Destination "C:\kubectl\kubectl.exe"

   # Tambahkan direktori ke PATH environment variable Anda (permanen)
   # $currentPath = [Environment]::GetEnvironmentVariable("Path", "Machine") # atau "User"
   # [Environment]::SetEnvironmentVariable("Path", $currentPath + ";C:\kubectl", "Machine") # atau "User"
   # Anda perlu memulai ulang terminal/PowerShell agar perubahan PATH efektif

   # Verifikasi (setelah PATH diperbarui dan terminal direstart)
   kubectl version --client
   ```

**2. Menggunakan Package Manager (Chocolatey/Winget):**
   *   **Chocolatey:**
     ```powershell
     choco install kubernetes-cli
     ```
   *   **Winget:**
     ```powershell
     winget install -e --id Kubernetes.kubectl
     ```

## Verifikasi Instalasi

Setelah instalasi, buka terminal atau command prompt baru dan jalankan:

```bash
kubectl version --client
# atau lebih detail
kubectl version --client --output=yaml
```

Outputnya akan menampilkan versi `kubectl` yang terinstal (Client Version). Pada titik ini, mungkin akan ada pesan error tentang tidak bisa terhubung ke server, itu normal karena kita belum menyiapkan cluster atau mengkonfigurasi koneksi.

**Pastikan `kubectl` ada di PATH Anda agar bisa dijalankan dari direktori mana saja.**

Sekarang Anda memiliki `kubectl`, alat fundamental untuk berkomunikasi dengan Kubernetes! Langkah selanjutnya adalah menyiapkan cluster Kubernetes itu sendiri.
