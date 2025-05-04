# Lab 04: Mengekspos Aplikasi ke Dunia Luar dengan Ingress

**Tujuan:** Lab ini menunjukkan cara menggunakan objek `Ingress` dan sebuah `Ingress Controller` untuk mengekspos aplikasi HTTP/S yang berjalan di dalam cluster (seperti yang kita buat di Lab 01) ke lalu lintas eksternal. Kita akan mencoba routing berbasis path dan mengkonfigurasi TLS (HTTPS).

**Konsep yang Dipelajari:**

*   Peran Ingress sebagai aturan routing L7.
*   Peran Ingress Controller sebagai implementasi aturan (reverse proxy).
*   Membuat objek `Ingress` sederhana untuk routing berbasis path.
*   Menguji akses melalui Ingress Controller.
*   Membuat Secret TLS untuk sertifikat HTTPS.
*   Mengkonfigurasi Ingress untuk terminasi TLS.
*   Memahami `ingressClassName`.

**Prasyarat:**

*   Cluster Kubernetes lokal berjalan.
*   `kubectl` terinstal dan terkonfigurasi.
*   **Aplikasi dan Service dari Lab 01 berjalan:** Pastikan Deployment `hello-k8s-deployment` dan Service `hello-k8s-service` dari Lab 01 sudah berjalan di namespace `lab01-stateless` (atau namespace pilihan Anda). Jika belum, jalankan langkah-langkah dari Lab 01 untuk men-deploynya.
*   **PENTING: Ingress Controller Terinstal dan Berjalan:** Ingress hanya berfungsi jika ada Ingress Controller yang aktif di cluster Anda. Metode instalasi bervariasi:
    *   **Minikube:** `minikube addons enable ingress` (Menginstal Nginx Ingress Controller).
    *   **Kind:** Perlu diinstal manual. Cara umum pakai Helm untuk Nginx Ingress:
        ```bash
        helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
        helm repo update
        helm install nginx-ingress ingress-nginx/ingress-nginx \
          --namespace ingress-nginx --create-namespace \
          --set controller.service.type=NodePort \
          --set controller.service.nodePorts.http=30080 \
          --set controller.service.nodePorts.https=30443
        # (Port 30080/30443 adalah contoh, bisa diganti)
        ```
    *   **K3s:** Biasanya sudah menyertakan Traefik Ingress Controller secara default (kecuali dinonaktifkan saat instalasi).
    *   **Docker Desktop:** Menggunakan Nginx Ingress Controller bawaan saat K8s diaktifkan.
    *   **Verifikasi Ingress Controller:** Periksa apakah Pods Ingress Controller berjalan (seringkali di namespace `ingress-nginx`, `kube-system`, atau `traefik`) dan apakah ada Service (biasanya LoadBalancer atau NodePort) untuk controller tersebut. `kubectl get pods,svc -n <ingress-controller-namespace>`
*   `openssl` terinstal (untuk membuat sertifikat self-signed).

## Langkah 1: Siapkan Namespace dan Aplikasi

Pastikan Anda berada di namespace tempat aplikasi Lab 01 berjalan.

```bash
# Jika belum, set namespace dari Lab 01
kubectl config set-context --current --namespace=lab01-stateless

# Verifikasi aplikasi dan service berjalan
kubectl get deployment hello-k8s-deployment
kubectl get service hello-k8s-service
kubectl get pods -l app=hello-k8s
```

## Langkah 2: Membuat Ingress Sederhana (HTTP)

Kita akan membuat aturan Ingress yang mengarahkan semua traffic untuk path `/` ke service `hello-k8s-service`.

Buat file `ingress.yaml`:

```yaml
# ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: hello-k8s-ingress
  annotations:
    # Anotasi mungkin diperlukan tergantung Ingress Controller Anda
    # Contoh untuk Nginx Ingress jika path bukan root:
    # nginx.ingress.kubernetes.io/rewrite-target: /
spec:
  # Penting: Sesuaikan dengan Ingress Class yang tersedia di cluster Anda
  # Gunakan 'kubectl get ingressclass' untuk melihat yang tersedia
  # Jika menggunakan Nginx Ingress dari Helm/Minikube addon, biasanya 'nginx'
  # Jika K3s/Traefik default, mungkin tidak perlu (cek dokumentasi Traefik CRD)
  # Jika Docker Desktop, 'nginx'
  ingressClassName: nginx # GANTI JIKA PERLU
  rules:
  # Tidak ada host spesifik, akan cocok untuk semua host (atau IP Ingress Controller)
  - http:
      paths:
      - path: / # Cocokkan path root
        pathType: Prefix # Tipe pencocokan (Prefix atau Exact)
        backend:
          service:
            name: hello-k8s-service # Nama Service target
            port:
              number: 80 # Port Service target (port 80 di Service kita)
```

