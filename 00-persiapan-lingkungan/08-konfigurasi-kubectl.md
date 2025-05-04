# Langkah 5: Memahami Konfigurasi `kubectl` (Kubeconfig)

Sekarang Anda memiliki `kubectl` terinstal dan sebuah cluster Kubernetes berjalan. Tapi bagaimana `kubectl` tahu *cluster mana* yang harus diajak bicara, dan *bagaimana cara mengautentikasi* dirinya ke cluster tersebut? Jawabannya terletak pada file konfigurasi `kubectl`, yang umumnya dikenal sebagai **kubeconfig**.

Memahami file kubeconfig penting karena:

*   Anda mungkin perlu berinteraksi dengan *beberapa* cluster (misalnya, lokal, development, staging, production).
*   Anda perlu tahu bagaimana `kubectl` mendapatkan kredensial untuk mengakses cluster.
*   Anda mungkin perlu memodifikasi atau membuat file kubeconfig secara manual dalam skenario tertentu.

## Apa itu File Kubeconfig?

File kubeconfig adalah file YAML yang menyimpan informasi tentang:

1.  **Clusters:** Mendefinisikan cluster Kubernetes yang dapat Anda akses. Setiap entri cluster biasanya berisi:
    *   `name`: Nama unik untuk merujuk ke cluster ini dalam file kubeconfig.
    *   `server`: URL dari Kubernetes API Server cluster tersebut.
    *   `certificate-authority-data` atau `certificate-authority`: Data sertifikat CA (Certificate Authority) dalam format base64 atau path ke file CA. Digunakan oleh `kubectl` untuk memverifikasi identitas API Server (mencegah serangan man-in-the-middle).
    *   `insecure-skip-tls-verify`: (Tidak disarankan untuk produksi!) Boolean untuk melewati verifikasi sertifikat server.

2.  **Users:** Mendefinisikan kredensial klien yang digunakan untuk autentikasi ke cluster. Setiap entri pengguna biasanya berisi:
    *   `name`: Nama unik untuk merujuk ke pengguna ini.
    *   Kredensial: Bisa berupa salah satu dari:
        *   `client-certificate-data` / `client-certificate`: Sertifikat klien base64 / path ke file sertifikat.
        *   `client-key-data` / `client-key`: Kunci privat klien base64 / path ke file kunci.
        *   `token`: Token Bearer (misalnya, Service Account token, OIDC token).
        *   `username` / `password`: Untuk autentikasi basic (semakin jarang digunakan).
        *   `auth-provider` / `exec`: Untuk mekanisme autentikasi yang lebih kompleks (misalnya, memanggil helper cloud provider untuk mendapatkan kredensial sementara).

3.  **Contexts:** Menggabungkan informasi dari satu `cluster`, satu `user`, dan (opsional) satu `namespace` default. Setiap entri konteks berisi:
    *   `name`: Nama unik untuk merujuk ke konteks ini.
    *   `cluster`: Nama cluster (dari bagian `clusters`) yang akan digunakan oleh konteks ini.
    *   `user`: Nama pengguna (dari bagian `users`) yang akan digunakan oleh konteks ini.
    *   `namespace` (Opsional): Namespace default yang akan digunakan oleh `kubectl` saat konteks ini aktif (jika tidak ditentukan, namespace `default` akan digunakan).

4.  **`current-context`:** Menentukan nama konteks mana (dari bagian `contexts`) yang **aktif** digunakan oleh `kubectl` secara default jika tidak ada konteks lain yang ditentukan secara eksplisit.

## Lokasi File Kubeconfig

`kubectl` mencari file kubeconfig dalam urutan berikut:

1.  **Flag `--kubeconfig`:** Jika Anda menentukan flag ini saat menjalankan `kubectl` (misalnya, `kubectl --kubeconfig=/path/to/custom/config get pods`), file yang ditentukan akan digunakan.
2.  **Variabel Environment `KUBECONFIG`:** Jika flag `--kubeconfig` tidak digunakan, `kubectl` akan memeriksa variabel environment `KUBECONFIG`. Variabel ini dapat berisi daftar path file kubeconfig yang dipisahkan oleh titik dua ( `:` di Linux/macOS) atau titik koma ( `;` di Windows). Konfigurasi dari semua file ini akan digabungkan.
3.  **Lokasi Default:** Jika kedua hal di atas tidak ada, `kubectl` akan mencari file di lokasi default: `$HOME/.kube/config`.

