# Langkah 3 (Opsi C): Instalasi dan Penggunaan K3s

K3s adalah distribusi Kubernetes resmi bersertifikasi CNCF yang dirancang oleh Rancher (sekarang bagian dari SUSE) agar menjadi **sangat ringan**, mudah diinstal, dan cocok untuk lingkungan dengan sumber daya terbatas seperti Edge, IoT, CI, dan development.

**Fitur Utama K3s:**

*   **Ringan:** Dikemas dalam binary tunggal kurang dari 100MB. Kebutuhan RAM rendah (mulai dari 512MB).
*   **Mudah Diinstal:** Skrip instalasi sederhana (`curl | sh`).
*   **Aman Secara Default:** Konfigurasi default yang lebih ketat.
*   **Menggunakan containerd:** Menggunakan containerd sebagai container runtime default (bukan Docker).
*   **Alternatif Komponen:** Menggunakan SQLite sebagai datastore default (lebih ringan dari etcd, tapi etcd bisa dikonfigurasi), Flannel untuk CNI, CoreDNS, Traefik Ingress Controller bawaan (opsional).
*   **Menghapus Fitur Non-Inti:** Menghilangkan driver cloud non-default, storage driver alpha, dll., untuk memperkecil ukuran.

## Prasyarat

*   **Sistem Operasi Linux:** K3s utamanya menargetkan Linux (x86_64, ARM64, ARMv7).
*   **Sumber Daya:** Minimal 512MB RAM (disarankan 1GB+), 1 CPU core.
*   **Koneksi Internet:** Untuk mengunduh binary K3s.
*   **Akses `root` atau `sudo`:** Diperlukan untuk instalasi.

## Langkah 1: Instalasi K3s (Server/Node Tunggal)

Metode paling umum adalah menggunakan skrip instalasi resmi. Buka terminal di mesin Linux Anda.

```bash
# Unduh dan jalankan skrip instalasi (akan menginstal K3s sebagai service systemd/openrc)
# Jalankan sebagai root atau menggunakan sudo
curl -sfL https://get.k3s.io | sh -

# Skrip ini akan:
# 1. Mendeteksi arsitektur dan OS Anda.
# 2. Mengunduh binary K3s yang sesuai.
# 3. Mengatur K3s untuk berjalan sebagai service (misalnya, /etc/systemd/system/k3s.service).
# 4. Memulai service K3s.
```

Instalasi biasanya sangat cepat.

**Opsi Instalasi Tambahan (Flags):**
Anda bisa menambahkan opsi ke perintah `sh` untuk mengkustomisasi instalasi, misalnya:
*   `INSTALL_K3S_EXEC="server --disable traefik"`: Menginstal server K3s tanpa Traefik Ingress Controller bawaan.
*   `INSTALL_K3S_EXEC="agent --server https://<IP_SERVER_K3S>:6443 --token <TOKEN_NODE>"`: Menginstal sebagai agent/worker node yang terhubung ke server K3s yang sudah ada.

Lihat **[Dokumentasi Opsi Instalasi K3s](https://rancher.com/docs/k3s/latest/en/installation/install-options/)** untuk detail lengkap.

## Langkah 2: Mengkonfigurasi Akses `kubectl`

Secara default, K3s membuat file kubeconfig di `/etc/rancher/k3s/k3s.yaml`. File ini hanya bisa dibaca oleh `root`. Agar `kubectl` Anda (yang biasanya dijalankan sebagai user biasa) dapat mengakses cluster K3s, Anda perlu melakukan salah satu langkah berikut:

**Opsi A: Salin Konfigurasi ke Lokasi Default `kubectl` (Umum)**

```bash
# Pastikan direktori .kube ada
mkdir -p ~/.kube

# Salin file kubeconfig K3s ke lokasi default kubectl dan atur izinnya
sudo cp /etc/rancher/k3s/k3s.yaml ~/.kube/config
sudo chown $(id -u):$(id -g) ~/.kube/config # Berikan kepemilikan ke user Anda saat ini

# Sekarang kubectl akan otomatis menggunakan konfigurasi ini
kubectl get nodes
```

**Opsi B: Gunakan Variabel Environment `KUBECONFIG`**

```bash
# Set variabel environment untuk sesi terminal saat ini
export KUBECONFIG=/etc/rancher/k3s/k3s.yaml

# Anda mungkin perlu sudo untuk membaca file jika belum menyalinnya
sudo kubectl get nodes

# Agar permanen, tambahkan 'export KUBECONFIG=...' ke file profil shell Anda (~/.bashrc, ~/.zshrc, dll.)
# dan pastikan user Anda punya izin baca ke file tersebut.
```

**Opsi C: Gunakan `kubectl` Bawaan K3s (Kurang Umum untuk Akses Eksternal)**
K3s juga menyertakan `kubectl`.
```bash
sudo k3s kubectl get nodes
```

## Langkah 3: Verifikasi Cluster K3s

Setelah `kubectl` terkonfigurasi, verifikasi cluster:

```bash
# Periksa konteks (biasanya 'default')
kubectl config current-context

# Lihat node (akan ada satu node, nama host mesin Anda)
kubectl get nodes -o wide

# Lihat pods sistem (di namespace kube-system dan lainnya)
kubectl get pods -A # -A adalah singkatan dari --all-namespaces
```

Anda akan melihat pod-pod inti K3s seperti CoreDNS, Klipper Load Balancer (service load balancer), Local Path Provisioner (storage), dll. Jika Anda tidak menonaktifkannya, Anda juga akan melihat pod Traefik.

## Perintah K3s Berguna Lainnya

*   **Memeriksa Status Service K3s:**
    ```bash
    # Jika menggunakan systemd
    sudo systemctl status k3s

    # Memulai/Menghentikan/Me-restart service
    sudo systemctl start k3s
    sudo systemctl stop k3s
    sudo systemctl restart k3s
    ```
*   **Melihat Log K3s:**
    ```bash
    sudo journalctl -u k3s -f # Ikuti log (jika systemd)
    ```
*   **Menambahkan Worker Node (Agent):**
    1.  Dapatkan token join dari server K3s:
        ```bash
        sudo cat /var/lib/rancher/k3s/server/node-token
        ```
    2.  Di mesin worker node, jalankan skrip instalasi dengan flag agent:
        ```bash
        # Ganti <IP_SERVER_K3S> dan <TOKEN_NODE>
        curl -sfL https://get.k3s.io | K3S_URL=https://<IP_SERVER_K3S>:6443 K3S_TOKEN=<TOKEN_NODE> sh -
        ```
*   **Uninstal K3s:**
    K3s menyediakan skrip untuk membersihkan instalasi.
    ```bash
    # Di Server Node
    sudo /usr/local/bin/k3s-uninstall.sh

    # Di Agent Node
    sudo /usr/local/bin/k3s-agent-uninstall.sh
    ```

K3s adalah pilihan yang sangat baik jika Anda menginginkan pengalaman Kubernetes yang ringan, cepat, dan mudah diinstal, terutama untuk development atau lingkungan dengan keterbatasan sumber daya.
