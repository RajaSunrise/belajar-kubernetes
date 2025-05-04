# Headless Services: Service Tanpa Kepala (Tanpa ClusterIP)

Biasanya, ketika kita membuat `Service`, Kubernetes secara otomatis mengalokasikan alamat IP virtual internal yang stabil, yaitu **ClusterIP**. `kube-proxy` kemudian menggunakan ClusterIP ini untuk melakukan load balancing ke Pods backend.

Namun, ada skenario di mana kita **tidak** menginginkan ClusterIP atau load balancing bawaan dari Service. Kita hanya ingin menggunakan mekanisme Service untuk **penemuan layanan (service discovery)**, yaitu mendapatkan daftar alamat IP dari Pods yang mendukung layanan tersebut secara langsung. Di sinilah **Headless Service** berperan.

## Apa itu Headless Service?

Headless Service adalah Service biasa yang didefinisikan dengan mengatur `spec.clusterIP` secara eksplisit ke **`None`**.

```yaml
apiVersion: v1
kind: Service
metadata:
  name: my-headless-service
spec:
  clusterIP: None # Kunci untuk membuatnya Headless!
  selector:
    app: my-app # Selector untuk menemukan Pods target
  ports:
    - name: http
      port: 80 # Port tetap diperlukan untuk definisi Service
      targetPort: 8080
```

## Apa yang Terjadi Ketika `clusterIP: None`?

1.  **Tidak Ada ClusterIP yang Dialokasikan:** Kubernetes tidak akan mengalokasikan alamat IP virtual untuk Service ini.
2.  **Tidak Ada Load Balancing/Proxying oleh `kube-proxy`:** Karena tidak ada ClusterIP, `kube-proxy` tidak melakukan apa pun untuk Service ini. Aturan `iptables` atau `IPVS` tidak dibuat untuknya.
3.  **DNS Dikonfigurasi Secara Berbeda:** Ini adalah bagian kuncinya. Server DNS internal Kubernetes (biasanya CoreDNS) akan dikonfigurasi secara berbeda untuk Headless Service:
    *   **Untuk Service dengan Selector:** Alih-alih me-resolve nama Service (`<service-name>.<namespace>.svc.cluster.local`) ke satu ClusterIP, DNS akan mengembalikan **multiple A records**, satu untuk **setiap alamat IP Pod** yang saat ini `Ready` dan cocok dengan `selector` Service.
    *   **Untuk Service tanpa Selector (ExternalName atau definisi Endpoints manual):** Perilakunya bergantung pada tipe Service lainnya atau konfigurasi Endpoints/EndpointSlice manual.

## Kasus Penggunaan Headless Services

1.  **Service Discovery untuk StatefulSets (Paling Umum):**
    *   StatefulSets mengelola Pods yang memiliki identitas jaringan unik dan stabil (misalnya, `pod-0`, `pod-1`). Aplikasi stateful seringkali perlu berkomunikasi langsung dengan *rekan (peer)* spesifik dalam set tersebut (misalnya, untuk replikasi database, quorum).
    *   Headless Service digunakan sebagai `spec.serviceName` dalam StatefulSet. Ini memungkinkan setiap Pod dalam StatefulSet mendapatkan **entri DNS yang unik dan stabil**:
        `$(pod-name).$(service-name).$(namespace).svc.cluster.local`
        (Contoh: `my-db-pod-0.my-db-headless-svc.default.svc.cluster.local`)
    *   Klien (atau Pod lain dalam StatefulSet) dapat me-resolve nama DNS Pod spesifik ini untuk mendapatkan IP Pod tersebut secara langsung, melewati load balancing Service standar. Mereka juga bisa me-resolve nama Headless Service itu sendiri untuk mendapatkan daftar IP semua Pod yang Ready dalam StatefulSet tersebut.

2.  **Penemuan Layanan Terdesentralisasi / Sisi Klien:**
    *   Ketika Anda ingin logika load balancing atau pemilihan backend dilakukan oleh **klien itu sendiri**, bukan oleh `kube-proxy`.
    *   Klien dapat melakukan query DNS ke nama Headless Service untuk mendapatkan daftar semua IP Pod backend yang `Ready`.
    *   Klien kemudian dapat mengimplementasikan strategi load balancingnya sendiri (round-robin, acak, memilih berdasarkan latensi, dll.) untuk terhubung langsung ke salah satu IP Pod tersebut.

3.  **Database atau Sistem Terdistribusi Lainnya:**
    *   Mirip dengan StatefulSets, sistem terdistribusi lain yang berjalan di K8s mungkin memerlukan penemuan peer-to-peer langsung tanpa load balancing terpusat.

## Contoh: Headless Service untuk StatefulSet

```yaml
# Headless Service (WAJIB untuk StatefulSet jika butuh DNS Pod stabil)
apiVersion: v1
kind: Service
metadata:
  name: nginx-headless # Nama Service
  labels:
    app: nginx-sts
spec:
  ports:
  - port: 80
    name: web
  clusterIP: None # Membuatnya Headless
  selector:
    app: nginx-sts # Harus cocok dengan label Pod StatefulSet
---
# StatefulSet yang menggunakan Headless Service
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: web-sts
spec:
  serviceName: "nginx-headless" # <--- Mereferensikan Headless Service di atas
  replicas: 3
  selector:
    matchLabels:
      app: nginx-sts
  template:
    metadata:
      labels:
        app: nginx-sts
    spec:
      containers:
      - name: nginx
        image: registry.k8s.io/nginx-slim:0.8
        ports:
        - containerPort: 80
          name: web
        # ... volume mounts, etc. ...
```

Dengan konfigurasi ini:

*   Pod `web-sts-0` akan memiliki DNS: `web-sts-0.nginx-headless.default.svc.cluster.local`
*   Pod `web-sts-1` akan memiliki DNS: `web-sts-1.nginx-headless.default.svc.cluster.local`
*   Pod `web-sts-2` akan memiliki DNS: `web-sts-2.nginx-headless.default.svc.cluster.local`
*   Query DNS ke `nginx-headless.default.svc.cluster.local` akan mengembalikan daftar IP dari ketiga Pod (jika semuanya `Ready`).

## Ringkasan

Gunakan Headless Service (`clusterIP: None`) ketika Anda **tidak** membutuhkan IP virtual atau load balancing yang disediakan oleh Service biasa, tetapi Anda ingin memanfaatkan mekanisme penemuan layanan berbasis DNS Kubernetes untuk mendapatkan daftar IP Pod backend secara langsung atau untuk memberikan identitas DNS yang stabil per Pod (terutama dalam konteks StatefulSets).
