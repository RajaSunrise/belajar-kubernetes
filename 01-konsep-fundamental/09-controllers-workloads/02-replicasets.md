# ReplicaSets: Memastikan Jumlah Replika Pod

**ReplicaSet** adalah salah satu jenis controller fundamental di Kubernetes yang tujuan utamanya **sangat sederhana**: memastikan bahwa sejumlah **replika Pod** yang ditentukan selalu berjalan pada waktu tertentu.

## Fungsi Inti

*   **Menjaga Jumlah Replika:** Jika jumlah Pod aktual yang cocok dengan selector ReplicaSet kurang dari jumlah yang diinginkan (`spec.replicas`), ReplicaSet Controller akan membuat Pod baru (berdasarkan `spec.template`).
*   **Menghapus Kelebihan Replika:** Jika jumlah Pod aktual lebih banyak dari yang diinginkan (misalnya, karena Pod dengan label yang cocok dibuat secara manual atau oleh controller lain secara tidak sengaja), ReplicaSet Controller akan menghapus Pod tambahan.
*   **Self-Healing Dasar:** Jika sebuah Pod yang dikelola oleh ReplicaSet gagal, dihapus, atau Node tempatnya berjalan mati, ReplicaSet akan mendeteksi kekurangan tersebut dan secara otomatis membuat Pod pengganti untuk mempertahankan jumlah replika yang diinginkan.

## Hubungan dengan Deployment

**Penting:** Anda **hampir tidak pernah** perlu membuat atau mengelola ReplicaSet secara **langsung**.

**Deployment** adalah objek Workload Resource tingkat lebih tinggi yang **mengelola ReplicaSets** untuk Anda. Ketika Anda membuat sebuah `Deployment`, Deployment Controller akan membuat sebuah `ReplicaSet` di belakang layar (dengan nama seperti `[nama-deployment]-[hash-template-pod]`). ReplicaSet inilah yang kemudian benar-benar membuat dan mengelola Pods.

**Mengapa menggunakan Deployment alih-alih ReplicaSet langsung?**

Karena `Deployment` menambahkan fungsionalitas penting di atas `ReplicaSet`, yaitu:

1.  **Rolling Updates:** Deployment mengelola transisi antar versi aplikasi dengan membuat ReplicaSet *baru* untuk versi baru dan secara bertahap memindahkan replika dari ReplicaSet *lama* ke yang baru, memastikan zero downtime (jika menggunakan strategi `RollingUpdate`). ReplicaSet sendiri tidak memiliki mekanisme update bawaan.
2.  **Rollbacks:** Deployment menyimpan riwayat revisi (dalam bentuk ReplicaSets lama) dan memungkinkan Anda dengan mudah kembali (`undo`) ke revisi sebelumnya jika terjadi masalah. ReplicaSet tidak menyimpan riwayat.
3.  **Manajemen Deklaratif yang Lebih Baik:** Anda hanya perlu mengelola satu objek `Deployment` untuk mendefinisikan state aplikasi Anda, termasuk strategi update dan jumlah replika.

**Jadi, anggap ReplicaSet sebagai mekanisme implementasi internal yang digunakan oleh Deployment.** Anda berinteraksi dengan Deployment, dan Deployment menggunakan ReplicaSet untuk melakukan tugas replikasi dan self-healing dasar.

## Struktur YAML ReplicaSet (Hanya untuk Referensi)

Meskipun Anda tidak akan sering membuatnya manual, berikut adalah contoh struktur YAML ReplicaSet:

```yaml
# replicaset-example.yaml (JANGAN DIGUNAKAN LANGSUNG, GUNAKAN DEPLOYMENT!)
apiVersion: apps/v1 # Sama seperti Deployment
kind: ReplicaSet # Jenisnya ReplicaSet
metadata:
  name: frontend-replicaset
  labels:
    app: guestbook
    tier: frontend
spec:
  # Jumlah replika Pod yang diinginkan
  replicas: 3

  # Selector untuk menemukan Pods yang dikelola ReplicaSet ini
  selector:
    matchLabels:
      # Pod harus punya label ini agar dikelola
      tier: frontend
    # matchExpressions: ... # Juga bisa menggunakan ekspresi set

  # Template untuk membuat Pods (identik dengan template di Deployment)
  template:
    metadata:
      labels:
        # Label Pod HARUS memenuhi syarat selector di atas
        tier: frontend
        app: guestbook # Label tambahan
    spec:
      containers:
      - name: php-redis
        image: gcr.io/google_samples/gb-frontend:v3
        resources:
          requests:
            cpu: 100m
            memory: 100Mi
        ports:
        - containerPort: 80
```

Struktur `spec.selector` dan `spec.template` pada dasarnya identik dengan yang ada di Deployment. Perbedaannya adalah ReplicaSet tidak memiliki `spec.strategy` untuk update.

## Melihat ReplicaSets yang Dikelola Deployment

Anda dapat melihat ReplicaSets yang dibuat dan dikelola oleh Deployment Anda:

```bash
# Buat Deployment (jika belum ada)
kubectl create deployment my-nginx --image=nginx:1.25 --replicas=3

# Lihat ReplicaSet yang terkait dengan Deployment my-nginx
kubectl get replicaset # atau 'kubectl get rs'
# OUTPUT (Contoh):
# NAME                      DESIRED   CURRENT   READY   AGE
# my-nginx-7b7f8d4c9f       3         3         3       1m

# Perhatikan hash unik (7b7f8d4c9f) yang ditambahkan ke nama ReplicaSet.
# Hash ini berasal dari template Pod.

# Lakukan update pada Deployment (mis: ubah image)
kubectl set image deployment/my-nginx nginx=nginx:1.26

# Lihat ReplicaSets lagi selama atau setelah update
kubectl get rs
# OUTPUT (Contoh selama update):
# NAME                      DESIRED   CURRENT   READY   AGE
# my-nginx-7b7f8d4c9f       2         2         2       2m  <-- RS Lama, scaling down
# my-nginx-6f4dcc8f65       2         2         2       15s <-- RS Baru, scaling up

# Setelah update selesai:
# NAME                      DESIRED   CURRENT   READY   AGE
# my-nginx-7b7f8d4c9f       0         0         0       3m  <-- RS Lama, 0 replika
# my-nginx-6f4dcc8f65       3         3         3       1m  <-- RS Baru, 3 replika

# Deployment menyimpan RS lama (sesuai revisionHistoryLimit) untuk rollback.
