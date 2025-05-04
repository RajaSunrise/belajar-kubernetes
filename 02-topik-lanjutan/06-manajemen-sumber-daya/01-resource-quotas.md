# Resource Quotas: Membatasi Penggunaan Sumber Daya per Namespace

Dalam cluster Kubernetes yang digunakan oleh banyak tim, aplikasi, atau lingkungan (misalnya, dev, staging, prod) yang dipisahkan menggunakan **Namespaces**, ada risiko bahwa satu namespace dapat menghabiskan sumber daya cluster secara tidak proporsional, menyebabkan kelaparan sumber daya (resource starvation) untuk namespace lain.

Untuk mencegah hal ini dan memastikan pembagian sumber daya yang adil, Kubernetes menyediakan objek **ResourceQuota**.

## Apa itu ResourceQuota?

ResourceQuota adalah objek Kubernetes (namespaced) yang memungkinkan administrator untuk menetapkan **batasan total** pada jumlah sumber daya komputasi (CPU, Memori) dan jumlah objek API yang dapat dibuat atau dikonsumsi **di dalam satu Namespace tertentu**.

Ketika ResourceQuota diterapkan pada sebuah namespace:

*   Pengguna yang membuat sumber daya (seperti Pods, Services, PVCs) di namespace tersebut akan divalidasi terhadap kuota yang tersisa. Jika pembuatan sumber daya baru akan melebihi kuota yang ditetapkan, permintaan tersebut akan **ditolak** oleh API Server.
*   Ini membantu mencegah satu namespace memonopoli sumber daya cluster.

## Sumber Daya yang Dapat Dibatasi

ResourceQuota dapat membatasi berbagai jenis sumber daya:

**1. Kuota Sumber Daya Komputasi:**
   *   **Berdasarkan Permintaan (Requests):**
        *   `requests.cpu`: Jumlah total millicore CPU yang dapat *diminta* oleh semua Pod di namespace.
        *   `requests.memory`: Jumlah total Memori (dalam byte, mis: Mi, Gi) yang dapat *diminta* oleh semua Pod di namespace.
        *   `requests.storage`: Jumlah total kapasitas penyimpanan (mis: Gi, Ti) yang dapat *diminta* oleh semua PersistentVolumeClaims (PVCs) di namespace.
        *   `requests.ephemeral-storage`: (Jarang) Jumlah total penyimpanan ephemeral lokal yang diminta.
   *   **Berdasarkan Batas (Limits):**
        *   `limits.cpu`: Jumlah total millicore CPU yang dapat *dibatasi* untuk semua Pod di namespace.
        *   `limits.memory`: Jumlah total Memori yang dapat *dibatasi* untuk semua Pod di namespace.
        *   `limits.ephemeral-storage`: (Jarang) Jumlah total penyimpanan ephemeral lokal yang dibatasi.

   **Penting:** Agar kuota komputasi (`requests.*`, `limits.*`) berfungsi dengan benar, **setiap Pod** yang dibuat di namespace tersebut **harus** menentukan `requests` (dan `limits`, jika kuota limit diterapkan) untuk sumber daya yang relevan (CPU, Memori). Jika Pod tidak menentukan requests/limits, dan ada ResourceQuota yang aktif untuk sumber daya tersebut, Pod tersebut **akan ditolak** pembuatannya. Objek `LimitRange` sering digunakan bersama ResourceQuota untuk menetapkan nilai default requests/limits.

**2. Kuota Jumlah Objek:**
   *   `count/pods`: Jumlah maksimum Pods yang dapat ada di namespace.
   *   `count/services`: Jumlah maksimum Services.
   *   `count/replicationcontrollers`: Jumlah maksimum ReplicationControllers.
   *   `count/deployments.apps`: Jumlah maksimum Deployments.
   *   `count/replicasets.apps`: Jumlah maksimum ReplicaSets.
   *   `count/statefulsets.apps`: Jumlah maksimum StatefulSets.
   *   `count/jobs.batch`: Jumlah maksimum Jobs.
   *   `count/cronjobs.batch`: Jumlah maksimum CronJobs.
   *   `count/configmaps`: Jumlah maksimum ConfigMaps.
   *   `count/secrets`: Jumlah maksimum Secrets.
   *   `count/persistentvolumeclaims`: Jumlah maksimum PVCs.
   *   `count/services.nodeports`: Jumlah maksimum Services tipe NodePort.
   *   `count/services.loadbalancers`: Jumlah maksimum Services tipe LoadBalancer.
   *   Dan banyak lagi untuk objek lain... (Gunakan `kubectl api-resources --namespaced=true` untuk melihat daftar). Anda bisa membuat kuota untuk hampir semua objek namespaced dengan format `count/<resource>.<apigroup>`.

