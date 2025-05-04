# Contoh YAML Definisi Service

Berikut adalah beberapa contoh definisi Service dalam YAML untuk mengilustrasikan tipe-tipe yang berbeda dan konfigurasi umumnya.

## Contoh 1: Service `ClusterIP` (Paling Umum)

Service ini mengekspos Pods dengan label `app=my-api` dan `tier=backend` di port 8080 secara internal di dalam cluster.

```yaml
# service-clusterip.yaml
apiVersion: v1
kind: Service
metadata:
  name: backend-api-service
  namespace: production # Berada di namespace 'production'
  labels:
    # Label untuk service itu sendiri (opsional)
    project: ecommerce
spec:
  # Tipe default adalah ClusterIP, jadi 'type: ClusterIP' bisa dihilangkan
  type: ClusterIP
  selector:
    # Pilih Pods yang memiliki KEDUA label ini
    app: my-api
    tier: backend
  ports:
    # Bisa mendefinisikan lebih dari satu port
    - name: http-api # Nama deskriptif untuk port
      protocol: TCP
      port: 8080 # Port yang diekspos oleh Service pada ClusterIP-nya
      targetPort: 8000 # Port pada Pods target tempat traffic diarahkan
                      # Bisa berupa nomor atau nama port dari container spec
    - name: grpc-internal
      protocol: TCP
      port: 9090
      targetPort: 9000 # Contoh port lain
```

**Cara Akses (dari dalam cluster):** `http://backend-api-service.production:8080` atau `grpc://backend-api-service.production:9090`

## Contoh 2: Service `NodePort`

Service ini mengekspos Pods dengan label `app=frontend` di port 80 pada setiap Node di cluster. Kubernetes akan memilih NodePort acak dari rentang 30000-32767.

```yaml
# service-nodeport.yaml
apiVersion: v1
kind: Service
metadata:
  name: frontend-web-nodeport
  namespace: web-staging
spec:
  type: NodePort # Tipe NodePort
  selector:
    app: frontend # Pilih Pods dengan label app=frontend
  ports:
    - name: http
      protocol: TCP
      port: 80       # Port pada ClusterIP internal (yg otomatis dibuat)
      targetPort: 8080 # Port pada Pods frontend target
      # nodePort: 30080 # Opsional: Tentukan NodePort spesifik (hati-hati potensi konflik!)
                       # Jika dikomentari, K8s akan memilih secara acak
```

**Cara Akses (dari luar cluster):** `http://<IP_Node_Mana_Saja>:<NodePort_Yang_Dialokasikan>` (misalnya `http://192.168.1.100:3xxxx`)

## Contoh 3: Service `LoadBalancer` (Membutuhkan Dukungan Cloud/Eksternal)

Service ini meminta penyedia cloud untuk membuat Load Balancer eksternal yang mengarahkan traffic port 443 ke port 8443 pada Pods dengan label `app=secure-gateway`.

```yaml
# service-loadbalancer.yaml
apiVersion: v1
kind: Service
metadata:
  name: secure-gateway-lb
  namespace: security
  annotations:
    # Anotasi spesifik cloud mungkin diperlukan di sini!
    # Contoh AWS: service.beta.kubernetes.io/aws-load-balancer-type: nlb
    # Contoh GCP: cloud.google.com/load-balancer-type: "Internal"
spec:
  type: LoadBalancer # Tipe LoadBalancer
  selector:
    app: secure-gateway
  ports:
    - name: https
      protocol: TCP
      port: 443 # Port yang diekspos oleh Load Balancer eksternal
      targetPort: 8443 # Port pada Pods target
  # externalTrafficPolicy: Local # Opsional: Pertimbangkan ini jika perlu IP sumber asli
```

**Cara Akses (dari luar cluster):** `https://<EXTERNAL_IP_LoadBalancer>:443` (EXTERNAL_IP akan muncul setelah LB dibuat oleh cloud).

## Contoh 4: Service `ExternalName`

Service ini membuat alias DNS internal `external-partner-api` yang menunjuk ke layanan eksternal `api.partner.com`.

```yaml
# service-externalname.yaml
apiVersion: v1
kind: Service
metadata:
  name: external-partner-api
  namespace: integrations
spec:
  type: ExternalName # Tipe ExternalName
  externalName: api.partner.com # Target FQDN eksternal
  # Tidak ada selector
  # Tidak ada ports (karena tidak ada proxying)
```

**Cara Akses (dari dalam cluster):** Aplikasi dapat menggunakan `http://external-partner-api.integrations` dan DNS akan me-resolve-nya ke `api.partner.com`.

## Contoh 5: Headless Service (Untuk StatefulSet atau Service Discovery Klien)

Service ini tidak memiliki ClusterIP dan akan me-resolve ke daftar IP Pods dengan label `app=my-stateful-app`.

```yaml
# service-headless.yaml
apiVersion: v1
kind: Service
metadata:
  name: my-stateful-app-headless
  namespace: databases
spec:
  clusterIP: None # Membuatnya Headless!
  selector:
    app: my-stateful-app
  ports:
    - name: peer-port # Port hanya untuk definisi, tidak digunakan untuk LB
      port: 7000
      targetPort: 7000
```

**Cara Akses (dari dalam cluster):**
*   DNS Query ke `my-stateful-app-headless.databases` akan mengembalikan multiple A records (IP Pods yang Ready).
*   Jika digunakan oleh StatefulSet bernama `my-sts`, Pod `my-sts-0` dapat diakses via DNS `my-sts-0.my-stateful-app-headless.databases`.

Contoh-contoh ini menunjukkan fleksibilitas Service Kubernetes dalam mengekspos aplikasi Anda sesuai dengan kebutuhan aksesibilitas yang berbeda. Selalu pilih tipe yang paling sesuai dengan kasus penggunaan Anda.
