# Deployments

Deployments adalah salah satu objek *workload* paling umum di Kubernetes. Mereka menyediakan cara deklaratif untuk mengelola pembaruan pada Pod dan ReplicaSets. Anda mendeskripsikan *state* (keadaan) yang diinginkan dalam Deployment, dan Deployment Controller akan mengubah *state* saat ini ke *state* yang diinginkan dengan kecepatan yang terkontrol.

## Mengapa Menggunakan Deployment?

*   **Mengelola Aplikasi Stateless:** Deployments sangat ideal untuk aplikasi stateless di mana setiap Pod identik dan dapat diganti dengan Pod lain.
*   **Pembaruan Deklaratif:** Anda cukup mendefinisikan state akhir yang diinginkan (misalnya, versi image baru), dan Kubernetes menangani proses pembaruan.
*   **Rolling Updates:** Melakukan pembaruan secara bertahap (rolling update) tanpa downtime. Pod baru dibuat dan Pod lama dihapus secara terkontrol.
*   **Rollback Mudah:** Jika pembaruan bermasalah, Anda dapat dengan mudah kembali (rollback) ke versi sebelumnya.
*   **Scaling:** Menaikkan atau menurunkan jumlah replika (Pod) dengan mudah.
*   **Self-healing:** Deployment memastikan jumlah Pod yang diinginkan selalu berjalan. Jika sebuah Pod gagal, Deployment akan menggantinya.

## Bagaimana Deployment Bekerja?

Deployment mengelola **ReplicaSet**. Saat Anda membuat Deployment, ia akan membuat ReplicaSet di belakang layar. ReplicaSet inilah yang bertanggung jawab untuk membuat dan mengelola jumlah Pod yang diinginkan sesuai dengan template Pod yang ditentukan dalam Deployment.

Ketika Anda memperbarui Deployment (misalnya, mengubah image container), Deployment akan:

1.  Membuat ReplicaSet baru dengan spesifikasi yang diperbarui.
2.  Secara bertahap menaikkan jumlah Pod di ReplicaSet baru.
3.  Secara bertahap menurunkan jumlah Pod di ReplicaSet lama.
4.  Setelah semua Pod baru berjalan dan Pod lama dihentikan, ReplicaSet lama tetap ada (untuk memungkinkan rollback) tetapi tidak mengelola Pod apa pun.

## Contoh YAML Deployment Sederhana

Berikut adalah contoh manifes YAML untuk Deployment sederhana yang menjalankan 3 replika Nginx:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx-deployment # Nama Deployment
  labels:
    app: nginx
spec:
  replicas: 3 # Jumlah Pod yang diinginkan
  selector:
    matchLabels:
      app: nginx # Selector untuk memilih Pod yang dikelola oleh Deployment ini
  template: # Template untuk membuat Pod
    metadata:
      labels:
        app: nginx # Label yang akan dimiliki oleh Pod
    spec:
      containers:
      - name: nginx
        image: nginx:1.14.2 # Image container yang akan digunakan
        ports:
        - containerPort: 80 # Port yang diekspos oleh container
```

**Penjelasan:**

*   `apiVersion: apps/v1`: Menentukan versi API Kubernetes untuk objek Deployment.
*   `kind: Deployment`: Menentukan tipe objek adalah Deployment.
*   `metadata`: Berisi data tentang Deployment, seperti `name` dan `labels`.
*   `spec`: Mendefinisikan state yang diinginkan untuk Deployment.
    *   `replicas: 3`: Menentukan bahwa kita ingin 3 Pod identik berjalan.
    *   `selector`: Menentukan bagaimana Deployment menemukan Pod yang harus dikelolanya. Label `app: nginx` di sini harus cocok dengan label di `spec.template.metadata.labels`.
    *   `template`: Mendefinisikan blueprint untuk Pod yang akan dibuat.
        *   `metadata.labels`: Label yang akan diterapkan pada setiap Pod yang dibuat oleh template ini.
        *   `spec.containers`: Daftar container yang akan dijalankan di dalam Pod. Di sini, kita hanya menjalankan satu container Nginx.

## Operasi Umum dengan `kubectl`

*   **Membuat Deployment:**
    ```bash
    kubectl apply -f nama-file-deployment.yaml
    ```
*   **Melihat Deployment:**
    ```bash
    kubectl get deployments
    kubectl describe deployment nama-deployment
    ```
*   **Melihat ReplicaSets yang dibuat oleh Deployment:**
    ```bash
    kubectl get rs
    ```
*   **Melihat Pods yang dibuat oleh Deployment:**
    ```bash
    kubectl get pods --selector=app=nginx # Gunakan selector yang sesuai
    ```
*   **Memperbarui Deployment (misalnya, ganti image):**
    Edit file YAML dan jalankan `kubectl apply -f nama-file-deployment.yaml` lagi, atau gunakan perintah `set image`:
    ```bash
    kubectl set image deployment/nama-deployment nama-container=image-baru:versi-baru
    # Contoh: kubectl set image deployment/nginx-deployment nginx=nginx:1.16.1
    ```
*   **Memantau status rollout:**
    ```bash
    kubectl rollout status deployment/nama-deployment
    ```
*   **Melihat riwayat revisi:**
    ```bash
    kubectl rollout history deployment/nama-deployment
    ```
*   **Rollback ke revisi sebelumnya:**
    ```bash
    kubectl rollout undo deployment/nama-deployment
    ```
*   **Rollback ke revisi spesifik:**
    ```bash
    kubectl rollout undo deployment/nama-deployment --to-revision=2
    ```
*   **Scaling Deployment:**
    ```bash
    kubectl scale deployment nama-deployment --replicas=5
    ```
*   **Menghapus Deployment:**
    ```bash
    kubectl delete deployment nama-deployment
    # Atau
    kubectl delete -f nama-file-deployment.yaml
    ```
    Menghapus Deployment juga akan menghapus ReplicaSet dan Pod yang terkait.

## Strategi Pembaruan (Update Strategies)

Deployment mendukung dua strategi pembaruan, yang ditentukan dalam `spec.strategy.type`:

1.  **`RollingUpdate` (Default):** Memperbarui Pod secara bertahap. Anda dapat mengontrol proses ini lebih lanjut dengan `maxUnavailable` (jumlah maksimum Pod yang boleh tidak tersedia selama pembaruan) dan `maxSurge` (jumlah maksimum Pod tambahan yang boleh dibuat di atas jumlah `replicas` yang diinginkan selama pembaruan). Ini memastikan *zero downtime* jika dikonfigurasi dengan benar.
2.  **`Recreate`:** Menghapus semua Pod lama terlebih dahulu sebelum membuat Pod baru. Ini akan menyebabkan *downtime* singkat selama proses pembaruan.

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx-deployment
spec:
  replicas: 3
  selector:
    matchLabels:
      app: nginx
  strategy:
    type: RollingUpdate # Bisa juga 'Recreate'
    rollingUpdate:
      maxUnavailable: 25% # Maksimal 25% Pod tidak tersedia
      maxSurge: 1       # Maksimal 1 Pod tambahan dibuat
  template:
    # ... (template Pod seperti contoh sebelumnya)
```

Deployments adalah fondasi penting untuk menjalankan dan mengelola aplikasi di Kubernetes, menyediakan otomatisasi untuk deployment, scaling, dan pembaruan.
