# StatefulSets: Mengelola Aplikasi Stateful

Sementara `Deployment` sangat cocok untuk aplikasi *stateless* (di mana setiap replika Pod identik dan dapat saling menggantikan), banyak aplikasi penting bersifat *stateful*. Aplikasi stateful memiliki kebutuhan khusus yang tidak dapat dipenuhi oleh Deployment, seperti:

*   **Identitas Jaringan yang Stabil & Unik:** Setiap instance perlu nama host DNS yang persisten dan dapat diprediksi, bahkan jika Pod di-restart atau dijadwal ulang ke Node lain.
*   **Penyimpanan Persisten yang Stabil & Unik:** Setiap instance perlu volume penyimpanan persisten yang unik dan terikat padanya. Jika Pod dijadwal ulang, ia harus terhubung kembali ke volume penyimpanan *yang sama*.
*   **Deployment, Scaling, dan Deletion yang Terurut & Anggun:** Instance harus dibuat, diperbarui, atau dihapus dalam urutan yang ketat dan dapat diprediksi (misalnya, Pod 0, lalu Pod 1, lalu Pod 2). Ini penting untuk sistem terdistribusi seperti database yang memerlukan koordinasi antar node.

Contoh aplikasi stateful: Database (MySQL, PostgreSQL, MongoDB, Cassandra), sistem antrian pesan (Kafka, RabbitMQ), key-value store terdistribusi (etcd, Zookeeper), atau aplikasi kustom yang menyimpan state penting secara lokal.

Untuk memenuhi kebutuhan ini, Kubernetes menyediakan controller **StatefulSet**.

## Fitur Utama StatefulSet

StatefulSet mengelola sekumpulan Pods (berdasarkan template yang sama seperti Deployment), tetapi memberikan jaminan unik berikut:

1.  **Identitas Stabil dan Persisten per Pod:**
    *   **Nama Pod yang Dapat Diprediksi:** Pods dalam StatefulSet diberi nama dengan format `<nama-statefulset>-<indeks-ordinal>`, di mana indeks dimulai dari 0 (misalnya, `web-0`, `web-1`, `web-2`). Nama ini tetap melekat pada identitas logis Pod tersebut, bahkan jika Pod yang sebenarnya dihapus dan dibuat ulang.
    *   **Nama DNS Stabil per Pod:** Jika StatefulSet dikaitkan dengan **Headless Service** (lihat di bawah), setiap Pod mendapatkan entri DNS yang stabil dan dapat di-resolve:
        `<nama-pod>.<nama-headless-service>.<namespace>.svc.cluster.local`
        (Contoh: `web-0.nginx-headless.default.svc.cluster.local`). Ini memungkinkan penemuan peer-to-peer yang stabil antar Pods dalam StatefulSet.

2.  **Penyimpanan Persisten Stabil per Pod:**
    *   StatefulSet dapat menggunakan `spec.volumeClaimTemplates`. Ini adalah *template* untuk `PersistentVolumeClaim` (PVC).
    *   Untuk setiap Pod yang dibuat oleh StatefulSet (misalnya, `web-0`), sebuah PVC unik akan secara otomatis dibuat berdasarkan template ini (misalnya, `my-pvc-template-name-web-0`).
    *   PVC unik ini akan terikat ke `PersistentVolume` (PV) yang sesuai (baik melalui dynamic provisioning via StorageClass atau PV statis).
    *   Ketika Pod dijadwal ulang (misalnya karena Node gagal), Pod *baru* dengan nama ordinal yang sama (misalnya, `web-0` baru) akan **secara otomatis terhubung kembali ke PVC yang sama** (`my-pvc-template-name-web-0`), sehingga mempertahankan state-nya.
    *   **Penting:** PVC yang dibuat oleh `volumeClaimTemplates` **tidak** dihapus secara otomatis ketika StatefulSet di-scale down atau dihapus. Anda perlu menghapusnya secara manual jika datanya tidak lagi diperlukan, untuk menghindari biaya penyimpanan.

3.  **Deployment dan Scaling yang Terurut (Ordered):**
    *   **Scaling Up:** Pods dibuat **satu per satu**, berdasarkan indeks ordinal mereka (0, 1, 2, ...). Pod `<N>` tidak akan mulai dibuat sampai Pod `<N-1>` **berjalan dan siap (Running and Ready)**.
    *   **Scaling Down:** Pods dihapus dalam **urutan terbalik** (N, N-1, ..., 0). Pod `<N>` harus selesai terminasi sepenuhnya sebelum Pod `<N-1>` mulai dihentikan.

