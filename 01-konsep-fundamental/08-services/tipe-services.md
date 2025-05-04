# Tipe-tipe Service Kubernetes

Saat Anda mendefinisikan sebuah objek `Service`, salah satu field paling penting dalam `spec` adalah `type`. Field `type` menentukan *bagaimana* Service tersebut akan diekspos dan diakses. Kubernetes mendukung beberapa tipe Service utama:

## 1. `ClusterIP` (Default)

*   **Definisi:** Mengekspos Service pada sebuah alamat IP **internal cluster** (ClusterIP).
*   **Aksesibilitas:** Service ini **hanya dapat dijangkau dari *dalam* cluster Kubernetes**. Pod lain atau komponen internal dapat mengaksesnya menggunakan ClusterIP atau nama DNS Service (`<service-name>.<namespace>.svc.cluster.local`). Ia tidak dapat diakses langsung dari luar cluster (misalnya, dari internet atau jaringan lokal Anda).
*   **Cara Kerja:** `kube-proxy` di setiap node mengkonfigurasi aturan jaringan (iptables/IPVS) untuk mencegat traffic ke ClusterIP:Port dan melakukan load balance ke salah satu IP:Port Pod backend yang `Ready`.
*   **Default:** Jika Anda tidak menentukan `spec.type` saat membuat Service, Kubernetes akan otomatis menggunakan `ClusterIP`.
*   **Kasus Penggunaan:** Tipe yang paling umum digunakan untuk **komunikasi antar layanan (service-to-service)** di dalam cluster. Misalnya, frontend Pod berkomunikasi dengan backend API Pod melalui Service ClusterIP, atau backend API berkomunikasi dengan database melalui Service ClusterIP.

**Contoh YAML:**
```yaml
apiVersion: v1
kind: Service
metadata:
  name: my-internal-api
spec:
  selector:
    app: my-api
  # type: ClusterIP # Ini adalah default, jadi bisa dihilangkan
  ports:
    - protocol: TCP
      port: 8080 # Port yang diekspos oleh Service (pada ClusterIP)
      targetPort: 80 # Port pada Pods target
```

## 2. `NodePort`

*   **Definisi:** Mengekspos Service pada **port statis tertentu** (NodePort) di **setiap Node** dalam cluster. Port ini berada dalam rentang yang telah dikonfigurasi (default: 30000-32767).
*   **Aksesibilitas:** Service dapat dijangkau dari **luar cluster** dengan menargetkan **`<NodeIP>:<NodePort>`** (di mana `<NodeIP>` adalah alamat IP *apapun* dari salah satu Node di cluster Anda).
*   **Cara Kerja:**
    1.  Kubernetes mengalokasikan sebuah port dari rentang NodePort (atau Anda dapat menentukan port spesifik dalam rentang tersebut menggunakan `spec.ports[].nodePort`, meskipun tidak disarankan karena potensi konflik).
    2.  Secara otomatis, Kubernetes juga membuat Service `ClusterIP` internal untuk Service `NodePort` ini.
    3.  `kube-proxy` di setiap Node mengkonfigurasi aturan jaringan untuk:
        *   Mencegat traffic yang masuk ke `<NodeIP>:<NodePort>` pada Node tersebut.
        *   Meneruskan traffic tersebut ke `ClusterIP:Port` internal dari Service.
        *   Traffic kemudian di-load balance dari ClusterIP ke Pods backend seperti biasa.
*   **Kasus Penggunaan:**
    *   Cara cepat untuk mengekspos aplikasi ke luar cluster selama **pengembangan atau pengujian**.
    *   Ketika Anda tidak memiliki atau tidak ingin menggunakan Load Balancer eksternal (misalnya, di lingkungan on-premise atau bare metal sederhana).
    *   Sebagai "pondasi" untuk Service tipe `LoadBalancer` atau Ingress Controller (mereka seringkali menargetkan NodePorts di belakang layar).
*   **Kekurangan:**
    *   Anda perlu tahu setidaknya satu IP Node.
    *   Port berada dalam rentang yang mungkin tidak standar (di atas 30000).
    *   Kurang ideal untuk produksi karena bergantung pada IP Node yang bisa berubah dan tidak ada load balancing *sebelum* traffic mencapai Node.

**Contoh YAML:**
```yaml
apiVersion: v1
kind: Service
metadata:
  name: my-web-app-nodeport
spec:
  selector:
    app: my-web-app
  type: NodePort # Tipe Service NodePort
  ports:
    - protocol: TCP
      port: 80 # Port pada ClusterIP internal (otomatis dibuat)
      targetPort: 8080 # Port pada Pods target
      # nodePort: 30007 # Opsional: Tentukan NodePort spesifik (Hati-hati!)
                      # Jika dihilangkan, K8s pilih port acak dari rentang
```
*Anda dapat mengaksesnya via `http://<IP_Node_Mana_Saja>:<NodePort>`.*

## 3. `LoadBalancer`

