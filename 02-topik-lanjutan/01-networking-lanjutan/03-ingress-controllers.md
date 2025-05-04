# Ingress & Ingress Controllers: Mengekspos Layanan HTTP/S ke Luar Cluster

Kita sudah melihat bagaimana `Service` tipe `NodePort` dan `LoadBalancer` dapat digunakan untuk mengekspos aplikasi ke luar cluster. Namun, metode ini memiliki keterbatasan, terutama untuk aplikasi berbasis HTTP/S:

*   **`NodePort`:** Mengekspos port acak (atau tetap tapi terbatas) di setiap Node. Klien perlu tahu IP Node dan port tersebut. Tidak ideal untuk HA atau akses publik yang user-friendly. Memerlukan load balancer eksternal tambahan di depannya untuk produksi.
*   **`LoadBalancer`:** Membuat load balancer L4 (TCP/UDP) *terpisah* untuk *setiap* Service yang diekspos. Ini bisa menjadi mahal (setiap LB cloud provider biasanya dikenakan biaya) dan boros alamat IP publik jika Anda memiliki banyak layanan web.

Untuk mengatasi keterbatasan ini, terutama untuk lalu lintas HTTP/S (Layer 7), Kubernetes menyediakan mekanisme yang lebih fleksibel dan efisien: **Ingress**.

## Apa itu Ingress?

**Ingress** *bukanlah* sebuah Service. Sebaliknya, ini adalah **objek API Kubernetes** yang berfungsi sebagai **kumpulan aturan (rules)** untuk mengarahkan lalu lintas HTTP/S eksternal ke `Service` internal di dalam cluster.

Dengan Ingress, Anda dapat mendefinisikan aturan seperti:

*   Jika request datang untuk host `app.example.com` dengan path `/api`, arahkan ke `api-service` di port 8080.
*   Jika request datang untuk host `blog.example.com`, arahkan ke `blog-service` di port 80.
*   Jika request datang untuk host `app.example.com` dengan path `/ui`, arahkan ke `ui-service` di port 3000.
*   Konfigurasikan terminasi TLS (HTTPS) untuk `app.example.com` menggunakan sertifikat tertentu.

Ingress memungkinkan Anda mengelola akses eksternal ke berbagai layanan melalui **satu titik masuk (entrypoint)** tunggal (atau beberapa titik masuk yang terkelola), seringkali menggunakan satu load balancer dan satu alamat IP publik.

## Apa itu Ingress Controller?

Objek `Ingress` hanyalah **kumpulan aturan**. Ia tidak melakukan apa-apa sendirian. Agar aturan Ingress ini benar-benar berfungsi, Anda memerlukan **Ingress Controller**.

**Ingress Controller** adalah aplikasi (biasanya berjalan sebagai Deployment/DaemonSet di dalam cluster Anda) yang **bertugas untuk memenuhi aturan** yang didefinisikan dalam objek `Ingress`.

**Bagaimana Cara Kerjanya:**

1.  **Deployment Controller:** Anda men-deploy Ingress Controller pilihan Anda ke dalam cluster (misalnya, Nginx Ingress Controller, Traefik, HAProxy Ingress). Controller ini biasanya diekspos ke luar cluster menggunakan `Service` tipe `LoadBalancer` atau `NodePort` (yang kemudian diarahkan oleh LB eksternal). Ini menjadi titik masuk utama traffic eksternal.
2.  **Mengawasi Objek Ingress:** Pod Ingress Controller mengawasi API Server Kubernetes untuk pembuatan, pembaruan, atau penghapusan objek `Ingress`.
3.  **Konfigurasi Reverse Proxy:** Ketika Controller mendeteksi perubahan pada objek `Ingress`, ia akan menerjemahkan aturan-aturan tersebut ke dalam konfigurasi spesifik untuk reverse proxy L7 yang digunakannya (misalnya, mengkonfigurasi file `nginx.conf` untuk Nginx Ingress, atau konfigurasi internal Traefik).
4.  **Mengarahkan Lalu Lintas:** Ketika lalu lintas HTTP/S eksternal masuk ke titik masuk Ingress Controller (misalnya, melalui Service LoadBalancer-nya), reverse proxy yang telah dikonfigurasi akan memeriksa host, path, dan header request, lalu mengarahkannya ke `Service` dan `Pod` internal yang sesuai berdasarkan aturan Ingress yang cocok.

**Dengan kata lain:** Ingress Controller bertindak sebagai **reverse proxy cerdas** atau **API Gateway** untuk cluster Anda, yang konfigurasinya dikelola secara dinamis melalui objek `Ingress` Kubernetes.

## Ingress Controller Populer

Ada banyak implementasi Ingress Controller, beberapa yang umum:

*   **Ingress-NGINX:** Proyek yang dikelola oleh komunitas Kubernetes. Menggunakan Nginx sebagai reverse proxy. Sangat populer, stabil, dan kaya fitur.
*   **Traefik Kubernetes Ingress Provider:** Menggunakan Traefik Proxy. Dikenal karena kemudahan konfigurasi (sering menggunakan CRD selain Ingress standar), fitur otomatis (penemuan layanan, Let's Encrypt).
*   **HAProxy Ingress:** Menggunakan HAProxy yang dikenal handal dan berperforma tinggi.
*   **Contour:** Menggunakan Envoy Proxy (sama seperti Istio). Fokus pada fitur modern dan CRD `HTTPProxy` yang lebih fleksibel daripada Ingress standar.
*   **Ingress Controller Cloud Provider:** AWS (AWS Load Balancer Controller), GKE (GKE Ingress Controller), Azure (Application Gateway Ingress Controller - AGIC) menyediakan integrasi erat dengan load balancer L7 cloud native mereka.

## Contoh Objek Ingress YAML

```yaml
apiVersion: networking.k8s.io/v1 # Gunakan versi API yang stabil
kind: Ingress
metadata:
  name: my-app-ingress
  namespace: production
  annotations:
    # Anotasi sering digunakan untuk konfigurasi spesifik controller
    nginx.ingress.kubernetes.io/rewrite-target: / # Contoh untuk Nginx Ingress
    # kubernetes.io/ingress.class: "nginx" # Cara lama menentukan controller, sekarang pakai IngressClass
spec:
  # IngressClassName menunjuk ke resource IngressClass yang mengkonfigurasi controller mana yg digunakan
  ingressClassName: nginx-public # Nama IngressClass yang sudah dibuat admin
  tls: # Konfigurasi TLS (HTTPS)
  - hosts:
    - app.example.com # Host yang akan diamankan TLS
    secretName: my-app-tls-secret # Nama Secret K8s tipe 'kubernetes.io/tls'
                                  # yang berisi sertifikat dan kunci privat
  rules: # Daftar aturan routing
  - host: app.example.com # Aturan untuk host spesifik
    http:
      paths:
      - path: /api # Cocokkan path yang dimulai dengan /api
        pathType: Prefix # Tipe pencocokan path (Prefix atau Exact)
        backend: # Backend tujuan traffic
          service: # Merujuk ke Service K8s
            name: my-api-service # Nama Service backend
            port:
              number: 8080 # Port pada Service backend
      - path: / # Cocokkan path root (default jika yg lain tdk cocok)
        pathType: Prefix
        backend:
          service:
            name: my-frontend-service
            port:
              number: 80
  # Default backend (jika tidak ada aturan host/path yang cocok) - Opsional
  # defaultBackend:
  #   service:
  #     name: default-404-service
  #     port:
  #       number: 80
```

**Penjelasan Penting:**

*   **`apiVersion: networking.k8s.io/v1`**: Pastikan menggunakan versi API yang stabil.
*   **`ingressClassName`**: Cara modern untuk menentukan Ingress Controller mana yang harus menangani Ingress ini. Administrator cluster biasanya membuat resource `IngressClass` yang mereferensikan controller tertentu.
*   **`tls`**: Bagian ini mendefinisikan konfigurasi HTTPS. `secretName` harus merujuk ke Secret Kubernetes tipe `kubernetes.io/tls` yang berisi file `tls.crt` (sertifikat) dan `tls.key` (kunci privat). Ingress Controller akan menggunakan ini untuk terminasi TLS.
*   **`rules`**: Daftar aturan routing. Setiap aturan bisa memiliki `host` dan/atau `http` paths.
*   **`pathType`**: `Prefix` (mencocokkan awal path, mis: `/api` cocok dengan `/api/users`) atau `Exact` (harus cocok persis).
*   **`backend.service`**: Menentukan Service Kubernetes dan portnya yang akan menerima traffic.
*   **Annotations**: Sangat umum digunakan untuk mengontrol perilaku spesifik Ingress Controller (misalnya, rewrite URL, batas ukuran body, timeout, otentikasi, dll.). Anotasi bervariasi antar implementasi controller.

## Kapan Menggunakan Ingress?

Gunakan Ingress jika Anda perlu:

*   Mengekspos beberapa layanan HTTP/S melalui satu alamat IP/load balancer.
*   Melakukan routing berbasis Host atau Path.
*   Melakukan terminasi TLS (HTTPS) terpusat.
*   Menghemat biaya load balancer cloud dan alamat IP publik.

Ingress adalah cara standar dan paling efisien untuk mengelola akses eksternal ke aplikasi web dan API di Kubernetes. Pastikan Anda telah men-deploy Ingress Controller yang sesuai di cluster Anda agar objek Ingress dapat berfungsi.
