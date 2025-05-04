# Labels dan Selectors: Perekat Objek Kubernetes

**Labels** dan **Selectors** adalah mekanisme fundamental di Kubernetes yang memungkinkan Anda **mengorganisir** dan **memilih (memfilter)** subset objek Kubernetes. Mereka adalah "perekat" yang menghubungkan berbagai jenis objek, seperti menghubungkan Service ke Pods atau Deployment ke Pods yang dikelolanya.

## Labels

*   **Apa itu:** **Pasangan key-value (kunci-nilai)** berupa string yang Anda **lampirkan** ke objek Kubernetes (seperti Pods, Services, Nodes, Deployments, dll.) pada bagian `metadata.labels`.
*   **Tujuan:** Untuk **mengidentifikasi atribut** objek yang relevan bagi pengguna tetapi tidak memiliki arti semantik langsung bagi sistem inti Kubernetes. Labels digunakan untuk:
    *   Mengelompokkan objek (misalnya, semua Pods milik aplikasi "frontend").
    *   Memilih objek untuk operasi (misalnya, Service hanya menargetkan Pods dengan label `app=backend`).
    *   Memfilter tampilan objek di `kubectl`.
*   **Aturan & Konvensi:**
    *   Keys dan Values harus berupa string.
    *   Keys harus unik dalam satu objek.
    *   Keys biasanya terdiri dari dua bagian (opsional): `prefix/name`.
        *   `prefix` (Opsional): Namespace DNS (misalnya, `app.kubernetes.io/`). Prefix `kubernetes.io/` dicadangkan untuk komponen inti K8s.
        *   `name`: Nama kunci label itu sendiri (maksimal 63 karakter, alfanumerik, '-', '_', '.').
    *   Values juga string (maksimal 63 karakter, alfanumerik, '-', '_', '.').
*   **Contoh Labels Umum:**
    *   `app: myapp` atau `app.kubernetes.io/name: myapp` (Nama aplikasi)
    *   `environment: production` / `environment: staging` / `environment: development` (Lingkungan deployment)
    *   `tier: frontend` / `tier: backend` / `tier: cache` (Lapisan arsitektur)
    *   `release: stable` / `release: canary` / `release: v1.2.3` (Versi rilis)
    *   `owner: team-alpha` (Tim pemilik)
    *   `track: daily` / `track: weekly` (Untuk rilis bertahap)
