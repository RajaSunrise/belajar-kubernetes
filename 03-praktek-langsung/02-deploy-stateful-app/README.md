# Lab 02: Deploy Aplikasi Stateful (Database) dengan StatefulSet

**Tujuan:** Lab ini mendemonstrasikan cara men-deploy aplikasi stateful (dalam hal ini, database PostgreSQL sederhana) menggunakan `StatefulSet`. Kita akan fokus pada fitur kunci StatefulSet: identitas jaringan dan penyimpanan yang stabil dan unik per Pod.

**Konsep yang Dipelajari:**

*   Perbedaan antara aplikasi stateless (Deployment) dan stateful (StatefulSet).
*   Kebutuhan akan identitas Pod yang stabil (nama host, DNS).
*   Pentingnya penyimpanan persisten yang stabil (PVC per Pod).
*   Membuat `Secret` untuk kredensial database.
*   Membuat `Service` tipe `Headless` untuk penemuan peer StatefulSet.
*   Membuat `StatefulSet` dengan `volumeClaimTemplates`.
*   Mengamati pembuatan Pod dan PVC yang terurut.
*   Menguji persistensi data saat Pod di-restart.
*   Melakukan scaling StatefulSet.
*   Membersihkan sumber daya.

**Prasyarat:**

*   Cluster Kubernetes lokal berjalan (Minikube, Kind, K3s, Docker Desktop).
*   `kubectl` terinstal dan terkonfigurasi.
*   **Penting:** Sebuah **`StorageClass` yang berfungsi** dan mendukung **dynamic provisioning** harus tersedia di cluster Anda. Sebagian besar lingkungan lokal (Minikube, Kind, Docker Desktop) biasanya menyediakan satu secara default (misalnya, `standard`, `hostpath`, `gp2`). Verifikasi dengan `kubectl get sc`. Jika tidak ada, Anda perlu membuatnya atau menggunakan PV statis (yang lebih kompleks).
*   Pemahaman dasar tentang PVC, PV, dan StorageClass.
*   Klien `psql` terinstal di mesin lokal Anda (opsional, untuk pengujian koneksi).

## Langkah 1: Membuat Namespace

```bash
kubectl create namespace lab02-stateful
kubectl config set-context --current --namespace=lab02-stateful
```

## Langkah 2: Membuat Secret untuk Kredensial Database

Kita akan menyimpan password database dalam Secret, bukan hardcoding di manifest.

```bash
# Ganti 'YOUR_PASSWORD' dengan password yang aman
kubectl create secret generic pg-secret --from-literal=POSTGRES_PASSWORD='YOUR_PASSWORD'
```

Verifikasi Secret (data akan ter-encode base64):
```bash
kubectl get secret pg-secret -o yaml
```

## Langkah 3: Membuat Headless Service

StatefulSets memerlukan Headless Service untuk mengontrol domain jaringan Pods-nya dan menyediakan entri DNS unik per Pod.

Buat file `headless-service.yaml`:

```yaml
# headless-service.yaml
apiVersion: v1
kind: Service
metadata:
  name: postgres-headless # Nama penting, akan digunakan di StatefulSet
  labels:
    app: postgres # Label untuk Service (opsional)
spec:
  ports:
  - port: 5432
    name: postgresdb
  clusterIP: None # <-- Ini menjadikannya Headless Service
  selector:
    app: postgres # <-- Harus cocok dengan label Pods StatefulSet
```

**Terapkan manifest:**

```bash
kubectl apply -f headless-service.yaml
```

**Verifikasi:**
```bash
kubectl get service postgres-headless
# Perhatikan CLUSTER-IP adalah 'None'
```

## Langkah 4: Membuat StatefulSet

Ini adalah inti dari lab. Kita akan membuat StatefulSet untuk PostgreSQL.

Buat file `statefulset.yaml`:

```yaml
# statefulset.yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: postgres-sts # Nama StatefulSet
spec:
  serviceName: "postgres-headless" # <--- Harus cocok dengan nama Headless Service
  replicas: 2 # Mulai dengan 2 replika (mis: master & standby)
  selector:
    matchLabels:
      app: postgres # <--- Harus cocok dengan selector Service & label template Pod
  template: # Template untuk Pods
    metadata:
      labels:
        app: postgres # Label Pod
    spec:
      terminationGracePeriodSeconds: 10 # Waktu tunggu sebelum force kill
      containers:
      - name: postgres
        image: postgres:14 # Gunakan image PostgreSQL
        ports:
        - containerPort: 5432
          name: postgresdb
        env:
        - name: POSTGRES_USER
          value: "myuser" # Atau ambil dari Secret jika perlu
        - name: POSTGRES_DB
          value: "mydatabase"
        - name: PGDATA # Lokasi data PostgreSQL di dalam kontainer
          value: /var/lib/postgresql/data/pgdata
        # Ambil password dari Secret yang kita buat sebelumnya
        - name: POSTGRES_PASSWORD
          valueFrom:
            secretKeyRef:
              name: pg-secret # Nama Secret
              key: POSTGRES_PASSWORD # Key di dalam Secret
        volumeMounts:
        - name: postgres-data # Nama mount (harus cocok dgn nama volumeClaimTemplates)
          mountPath: /var/lib/postgresql/data # Mount point untuk data PG
        # Readiness probe sederhana (bisa lebih canggih)
        readinessProbe:
          exec:
            command: ["pg_isready", "-U", "myuser", "-d", "mydatabase"]
          initialDelaySeconds: 10
          timeoutSeconds: 5
          periodSeconds: 10
  # --- Template untuk membuat PVC secara otomatis ---
  volumeClaimTemplates:
  - metadata:
      name: postgres-data # Nama dasar untuk PVC (akan ditambahkan -<sts-name>-<ordinal>)
    spec:
      accessModes: [ "ReadWriteOnce" ] # Mode akses (cocok untuk database)
      # --- PENTING: Ganti nama StorageClass ini jika SC default Anda berbeda ---
      storageClassName: "standard" # Nama StorageClass yang berfungsi di cluster Anda
      resources:
        requests:
          storage: 2Gi # Ukuran volume persisten per Pod
```