**3. Kuota Storage Berdasarkan StorageClass:**
   *   Anda dapat membatasi permintaan storage total *per StorageClass*:
        *   `<storage-class-name>.storageclass.storage.k8s.io/requests.storage`: Kuota permintaan storage untuk StorageClass spesifik.
        *   `<storage-class-name>.storageclass.storage.k8s.io/persistentvolumeclaims`: Kuota jumlah PVC untuk StorageClass spesifik.

**4. Kuota Berdasarkan Prioritas Pod (Pod Priority):**
   *   Anda dapat menetapkan kuota komputasi yang hanya berlaku untuk Pods dengan PriorityClass tertentu menggunakan `scopes` dan `scopeSelector`.

## Contoh YAML ResourceQuota

```yaml
apiVersion: v1
kind: ResourceQuota
metadata:
  name: compute-object-quota
  namespace: team-a-dev # Kuota ini berlaku untuk namespace team-a-dev
spec:
  hard: # Batasan keras (hard limits)
    # Kuota Komputasi
    requests.cpu: "2"       # Maks total 2 CPU core yang diminta
    requests.memory: 8Gi    # Maks total 8 GiB Memori yang diminta
    limits.cpu: "4"         # Maks total 4 CPU core yang dibatasi
    limits.memory: 16Gi   # Maks total 16 GiB Memori yang dibatasi

    # Kuota Jumlah Objek
    count/pods: "20"        # Maks 20 Pods
    count/services: "10"    # Maks 10 Services
    count/persistentvolumeclaims: "5" # Maks 5 PVCs
    count/secrets: "30"     # Maks 30 Secrets

    # Kuota Storage per StorageClass
    fast-ssd.storageclass.storage.k8s.io/requests.storage: 100Gi # Maks 100Gi via SC 'fast-ssd'
    slow-hdd.storageclass.storage.k8s.io/requests.storage: 500Gi # Maks 500Gi via SC 'slow-hdd'
```

**Menerapkan Kuota:**

```bash
kubectl apply -f my-quota.yaml -n team-a-dev
```

**Melihat Penggunaan Kuota:**

```bash
# Lihat detail ResourceQuota dan penggunaannya saat ini
kubectl describe resourcequota compute-object-quota -n team-a-dev
# Atau
kubectl get resourcequota compute-object-quota -n team-a-dev -o yaml

# Lihat semua kuota di namespace
kubectl get resourcequota -n team-a-dev
```
Output `describe` akan menunjukkan batas `hard`, jumlah yang `used` saat ini, dan yang `remaining`.

## Interaksi dengan LimitRange

Seperti disebutkan, agar kuota komputasi berfungsi, Pods harus menentukan `requests` dan/atau `limits`. Jika pengguna lupa menentukannya, Pod akan ditolak. Untuk mengatasi ini, **LimitRange** sering digunakan bersama ResourceQuota.

*   `LimitRange`: Menetapkan nilai **default**, **minimum**, atau **maksimum** untuk `requests` dan `limits` CPU/Memori per Pod atau per Kontainer di suatu namespace.
*   Jika Pod dibuat tanpa `requests`/`limits`, nilai default dari LimitRange akan diterapkan secara otomatis, memungkinkan Pod melewati pemeriksaan ResourceQuota (asalkan nilai default tidak melebihi kuota yang tersisa).

## Kasus Penggunaan

*   **Multi-Tenancy:** Mencegah satu tenant (tim/aplikasi) menghabiskan semua sumber daya cluster.
*   **Pembagian Lingkungan:** Menetapkan batas berbeda untuk namespace `dev`, `staging`, dan `prod`.
*   **Kontrol Biaya:** Membatasi pembuatan sumber daya yang mahal (seperti LoadBalancer Services atau PVC besar).
*   **Stabilitas Cluster:** Mencegah namespace tunggal menyebabkan ketidakstabilan cluster karena penggunaan resource yang berlebihan.

ResourceQuota adalah alat administratif penting untuk mengelola penggunaan sumber daya secara adil dan terkontrol dalam cluster Kubernetes bersama. Pastikan untuk menggunakannya bersama dengan LimitRange untuk pengalaman pengguna yang lebih baik saat menerapkan kuota komputasi.