**Penting:** Sesuaikan `ingressClassName`! Jika Anda tidak yakin, coba jalankan `kubectl get ingressclass`. Jika tidak ada output atau Anda menggunakan Traefik K3s model lama, Anda mungkin perlu menghapus baris `ingressClassName` atau merujuk ke dokumentasi controller spesifik Anda.

**Terapkan manifest:**

```bash
kubectl apply -f ingress.yaml
```

**Verifikasi Ingress:**

```bash
kubectl get ingress hello-k8s-ingress
# OUTPUT (Contoh Nginx Ingress):
# NAME                CLASS   HOSTS   ADDRESS        PORTS   AGE
# hello-k8s-ingress   nginx   *       192.168.49.2   80      15s
# (ADDRESS akan berupa IP Node Minikube, IP LoadBalancer, atau kosong sementara)

kubectl describe ingress hello-k8s-ingress # Lihat detail dan event
```

## Langkah 3: Mengakses Aplikasi via Ingress (HTTP)

Untuk mengaksesnya, Anda perlu mengetahui **alamat IP eksternal** atau **NodePort** dari Ingress Controller Anda.

*   **Minikube:** `minikube ip` (dapatkan IP node) atau `minikube service list` (cari service ingress).
*   **Kind (dengan Helm Nginx Ingress NodePort):** Gunakan IP Node Docker (`docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' <nama-kontainer-control-plane>`) dan NodePort yang Anda set (misal, 30080 untuk HTTP). Alamatnya: `http://<IP_Node_Docker>:30080`
*   **Docker Desktop:** Biasanya `localhost`.
*   **K3s (Traefik):** Biasanya menggunakan port 80/443 di IP Node.
*   **Cloud (LoadBalancer):** `kubectl get service -n <ingress-namespace> <nama-service-ingress-controller>` dan lihat `EXTERNAL-IP`.

Mari kita asumsikan IP/Host Ingress Controller Anda adalah `<INGRESS_ADDRESS>`.

```bash
# Coba akses langsung path root
curl http://<INGRESS_ADDRESS>/

# Jika Anda mendefinisikan 'host' di Ingress (misal: hello.example.com):
# 1. Tambahkan entri ke file /etc/hosts lokal Anda (perlu admin/sudo):
#    <INGRESS_ADDRESS> hello.example.com
# 2. Akses menggunakan host:
#    curl http://hello.example.com/
# ATAU gunakan header Host dengan curl:
# curl -H "Host: hello.example.com" http://<INGRESS_ADDRESS>/
```

Anda seharusnya mendapatkan output HTML "Hello Kubernetes!" dari aplikasi Anda.

## Langkah 4: Menyiapkan TLS (HTTPS)

Untuk mengaktifkan HTTPS, kita perlu:
1.  Sertifikat TLS (private key dan public certificate). Untuk demo, kita buat self-signed.
2.  Secret Kubernetes tipe `kubernetes.io/tls` yang menyimpan key dan cert.
3.  Memperbarui Ingress untuk menggunakan Secret TLS.

**1. Buat Sertifikat Self-Signed (gunakan `openssl`)**
   Ganti `hello-k8s.local` dengan host yang ingin Anda gunakan (harus cocok dengan `host` di Ingress).

   ```bash
   # Buat private key
   openssl genrsa -out tls.key 2048

   # Buat Certificate Signing Request (CSR)
   # Isi informasi yang diminta (Common Name PENTING, isi dgn host Anda: hello-k8s.local)
   openssl req -new -key tls.key -out tls.csr -subj "/CN=hello-k8s.local/O=Lab Inc."

   # Buat Sertifikat Self-Signed (valid 365 hari)
   openssl x509 -req -days 365 -in tls.csr -signkey tls.key -out tls.crt

   # (Opsional) Periksa sertifikat
   # openssl x509 -in tls.crt -text -noout
   ```
   Sekarang Anda memiliki `tls.key` (kunci privat) dan `tls.crt` (sertifikat publik).