*   **Definisi:** Mengekspos Service secara eksternal menggunakan **load balancer dari penyedia cloud** (seperti AWS ELB, Google Cloud Load Balancer, Azure Load Balancer).
*   **Aksesibilitas:** Service mendapatkan **alamat IP eksternal (atau nama DNS)** yang stabil dari penyedia cloud, yang dapat digunakan untuk mengakses aplikasi dari internet.
*   **Cara Kerja:**
    1.  Membuat Service `type: LoadBalancer` memberi sinyal kepada `cloud-controller-manager` (jika berjalan dan terkonfigurasi) atau komponen integrasi cloud lainnya.
    2.  Komponen cloud ini akan secara otomatis **memesan (provision)** load balancer eksternal di infrastruktur cloud Anda.
    3.  Load balancer cloud tersebut akan dikonfigurasi untuk mengarahkan traffic ke **NodePorts** dari Service ini di semua Node yang relevan dalam cluster.
    4.  Secara otomatis, Kubernetes juga membuat Service `NodePort` dan `ClusterIP` untuk Service `LoadBalancer` ini.
    5.  Aliran traffic: Internet -> Cloud LB (IP Eksternal) -> Node (NodeIP:NodePort) -> Service (ClusterIP:Port) -> Pod (PodIP:TargetPort).
*   **Kasus Penggunaan:** Cara **standar dan direkomendasikan** untuk mengekspos aplikasi (terutama TCP/UDP non-HTTP/S) ke internet ketika berjalan di lingkungan **penyedia cloud** yang mendukungnya.
*   **Kekurangan:**
    *   **Membutuhkan dukungan dari penyedia cloud atau infrastruktur eksternal.** Tidak berfungsi di cluster lokal dasar (seperti Kind/Minikube tanpa addons khusus) atau bare metal tanpa solusi LB eksternal tambahan (seperti MetalLB).
    *   Biasanya **menimbulkan biaya** tambahan dari penyedia cloud untuk setiap Service LoadBalancer yang dibuat.
    *   Kurang fleksibel untuk routing HTTP/S kompleks (seperti routing berbasis path/host) dibandingkan Ingress.

**Contoh YAML:**
```yaml
apiVersion: v1
kind: Service
metadata:
  name: my-app-loadbalancer
spec:
  selector:
    app: my-critical-app
  type: LoadBalancer # Tipe Service LoadBalancer
  ports:
    - protocol: TCP
      port: 443 # Port eksternal yg diekspos oleh LB
      targetPort: 8443 # Port pada Pods target
  # externalTrafficPolicy: Local # Opsional: Hanya kirim traffic ke Pods di Node yg sama
                                # Mempertahankan IP sumber klien, tapi bisa tidak seimbang
```
*Setelah LB dibuat oleh cloud, `kubectl get service my-app-loadbalancer` akan menunjukkan `EXTERNAL-IP`.*

## 4. `ExternalName`

*   **Definisi:** Tipe Service khusus yang **tidak melakukan proxy atau load balancing** sama sekali. Sebaliknya, ia mengembalikan **record CNAME DNS** yang menunjuk ke nama DNS eksternal yang Anda tentukan di `spec.externalName`.
*   **Aksesibilitas:** Bergantung pada aksesibilitas nama DNS eksternal yang dituju.
*   **Cara Kerja:** Ketika klien di dalam cluster mencoba me-resolve nama DNS Service `ExternalName` (misalnya, `my-external-db.prod.svc.cluster.local`), server DNS internal cluster (CoreDNS) akan mengembalikan record CNAME yang menunjuk ke nilai `spec.externalName` (misalnya, `prod-rds-instance.abcdefg.us-west-2.rds.amazonaws.com`). Resolusi selanjutnya ditangani oleh resolver DNS klien.
*   **Kasus Penggunaan:**
    *   Membuat alias di dalam cluster untuk layanan eksternal (seperti database RDS, API pihak ketiga).
    *   Memungkinkan aplikasi internal merujuk ke layanan eksternal menggunakan nama Service Kubernetes yang konsisten, memudahkan migrasi atau perubahan backend eksternal di masa depan tanpa mengubah kode aplikasi.
*   **Penting:** Tidak ada ClusterIP, tidak ada NodePort, tidak ada Load Balancing. Ini murni pemetaan DNS.

**Contoh YAML:**
```yaml
apiVersion: v1
kind: Service
metadata:
  name: external-payment-api
  namespace: billing
spec:
  type: ExternalName # Tipe Service ExternalName
  externalName: api.payment-gateway.com # Nama DNS eksternal yg dituju
  # Tidak ada 'selector' atau 'ports' karena tidak ada proxying
```
*Aplikasi di namespace `billing` dapat menghubungi `http://external-payment-api` dan DNS akan me-resolve-nya ke `api.payment-gateway.com`.*

Memilih tipe Service yang tepat bergantung pada bagaimana Anda ingin mengekspos aplikasi Anda dan lingkungan tempat cluster Anda berjalan. `ClusterIP` untuk internal, `NodePort`/`LoadBalancer`/`Ingress` (objek terpisah) untuk eksternal.