*   **Penting:** Rancang strategi pelabelan yang **konsisten** di seluruh cluster Anda sejak awal. Ini akan sangat membantu pengelolaan jangka panjang. Lihat [Label yang Direkomendasikan Kubernetes](https://kubernetes.io/docs/concepts/overview/working-with-objects/common-labels/) untuk panduan.

**Contoh YAML dengan Labels:**

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: frontend-pod-7x9s
  labels:
    app.kubernetes.io/name: guestbook # Nama aplikasi (rekomendasi K8s)
    app.kubernetes.io/component: frontend # Komponen aplikasi (rekomendasi K8s)
    environment: production
    release: v2.1
spec:
  containers:
  - name: php-redis
    image: gcr.io/google_samples/gb-frontend:v4
    ports:
    - containerPort: 80
```

## Selectors

*   **Apa itu:** Cara untuk **memilih (memfilter)** objek Kubernetes berdasarkan **Labels** yang mereka miliki. Selectors adalah inti dari bagaimana objek yang berbeda saling terhubung.
*   **Penggunaan Utama:**
    *   **Service:** `spec.selector` pada Service menentukan Pods mana yang akan menjadi backend untuk Service tersebut.
    *   **Deployment/ReplicaSet/StatefulSet/DaemonSet:** `spec.selector` menentukan Pods mana yang dikelola oleh controller tersebut. Label di `spec.template.metadata.labels` Pod *harus* cocok dengan selector ini.
    *   **Job/CronJob:** Juga menggunakan selector untuk melacak Pods yang mereka buat.
    *   **`kubectl`:** Anda dapat menggunakan flag `-l` atau `--selector` untuk memfilter objek yang ditampilkan atau dimanipulasi.
    *   **NetworkPolicy:** Menggunakan `podSelector` dan `namespaceSelector` untuk menentukan Pods mana yang terpengaruh oleh kebijakan.
    *   **Node Affinity/Pod Affinity:** Menggunakan selector untuk menentukan Node atau Pod target.
*   **Jenis Selectors:** Kubernetes mendukung dua jenis selector utama:

    1.  **Equality-based Selectors (Berbasis Kesetaraan):**
        *   Memilih berdasarkan kecocokan **key dan value** label.
        *   Operator yang didukung:
            *   `=` atau `==`: Sama dengan (contoh: `environment=production`).
            *   `!=`: Tidak sama dengan (contoh: `tier!=frontend`).
        *   Anda dapat menggabungkan beberapa syarat dengan koma (`,`), yang bertindak sebagai operator **AND**. Contoh: `app=myapp,environment=production` (pilih objek dengan *kedua* label).
        *   Ini adalah jenis yang paling umum digunakan dalam `spec.selector.matchLabels`.

    2.  **Set-based Selectors (Berbasis Himpunan):**
        *   Memilih berdasarkan **keberadaan key** atau apakah **value** termasuk dalam **himpunan (set)** nilai tertentu.
        *   Operator yang didukung:
            *   `in`: Value label harus ada dalam daftar nilai yang diberikan (contoh: `environment in (production, staging)`).
            *   `notin`: Value label tidak boleh ada dalam daftar nilai yang diberikan (contoh: `tier notin (cache, db)`).
            *   `exists`: Objek harus memiliki label dengan key yang ditentukan (value tidak diperhatikan). Cukup tulis key-nya saja (contoh: `partition`).
            *   `!exists` atau `doesnotexist` (Meskipun `exists` lebih umum): Objek tidak boleh memiliki label dengan key yang ditentukan.
        *   Digunakan dalam `spec.selector.matchExpressions`. Anda dapat menggabungkan beberapa ekspresi (semuanya harus terpenuhi - AND).

*   **`spec.selector` dalam Controller/Service:** Biasanya memiliki dua sub-field:
    *   `matchLabels`: Peta (map) key-value sederhana untuk selektor berbasis kesetaraan (AND).
    *   `matchExpressions`: Daftar (list) ekspresi selektor berbasis himpunan.
    *   Jika *kedua* `matchLabels` dan `matchExpressions` ditentukan, **semua** syarat dari keduanya harus dipenuhi (AND).

**Contoh YAML Service dengan Selector:**

```yaml
apiVersion: v1
kind: Service
metadata:
  name: backend-service
spec:
  selector:
    # Pilih Pods yang memiliki KEDUA label ini:
    app.kubernetes.io/name: myapp
    app.kubernetes.io/component: backend
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8080
```

**Contoh YAML Deployment dengan Selector `matchExpressions`:**

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: advanced-deployment
spec:
  replicas: 3
  selector:
    matchLabels: # Syarat 1 (opsional jika matchExpressions ada)
      app: myapp
    matchExpressions: # Syarat 2 (harus dipenuhi bersama matchLabels)
      - {key: tier, operator: In, values: [cache, backend]} # Harus punya label tier=cache ATAU tier=backend
      - {key: environment, operator: NotIn, values: [development]} # TIDAK BOLEH punya label environment=development
      - {key: critical, operator: Exists} # HARUS punya label dengan key 'critical' (value bebas)
  template:
    metadata:
      labels:
        # Label Pod ini HARUS memenuhi SEMUA syarat selector di atas
        app: myapp
        tier: backend
        environment: production
        critical: "true"
    spec:
      # ... definisi kontainer ...
```

**Menggunakan Selectors dengan `kubectl`:**

```bash
# Equality-based (koma = AND)
kubectl get pods -l environment=production,tier=frontend

# Set-based (gunakan tanda kutip jika ada spasi atau karakter khusus)
kubectl get pods -l 'environment in (production,staging)'
kubectl get pods -l 'critical' # Exists
kubectl get pods -l '!canary' # Does not exist

# Menggabungkan
kubectl get pods -l 'app=myapp,environment in (prod,staging),!legacy'
```

Labels dan Selectors adalah mekanisme yang sangat kuat dan fundamental di Kubernetes. Menggunakannya secara efektif adalah kunci untuk membangun sistem yang terstruktur, dapat dikelola, dan terhubung dengan baik.
