# Custom Resource Definitions (CRD): Memperluas API Kubernetes

Kubernetes hadir dengan sekumpulan objek API bawaan yang kaya (seperti Pods, Deployments, Services, ConfigMaps) yang mencakup banyak kasus penggunaan umum. Namun, terkadang Anda perlu mengelola sumber daya atau konsep yang **spesifik untuk domain atau aplikasi Anda** yang tidak terwakili oleh objek bawaan.

Misalnya, Anda mungkin ingin:

*   Mengelola konfigurasi aplikasi yang kompleks sebagai satu objek tingkat tinggi.
*   Mendefinisikan dan mengelola cluster database (seperti `PostgreSQLCluster`) secara deklaratif.
*   Merepresentasikan sumber daya infrastruktur eksternal (seperti bucket S3 atau database RDS) sebagai objek di dalam Kubernetes.
*   Mengotomatiskan tugas operasional yang kompleks.

Di sinilah **Custom Resource Definitions (CRD)** berperan. CRD adalah fitur inti Kubernetes yang memungkinkan Anda **memperluas API Kubernetes** dengan mendefinisikan **tipe objek kustom Anda sendiri**, yang disebut **Custom Resources (CR)**.

## Apa itu CRD dan CR?

1.  **Custom Resource Definition (CRD):**
    *   Ini adalah objek Kubernetes (`kind: CustomResourceDefinition`, `apiVersion: apiextensions.k8s.io/v1`) yang Anda **buat sekali** di cluster.
    *   CRD mendefinisikan **skema** dan **metadata** untuk tipe objek kustom baru Anda. Ini memberitahu API Server tentang:
        *   **Nama:** Nama singular, plural, dan `kind` untuk tipe baru (misalnya, singular `cronjob`, plural `cronjobs`, kind `CronJob` - contoh lama sebelum jadi bawaan).
        *   **Grup API:** Grup API tempat tipe baru ini akan berada (misalnya, `batch.tutorial.kubebuilder.io`).
        *   **Scope:** Apakah objek kustom ini bersifat `Namespaced` atau `Cluster`-scoped.
        *   **Versi:** Versi API untuk tipe kustom Anda (misalnya, `v1`, `v1alpha1`, `v1beta1`). Anda bisa memiliki beberapa versi.
        *   **Skema Validasi:** Menggunakan [OpenAPI v3 schema](https://swagger.io/specification/v3/) untuk mendefinisikan field-field yang valid (nama, tipe data, deskripsi, apakah wajib, dll.) di dalam `spec` dan `status` (opsional) dari objek kustom Anda. Ini memungkinkan API Server memvalidasi objek kustom saat dibuat atau diperbarui.
        *   **Subresources (Opsional):** Bisa mendefinisikan subresource seperti `/status` (untuk memisahkan update spec dan status) atau `/scale` (untuk integrasi dengan HPA).
        *   **Kolom Tambahan untuk `kubectl get` (Opsional):** Mendefinisikan kolom mana dari CR yang akan ditampilkan secara default oleh `kubectl get`.

2.  **Custom Resource (CR):**
    *   Setelah CRD dibuat di cluster, Anda (atau pengguna lain) dapat **membuat objek dari tipe kustom** tersebut, sama seperti Anda membuat objek bawaan seperti Pod atau Deployment. Objek instance ini disebut Custom Resource (CR).
    *   CR mengikuti skema yang didefinisikan dalam CRD-nya. Ia memiliki `apiVersion` (termasuk grup API kustom), `kind` (nama kind kustom), `metadata`, dan bagian `spec` (di mana Anda mendefinisikan state yang diinginkan untuk resource kustom Anda). Bagian `status` (jika didefinisikan di CRD) akan diisi oleh controller.

**Contoh Alur:**

1.  Anda membuat CRD untuk `kind: DatabaseCluster` dalam grup `mycompany.com/v1`. CRD ini mendefinisikan field seperti `spec.engine` (mysql/postgres), `spec.replicas`, `spec.storageSize`.
2.  Setelah CRD terdaftar, Anda dapat membuat objek `DatabaseCluster` baru:
    ```yaml
    apiVersion: mycompany.com/v1
    kind: DatabaseCluster
    metadata:
      name: my-prod-db
      namespace: databases
    spec:
      engine: postgres
      replicas: 3
      storageSize: 100Gi
    ```
3.  API Server akan memvalidasi objek ini terhadap skema di CRD `DatabaseCluster`. Jika valid, objek CR `my-prod-db` akan disimpan di etcd.

**Penting:** Membuat CRD dan CR **hanya mendefinisikan dan menyimpan state** objek kustom Anda. Mereka **tidak secara otomatis melakukan apa pun**. Agar CR Anda benar-benar *melakukan* sesuatu (seperti membuat Pods database, mengkonfigurasi replikasi, dll.), Anda perlu komponen tambahan yang disebut **Controller** (atau **Operator**).

## Contoh YAML CRD Sederhana

```yaml
apiVersion: apiextensions.k8s.io/v1
kind: CustomResourceDefinition
metadata:
  # Nama harus cocok dengan spec.names.plural + "." + spec.group
  name: crontabs.stable.example.com
spec:
  # Grup API tempat resource baru akan berada
  group: stable.example.com
  # Daftar versi yang didukung oleh CRD ini
  versions:
    - name: v1 # Nama versi
      served: true # Versi ini diaktifkan dan disajikan oleh API Server
      storage: true # Versi ini adalah versi penyimpanan (hanya satu yg boleh true)
      schema:
        # Skema OpenAPI v3 untuk validasi objek Crontab
        openAPIV3Schema:
          type: object
          properties:
            spec: # Mendefinisikan field di bawah 'spec'
              type: object
              properties:
                cronSpec:
                  type: string
                  description: "Jadwal cron dalam format string."
                image:
                  type: string
                  description: "Image kontainer yang akan dijalankan."
                replicas:
                  type: integer
                  minimum: 1
                  maximum: 10
                  description: "Jumlah replika job yang akan dijalankan."
              required: # Field yang wajib ada di 'spec'
              - cronSpec
              - image
            status: # (Opsional) Mendefinisikan field di bawah 'status'
              type: object
              properties:
                lastScheduleTime:
                  type: string
                  format: date-time
                activeJobs:
                  type: integer
  # Scope: Namespaced atau Cluster
  scope: Namespaced
  # Nama yang digunakan untuk resource
  names:
    # Nama plural yang digunakan di URL: /apis/<group>/<version>/namespaces/<namespace>/<plural>
    plural: crontabs
    # Nama singular
    singular: crontab
    # kind yang digunakan dalam manifest YAML (CamelCase)
    kind: CronTab
    # Nama pendek yang bisa digunakan di kubectl (opsional)
    shortNames:
    - ct
```

**Setelah CRD ini dibuat (`kubectl apply -f crd.yaml`), Anda bisa membuat objek `CronTab`:**

```yaml
apiVersion: "stable.example.com/v1"
kind: CronTab
metadata:
  name: my-new-cron-object
  namespace: default
spec:
  cronSpec: "* * * * */5" # Jalankan setiap 5 menit
  image: my-cron-job-image:latest
  replicas: 1
```

## Mengapa Menggunakan CRDs?

*   **API Kubernetes Native:** Mengelola sumber daya kustom Anda menggunakan alat dan alur kerja Kubernetes yang sudah dikenal (`kubectl`, GitOps, RBAC, dll.).
*   **Deklaratif:** Mendefinisikan state yang diinginkan untuk sumber daya kustom Anda.
*   **Validasi:** Skema OpenAPI memastikan bahwa objek kustom yang dibuat valid.
*   **Dasar untuk Otomatisasi (Operators):** CRD adalah fondasi untuk membangun **Operators**, yaitu controller kustom yang meng-encode pengetahuan operasional untuk mengelola aplikasi atau sumber daya yang didefinisikan oleh CRD tersebut.
*   **Ekstensibilitas:** Cara standar untuk memperluas fungsionalitas Kubernetes tanpa memodifikasi kode inti.

## Pertimbangan

*   **Desain API:** Mendesain skema CRD yang baik (jelas, konsisten, mudah digunakan) itu penting. Pikirkan tentang field `spec` (input pengguna) dan `status` (output controller).
*   **Manajemen Siklus Hidup:** CRD adalah objek cluster-scoped. Menghapus CRD akan menghapus *semua* objek Custom Resource (CR) dari tipe tersebut! Lakukan dengan hati-hati. Upgrade skema antar versi juga perlu direncanakan (konversi versi).
*   **Membutuhkan Controller:** Ingat, CRD hanya mendefinisikan tipe. Anda perlu *controller* (Operator) untuk benar-benar bertindak berdasarkan CR yang dibuat.

CRD adalah fitur yang sangat kuat yang memungkinkan Kubernetes diadaptasi dan diperluas untuk mengelola hampir semua jenis sumber daya atau konsep secara deklaratif, menjadikannya fondasi untuk otomatisasi tingkat lanjut melalui pola Operator.
