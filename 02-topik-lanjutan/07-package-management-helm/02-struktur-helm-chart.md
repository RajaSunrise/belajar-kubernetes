# Struktur Direktori Helm Chart

Setiap Helm Chart adalah sebuah **direktori** yang berisi kumpulan file dan subdirektori dengan nama dan struktur yang spesifik. Memahami struktur ini penting untuk membuat dan memodifikasi Chart.

Berikut adalah struktur direktori tipikal dari sebuah Helm Chart:

```
nama-chart/                  # Nama direktori = Nama Chart
│
├── Chart.yaml             # WAJIB: Metadata tentang Chart (versi, nama, deskripsi, dll.)
│
├── values.yaml            # WAJIB: Nilai konfigurasi default untuk Chart ini.
│
├── templates/             # Direktori berisi file template manifest Kubernetes.
│   │
│   ├── deployment.yaml    # Contoh: Template untuk Deployment.
│   ├── service.yaml       # Contoh: Template untuk Service.
│   ├── ingress.yaml       # Contoh: Template untuk Ingress.
│   ├── configmap.yaml     # Contoh: Template untuk ConfigMap.
│   ├── secrets.yaml       # Contoh: Template untuk Secret (sering dibuat di luar template).
│   ├── NOTES.txt          # Opsional: Teks instruksi/catatan yang ditampilkan setelah instalasi berhasil.
│   └── _helpers.tpl       # Opsional: File untuk mendefinisikan "template helpers" (fungsi template kustom).
│   └── ...                # File template lainnya (.yaml, .tpl)
│
├── charts/                # Opsional: Direktori berisi dependensi Chart (subcharts).
│   │                      # Chart lain (.tgz atau direktori) ditempatkan di sini.
│   └── mariadb-10.1.2.tgz # Contoh subchart dependensi
│
├── crds/                  # Opsional: Direktori berisi definisi Custom Resource Definitions (CRDs).
│   │                      # CRD di sini diinstal SEBELUM template dirender saat 'helm install'.
│   └── my-crd.yaml        # Contoh file CRD.
│
└── .helmignore            # Opsional: File berisi pola file/direktori yang harus diabaikan saat packaging.

```

Mari kita bahas file dan direktori kunci:

**1. `Chart.yaml` (Wajib)**
   File ini berisi metadata penting tentang Chart.

   ```yaml
   apiVersion: v2 # Gunakan v2 untuk Helm 3+
   name: my-web-app # Nama chart (harus sama dengan nama direktori)
   description: A Helm chart for deploying my awesome web application.

   # Tipe aplikasi (opsional, bisa 'application' atau 'library')
   type: application

   # Versi Chart ini (gunakan Semantic Versioning - SemVer)
   version: 0.1.0

   # Versi aplikasi yang dikemas oleh chart ini (opsional tapi direkomendasikan)
   appVersion: "1.16.0"

   # Informasi maintainer (opsional)
   maintainers:
     - name: John Doe
       email: john.doe@example.com

   # Dependensi (jika menggunakan subcharts di direktori 'charts/' atau dari repo)
   dependencies:
     - name: mariadb # Nama chart dependensi
       version: "10.x.x" # Rentang versi yang dibutuhkan
       repository: "https://charts.bitnami.com/bitnami" # URL Repo (jika bukan dari dir 'charts/')
       # condition: mariadb.enabled # Opsional: hanya load jika value 'mariadb.enabled' true
       # alias: my-database # Opsional: gunakan nama alias untuk values dependensi
   ```
   *   **`apiVersion: v2`**: Wajib untuk Helm 3+. Menunjukkan format file `Chart.yaml`.
   *   **`name`**: Nama chart. Harus cocok dengan nama direktori.
   *   **`version`**: Versi chart itu sendiri, mengikuti SemVer (MAJOR.MINOR.PATCH). Setiap perubahan pada chart (template, values default) harus menaikkan versi ini.
   *   **`appVersion`**: Versi aplikasi yang sebenarnya di-deploy oleh chart ini (misalnya, versi image Docker). Berguna untuk informasi.
   *   **`dependencies`**: Mendefinisikan chart lain yang diperlukan oleh chart ini. Helm akan mengunduh dependensi ini (`helm dependency update`) sebelum instalasi/packaging.