**2. Buat Secret TLS**
   Buat file `tls-secret.yaml` (atau langsung gunakan kubectl).

   ```yaml
   # tls-secret.yaml (Alternatif: gunakan kubectl create secret tls)
   apiVersion: v1
   kind: Secret
   metadata:
     name: hello-k8s-tls-secret # Nama Secret yang akan dirujuk Ingress
   type: kubernetes.io/tls # Tipe HARUS ini
   data:
     # Nilai harus base64 encoded
     tls.crt: $(cat tls.crt | base64 | tr -d '\n') # Baca & encode cert
     tls.key: $(cat tls.key | base64 | tr -d '\n') # Baca & encode key
   ```
   **Cara Lebih Mudah dengan `kubectl`:**
   ```bash
   kubectl create secret tls hello-k8s-tls-secret --cert=tls.crt --key=tls.key
   ```

   **Verifikasi Secret:**
   ```bash
   kubectl get secret hello-k8s-tls-secret
   ```

**3. Update Ingress untuk Menggunakan TLS**
   Buat file baru `ingress-tls.yaml` (atau edit `ingress.yaml`). Kita **harus** menambahkan `host` agar TLS berfungsi dengan benar.

   ```yaml
   # ingress-tls.yaml
   apiVersion: networking.k8s.io/v1
   kind: Ingress
   metadata:
     name: hello-k8s-ingress # Nama yang sama akan memperbarui Ingress yg ada
     annotations:
       # Anotasi mungkin diperlukan tergantung Ingress Controller Anda
       nginx.ingress.kubernetes.io/rewrite-target: /
       # Anotasi lain mungkin: force-ssl-redirect, etc.
   spec:
     ingressClassName: nginx # GANTI JIKA PERLU
     tls: # <-- Tambahkan bagian TLS
     - hosts:
       - hello-k8s.local # Host yang diamankan (harus cocok dgn CN cert & rule host)
       secretName: hello-k8s-tls-secret # Nama Secret TLS yang dibuat
     rules:
     - host: hello-k8s.local # <-- Tambahkan host di sini
       http:
         paths:
         - path: /
           pathType: Prefix
           backend:
             service:
               name: hello-k8s-service
               port:
                 number: 80
   ```

   **Terapkan perubahan:**
   ```bash
   kubectl apply -f ingress-tls.yaml
   ```

## Langkah 5: Mengakses Aplikasi via Ingress (HTTPS)

1.  **Edit file `/etc/hosts` lokal Anda (perlu admin/sudo):** Tambahkan baris berikut (ganti `<INGRESS_ADDRESS>` dengan IP/host Ingress Controller Anda):
    ```
    <INGRESS_ADDRESS> hello-k8s.local
    ```
2.  **Akses menggunakan `curl` (dengan `-k` karena sertifikat self-signed):**
    ```bash
    # Ganti <INGRESS_HTTPS_PORT> jika berbeda (misal 30443 untuk Kind/NodePort)
    # Defaultnya 443 jika LoadBalancer atau K3s/Docker Desktop
    curl -k https://hello-k8s.local:<INGRESS_HTTPS_PORT>/
    ```
3.  **Akses dari Browser:** Buka `https://hello-k8s.local:<INGRESS_HTTPS_PORT>/`. Browser Anda akan menampilkan peringatan keamanan karena sertifikatnya self-signed. Anda perlu menerima risiko untuk melanjutkan.

Anda seharusnya melihat output HTML "Hello Kubernetes!", sekarang diakses melalui HTTPS. Ingress Controller menangani terminasi TLS.

## Langkah 6: Pembersihan

```bash
# Hapus Ingress
kubectl delete ingress hello-k8s-ingress

# Hapus Secret TLS
kubectl delete secret hello-k8s-tls-secret

# Hapus file sertifikat lokal
# rm tls.key tls.csr tls.crt

# Hapus aplikasi dan service dari Lab 01 jika sudah tidak diperlukan
# kubectl delete service hello-k8s-service
# kubectl delete deployment hello-k8s-deployment

# Hapus entri dari /etc/hosts Anda

# Kembali ke namespace default
# kubectl config set-context --current --namespace=default

# Hapus namespace lab
kubectl delete namespace lab01-stateless
```

**Selamat!** Anda telah berhasil menggunakan Ingress untuk mengekspos aplikasi HTTP dan mengamankannya dengan TLS. Ingress adalah cara standar untuk mengelola akses L7 ke aplikasi Anda di Kubernetes.