**Penting:** Sesuaikan `storageClassName` dengan nama StorageClass yang valid di cluster Anda (`kubectl get sc`).

**Terapkan manifest:**

```bash
kubectl apply -f statefulset.yaml
```

## Langkah 5: Verifikasi Pembuatan Terurut dan Sumber Daya

Amati bagaimana StatefulSet membuat Pods dan PVCs satu per satu.

```bash
# Tonton pembuatan Pods
kubectl get pods -l app=postgres -w
# Anda akan melihat postgres-sts-0 dibuat, lalu postgres-sts-1 setelah yg pertama Ready.

# Periksa status StatefulSet
kubectl get statefulset postgres-sts
# Tunggu hingga READY = 2

# Periksa PVCs yang dibuat secara otomatis
kubectl get pvc -l app=postgres
# OUTPUT (Contoh):
# NAME                     STATUS   VOLUME                                     CAPACITY   ACCESS MODES   STORAGECLASS   AGE
# postgres-data-postgres-sts-0   Bound    pvc-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx   2Gi        RWO            standard       1m
# postgres-data-postgres-sts-1   Bound    pvc-yyyyyyyy-yyyy-yyyy-yyyy-yyyyyyyyyyyy   2Gi        RWO            standard       30s

# Periksa nama host dan DNS Pods (dari dalam Pod lain)
kubectl run tmp-debug --image=busybox:1.28 --rm -it --restart=Never -- /bin/sh

# Di dalam shell busybox:
# nslookup postgres-sts-0.postgres-headless # Resolves ke IP Pod-0
# nslookup postgres-sts-1.postgres-headless # Resolves ke IP Pod-1
# exit
```
Anda melihat Pods memiliki nama ordinal (`-0`, `-1`) dan PVC unik yang terikat padanya. DNS internal juga berfungsi per Pod melalui Headless Service.

## Langkah 6: Menguji Persistensi Data

Mari kita tulis data ke Pod pertama (`postgres-sts-0`) dan lihat apakah data tetap ada setelah Pod di-restart.

1.  **Masuk ke Pod-0:**
    ```bash
    kubectl exec -it postgres-sts-0 -- /bin/bash
    ```
2.  **Di dalam shell Pod-0, hubungkan ke psql:**
    ```bash
    # Gunakan user dan db yang didefinisikan di env var StatefulSet
    psql -U myuser -d mydatabase

    # Prompt psql akan muncul (mydatabase=>)
    ```
3.  **Buat tabel dan masukkan data:**
    ```sql
    CREATE TABLE messages (id SERIAL PRIMARY KEY, msg TEXT);
    INSERT INTO messages (msg) VALUES ('Hello from Pod 0!');
    SELECT * FROM messages;
    \q
    ```
4.  **Keluar dari shell Pod-0:**
    ```bash
    exit
    ```
5.  **Hapus Pod-0 (StatefulSet Controller akan membuatnya kembali):**
    ```bash
    kubectl delete pod postgres-sts-0
    ```
6.  **Tunggu Pod-0 yang baru menjadi Ready:**
    ```bash
    kubectl get pods -l app=postgres -w # Tunggu sampai postgres-sts-0 Running 1/1
    ```
7.  **Masuk lagi ke Pod-0 yang *baru*:**
    ```bash
    kubectl exec -it postgres-sts-0 -- /bin/bash
    ```
8.  **Hubungkan ke psql lagi:**
    ```bash
    psql -U myuser -d mydatabase
    ```
9.  **Periksa data:**
    ```sql
    SELECT * FROM messages;
    -- Anda HARUS melihat pesan "Hello from Pod 0!" lagi!
    \q
    ```
10. **Keluar dari shell Pod-0:**
    ```bash
    exit
    ```

Ini membuktikan bahwa meskipun Pod dibuat ulang, ia terhubung kembali ke PVC yang sama (`postgres-data-postgres-sts-0`), dan datanya tetap persisten.

## Langkah 7: Scaling StatefulSet

Mari kita scale StatefulSet menjadi 3 replika.

```bash
kubectl scale statefulset postgres-sts --replicas=3

# Amati pembuatan Pod dan PVC baru (postgres-sts-2)
kubectl get pods -l app=postgres -w
kubectl get pvc -l app=postgres
# Tunggu sampai semua 3 Pods/PVCs siap.
```
Penskalaan juga terjadi secara terurut (Pod-2 akan dibuat setelah Pod-1 siap).

## Langkah 8: Pembersihan

```bash
# Hapus StatefulSet (akan menghapus Pods)
kubectl delete statefulset postgres-sts

# Hapus Service
kubectl delete service postgres-headless

# Hapus Secret
kubectl delete secret pg-secret

# Hapus PVCs (PENTING: Data akan hilang jika reclaimPolicy adalah Delete!)
# Jika Anda ingin menyimpan data, hapus PVC secara manual nanti atau ubah reclaimPolicy PV.
kubectl delete pvc -l app=postgres

# Kembali ke namespace default (jika perlu)
# kubectl config set-context --current --namespace=default

# Hapus namespace lab
kubectl delete namespace lab02-stateful
```

**Selamat!** Anda telah berhasil men-deploy dan mengelola aplikasi stateful menggunakan StatefulSet, memanfaatkan identitas stabil dan penyimpanan persisten per Pod.