**2. `values.yaml` (Wajib)**
   File ini mendefinisikan **nilai konfigurasi default** untuk Chart Anda. Nilai-nilai ini dapat ditimpa oleh pengguna saat instalasi atau upgrade. Struktur file ini bebas (biasanya mengikuti struktur logis aplikasi), dan nilai-nilai ini dapat diakses di dalam template menggunakan objek `.Values`.

   ```yaml
   # values.yaml
   replicaCount: 1 # Default jumlah replika

   image:
     repository: nginx # Default image repo
     pullPolicy: IfNotPresent
     # Tag image default kosong, seringkali diisi dari Chart.appVersion
     tag: ""

   service:
     type: ClusterIP # Default tipe service
     port: 80

   ingress:
     enabled: false # Default ingress dinonaktifkan
     className: ""
     hosts:
       - host: chart-example.local
         paths:
           - path: /
             pathType: ImplementationSpecific
     tls: []
     #  - secretName: chart-example-tls
     #    hosts:
     #      - chart-example.local

   # Contoh untuk subchart (jika ada alias 'my-database')
   # my-database:
   #   auth:
   #     rootPassword: "change-me"
   #     database: "my_app_db"
   ```

**3. `templates/` Direktori (Wajib Ada, Bisa Kosong)**
   Direktori ini berisi **semua file template manifest Kubernetes** yang akan dirender oleh Helm.
   *   File di dalam `templates/` biasanya memiliki ekstensi `.yaml`.
   *   Helm akan membaca *semua* file YAML di direktori ini, merendernya menggunakan engine templating Go + Sprig, menggabungkannya (jika perlu), dan kemudian mengirimkannya ke Kubernetes API Server.
   *   Nama file di dalam `templates/` tidak terlalu penting bagi Helm (kecuali `NOTES.txt` dan `_helpers.tpl`), tetapi praktik yang baik adalah menamainya sesuai dengan `kind` objek yang didefinisikannya (misalnya, `deployment.yaml`, `service.yaml`).
   *   **`NOTES.txt`:** File teks biasa (bisa berisi logika template) yang isinya akan **dicetak ke konsol pengguna** setelah `helm install` atau `helm upgrade` berhasil. Berguna untuk memberikan instruksi tentang cara mengakses aplikasi atau langkah selanjutnya.
   *   **`_helpers.tpl`:** File yang namanya diawali dengan underscore (`_`) dianggap sebagai "partial" atau "helper template". File ini tidak akan dirender sebagai manifest Kubernetes, tetapi digunakan untuk mendefinisikan **fungsi template kustom (named templates)** yang dapat dipanggil dan digunakan kembali di file template lain di dalam direktori `templates/`. Sangat berguna untuk menjaga template tetap DRY (Don't Repeat Yourself).

**4. `charts/` Direktori (Opsional)**
   Direktori ini digunakan untuk menyimpan **dependensi Chart (subcharts)** yang dikemas *bersama* Chart utama. Jika Anda mendeklarasikan dependensi di `Chart.yaml` tanpa `repository`, Helm akan mencarinya di direktori ini. Dependensi juga bisa berupa file arsip `.tgz` atau direktori chart yang belum dikemas. Gunakan `helm dependency build` atau `helm dependency update` untuk mengelola isi direktori ini berdasarkan `Chart.yaml`.

**5. `crds/` Direktori (Opsional)**
   Direktori ini berisi definisi **Custom Resource Definition (CRD)**. Berbeda dengan template biasa, CRD di direktori ini akan **diterapkan ke cluster oleh Helm *sebelum* template lain dirender** saat menjalankan `helm install`. Ini memastikan bahwa CRD sudah ada sebelum objek kustom (Custom Resources) yang menggunakannya (yang mungkin didefinisikan di `templates/`) dibuat. CRD tidak di-template dan tidak dihapus saat `helm uninstall`.

**6. `.helmignore` (Opsional)**
   Mirip seperti `.gitignore`, file ini berisi pola file atau direktori (satu per baris) yang harus **diabaikan oleh Helm** saat mengemas Chart menjadi file `.tgz` menggunakan `helm package`. Berguna untuk mengecualikan file dokumentasi, catatan, atau file sementara yang tidak perlu dimasukkan ke dalam paket Chart.

Memahami struktur standar ini memungkinkan Anda membaca, memodifikasi, dan membuat Helm Charts dengan lebih efektif.