4.  **Update yang Terurut (Ordered Rolling Updates):**
    *   Ketika `spec.template` StatefulSet diperbarui, update diterapkan pada Pods **satu per satu**, dalam **urutan terbalik** secara default (N, N-1, ..., 0).
    *   Pod `<N>` akan diperbarui (Pod lama dihapus, Pod baru dibuat dengan template baru) dan harus menjadi `Ready` sebelum Pod `<N-1>` diperbarui.
    *   Anda dapat mengontrol strategi update dengan `spec.updateStrategy`:
        *   `RollingUpdate` (Default): Perilaku terurut seperti dijelaskan di atas. Anda bisa menggunakan `partition` untuk melakukan canary update (memperbarui hanya Pods dengan ordinal >= partition).
        *   `OnDelete`: Controller tidak secara otomatis memperbarui Pods. Anda perlu menghapus Pod lama secara manual, dan controller akan membuat Pod baru dengan versi baru untuk menggantikannya.

## Persyaratan Penting

1.  **Headless Service:** StatefulSet **memerlukan** sebuah [Headless Service](./08-services/headless-services.md) (`clusterIP: None`) yang `selector`-nya cocok dengan label Pods StatefulSet. Nama Service ini harus ditentukan dalam `spec.serviceName` StatefulSet. Headless Service inilah yang bertanggung jawab menyediakan domain jaringan dan entri DNS stabil per Pod.
2.  **Persistent Storage:** Agar state benar-benar persisten, Anda memerlukan `PersistentVolumes` yang disediakan (baik secara statis atau dinamis melalui `StorageClass`) yang dapat digunakan oleh `volumeClaimTemplates`.

## Contoh YAML StatefulSet (dengan Headless Service & PVC Template)

```yaml
# 1. Headless Service (WAJIB)
apiVersion: v1
kind: Service
metadata:
  name: nginx-headless # Nama Headless Service
  labels:
    app: nginx-sts
spec:
  ports:
  - port: 80
    name: web
  clusterIP: None # Kunci untuk Headless
  selector:
    app: nginx-sts # Harus cocok label Pod StatefulSet
---
# 2. StatefulSet
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: web-sts # Nama StatefulSet
spec:
  # Mereferensikan Headless Service
  serviceName: "nginx-headless"
  # Jumlah replika Pod yang diinginkan
  replicas: 3
  # Selector untuk menemukan Pods yang dikelola
  selector:
    matchLabels:
      app: nginx-sts # Harus cocok dgn selector Service & label template Pod
  # Template untuk Pods
  template:
    metadata:
      labels:
        app: nginx-sts # Label Pod
    spec:
      terminationGracePeriodSeconds: 10
      containers:
      - name: nginx
        image: registry.k8s.io/nginx-slim:0.8
        ports:
        - containerPort: 80
          name: web
        volumeMounts:
        - name: www-data # Nama mount volume (harus cocok dgn volumeClaimTemplates.name)
          mountPath: /usr/share/nginx/html # Path di dalam kontainer
  # Template untuk membuat PVC secara otomatis untuk setiap Pod
  volumeClaimTemplates:
  - metadata:
      name: www-data # Nama dasar PVC (akan ditambahi -<pod-name>, mis: www-data-web-sts-0)
    spec:
      accessModes: [ "ReadWriteOnce" ] # Mode akses PVC
      storageClassName: "standard" # (PENTING) Nama StorageClass utk dynamic provisioning
                                   # Atau cocokkan dgn PV statis jika provisioning manual
      resources:
        requests:
          storage: 1Gi # Ukuran volume yang diminta per Pod
```

**Dalam contoh ini:**

*   Akan dibuat 3 Pods: `web-sts-0`, `web-sts-1`, `web-sts-2`.
*   Akan dibuat 3 PVCs: `www-data-web-sts-0`, `www-data-web-sts-1`, `www-data-web-sts-2`, masing-masing meminta 1Gi dari StorageClass `standard`.
*   Setiap Pod akan me-mount PVC-nya sendiri ke `/usr/share/nginx/html`.
*   DNS `web-sts-0.nginx-headless.default.svc.cluster.local` akan me-resolve ke IP `web-sts-0`.

## Kapan Menggunakan StatefulSet vs. Deployment?

Gunakan **StatefulSet** jika aplikasi Anda memerlukan **satu atau lebih** dari jaminan berikut:

*   Identitas jaringan (DNS/hostname) yang stabil dan unik per instance.
*   Penyimpanan persisten yang stabil dan unik per instance.
*   Deployment, scaling, atau update yang terurut dan terkontrol.

Jika aplikasi Anda stateless dan setiap instance identik serta dapat saling menggantikan, **Deployment** biasanya merupakan pilihan yang lebih sederhana dan lebih disukai.

StatefulSet adalah komponen yang kuat tetapi juga lebih kompleks daripada Deployment. Pastikan Anda benar-benar membutuhkan jaminan yang diberikannya sebelum memilihnya.