**Catatan:** Alat seperti Minikube, Kind, K3s, dan Docker Desktop biasanya **secara otomatis** memodifikasi file kubeconfig default (`$HOME/.kube/config`) untuk menambahkan cluster, user, dan konteks baru saat Anda membuat cluster lokal.

## Perintah `kubectl config`

`kubectl` menyediakan sub-perintah `config` untuk melihat dan memanipulasi file kubeconfig:

*   **Melihat Konfigurasi:**
    ```bash
    # Tampilkan konfigurasi yang digabungkan (dari semua sumber)
    kubectl config view

    # Tampilkan hanya konfigurasi mentah dari file default
    kubectl config view --raw

    # Tampilkan hanya konteks saat ini
    kubectl config current-context

    # Tampilkan daftar semua konteks yang tersedia
    kubectl config get-contexts
    # OUTPUT CONTOH:
    # CURRENT   NAME             CLUSTER          AUTHINFO         NAMESPACE
    # *         docker-desktop   docker-desktop   docker-desktop
    #           kind-belajar-k8s kind-belajar-k8s kind-belajar-k8s lab01
    #           minikube         minikube         minikube         default
    # (Tanda '*' menunjukkan konteks saat ini)

    # Tampilkan daftar cluster
    kubectl config get-clusters

    # Tampilkan daftar user
    kubectl config get-users
    ```

*   **Mengubah Konteks Aktif:**
    ```bash
    kubectl config use-context <nama-konteks>
    # Contoh: kubectl config use-context minikube
    ```

*   **Memodifikasi Konteks:**
    ```bash
    # Mengubah namespace default untuk konteks SAAT INI
    kubectl config set-context --current --namespace=<nama-namespace-baru>
    # Contoh: kubectl config set-context --current --namespace=production

    # Mengubah namespace default untuk konteks SPESIFIK
    kubectl config set-context <nama-konteks> --namespace=<nama-namespace-baru>
    ```

*   **Menambah/Mengubah Entri (Lebih Jarang Dilakukan Manual):**
    Perintah seperti `kubectl config set-cluster`, `kubectl config set-credentials`, `kubectl config set-context` memungkinkan Anda memodifikasi file kubeconfig secara terprogram, tetapi seringkali lebih mudah mengedit file YAML secara langsung atau mendapatkan file kubeconfig dari administrator cluster atau alat penyedia cluster.

## Mengelola Beberapa File Kubeconfig

Jika Anda bekerja dengan banyak cluster dan tidak ingin menggabungkan semuanya ke dalam file default, Anda bisa:

1.  **Menyimpan setiap konfigurasi dalam file terpisah.**
2.  **Menggunakan variabel environment `KUBECONFIG`:**
    ```bash
    # Linux/macOS
    export KUBECONFIG=~/.kube/config:~/.kube/config-work:~/.kube/config-prod

    # Windows (PowerShell)
    $env:KUBECONFIG="$HOME\.kube\config;$HOME\.kube\config-work;$HOME\.kube\config-prod"

    # Sekarang 'kubectl config get-contexts' akan menampilkan konteks dari semua file tersebut.
    ```
3.  **Menggunakan flag `--kubeconfig`:**
    ```bash
    kubectl --kubeconfig=~/.kube/config-work get pods -n app-staging
    ```

## Keamanan Kubeconfig

**Penting:** File kubeconfig berisi kredensial (sertifikat, kunci, token) yang memberikan akses ke cluster Kubernetes Anda. **Perlakukan file ini sebagai informasi sensitif!**

*   Jangan membagikan file kubeconfig Anda secara sembarangan.
*   Atur izin file yang sesuai (`chmod 600 ~/.kube/config`) agar hanya Anda yang bisa membacanya.
*   Jika menggunakan token, terutama Service Account token, berhati-hatilah karena token tersebut mungkin memiliki masa berlaku yang panjang atau tidak kedaluwarsa secara default.

Memahami bagaimana `kubectl` menemukan dan menggunakan konfigurasi adalah langkah penting untuk mengelola akses ke satu atau lebih cluster Kubernetes secara efektif dan aman.
