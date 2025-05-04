# Dependensi Chart (Subcharts) di Helm

Aplikasi modern seringkali terdiri dari beberapa komponen atau layanan yang saling bergantung. Misalnya, sebuah aplikasi web mungkin memerlukan database, sebuah message queue, atau cache. Daripada mencoba mengemas semua logika untuk semua komponen ini ke dalam satu Helm Chart raksasa, Helm memungkinkan Anda mendefinisikan **dependensi** pada Chart lain. Chart dependen ini disebut **subcharts**.

Menggunakan dependensi memungkinkan:

*   **Modularitas:** Memecah aplikasi kompleks menjadi Chart yang lebih kecil dan lebih mudah dikelola.
*   **Penggunaan Kembali (Reusability):** Memanfaatkan Chart yang sudah ada dan terkelola dengan baik (misalnya, Chart resmi untuk database seperti PostgreSQL atau Redis) sebagai bagian dari aplikasi Anda.
*   **Manajemen Versi:** Mengunci versi spesifik dari Chart dependen.

## Mendefinisikan Dependensi

Dependensi didefinisikan dalam bagian `dependencies` di file `Chart.yaml` milik Chart *induk* (parent chart).

```yaml
# my-app/Chart.yaml
apiVersion: v2
name: my-app
version: 0.1.0
appVersion: "1.0"
description: My application chart that depends on a database.

dependencies:
  # Dependensi 1: Menggunakan chart 'postgresql' dari repo Bitnami
  - name: postgresql           # Nama chart dependensi
    version: "12.x.x"         # Rentang versi SemVer yang dibutuhkan
    repository: "https://charts.bitnami.com/bitnami" # URL repositori Helm
    # Opsional: Kondisi untuk mengaktifkan/menonaktifkan dependensi ini
    # condition: postgresql.enabled
    # Opsional: Alias untuk mengakses values subchart dengan nama berbeda
    # alias: database

  # Dependensi 2: Menggunakan chart 'my-common-library' dari direktori lokal
  - name: my-common-library # Nama direktori subchart di dalam direktori 'charts/'
    version: "0.2.0"       # Versi subchart lokal
    # Tidak perlu 'repository' jika subchart ada di direktori 'charts/'
    # condition: common.enabled
```

**Field Kunci:**

*   **`name`**: Nama Chart dependen (seperti yang ada di repositori atau nama direktori di `charts/`).
*   **`version`**: Versi (atau rentang versi SemVer) dari Chart dependen yang dibutuhkan. Helm akan mencoba mencocokkan versi yang kompatibel.
*   **`repository`**: URL dari repositori Helm tempat Chart dependen dapat ditemukan. Jika dihilangkan, Helm akan mencarinya di dalam direktori `charts/` milik Chart induk.
*   **`condition`** (Opsional): Path ke nilai boolean di `values.yaml` Chart induk. Jika nilai ini `false`, dependensi ini **tidak akan dimuat** atau diinstal. Berguna untuk membuat dependensi opsional. Contoh: `postgresql.enabled`.
*   **`tags`** (Opsional): Daftar tag string. Memungkinkan pengaktifan/penonaktifan sekelompok dependensi sekaligus menggunakan flag `--set tags.mytag=false` saat instalasi.
*   **`alias`** (Opsional): Jika ditentukan, subchart ini akan dimuat di bawah alias ini dalam struktur `values.yaml` induk. Ini berguna jika Anda ingin menyertakan Chart yang sama beberapa kali dengan konfigurasi berbeda, atau jika nama Chart asli terlalu generik.

## Mengelola Dependensi

Setelah dependensi didefinisikan di `Chart.yaml`, Anda perlu **mengunduh dan mengelolanya** sebelum Chart induk dapat dikemas atau diinstal. Gunakan perintah `helm dependency`:

*   **Mengunduh/Memperbarui Dependensi:**
    ```bash
    # Pindah ke direktori Chart induk (mis: my-app/)
    cd my-app/

    # Unduh dependensi dari repo dan salin/update subcharts lokal ke direktori 'charts/'
    helm dependency update
    # atau
    helm dependency build # Mirip, tapi bisa menghapus file lama di 'charts/'

    # Ini akan:
    # 1. Membaca 'Chart.yaml'.
    # 2. Mengunduh chart 'postgresql' dari repo Bitnami (versi yang cocok) ke dalam direktori 'charts/'.
    # 3. Memverifikasi chart 'my-common-library' ada di 'charts/' (atau menyalinnya jika sumbernya berbeda).
    # 4. Membuat/memperbarui file 'Chart.lock' yang mengunci versi dependensi yang diunduh.
    ```
    **Penting:** File `Chart.lock` sebaiknya dimasukkan ke dalam sistem kontrol versi (Git) untuk memastikan build yang dapat direproduksi. Direktori `charts/` yang berisi dependensi terunduh **tidak** selalu perlu dimasukkan ke Git jika Anda selalu menjalankan `helm dependency update` sebagai bagian dari proses build/CI.

*   **Melihat Status Dependensi:**
    ```bash
    helm dependency list
    ```

## Mengakses Nilai Subchart

Secara default, nilai untuk subchart diakses di dalam `values.yaml` Chart induk menggunakan nama subchart sebagai kunci tingkat atas.

```yaml
# my-app/values.yaml

# Nilai untuk Chart induk 'my-app'
replicaCount: 2
image: my-app:1.0

# Nilai untuk subchart 'postgresql'
postgresql:
  # Kita bisa menimpa nilai default dari chart postgresql di sini
  auth:
    username: myuser
    database: myappdb
    # Password sebaiknya tidak di-hardcode, mungkin diambil dari secret atau --set
    # existingSecret: "my-postgres-secret"
  primary:
    persistence:
      size: 5Gi

# Nilai untuk subchart 'my-common-library'
my-common-library:
  someSetting: valueForCommon

# Jika menggunakan alias 'database' untuk postgresql:
# database:
#   auth:
#     username: myuser
#     # ...
```

Di dalam template Chart induk (`my-app/templates/`), Anda **tidak** dapat secara langsung mengakses nilai subchart (seperti `.Values.postgresql.auth.username`). Nilai subchart hanya digunakan oleh *template subchart itu sendiri*.

## Mengirim Nilai dari Induk ke Subchart (Global Values)

Terkadang, Anda ingin beberapa nilai dari Chart induk (misalnya, nama rilis, namespace, atau pengaturan global lainnya) tersedia untuk *semua* subchart. Helm menyediakan konsep **"Global Values"**.

Nilai yang didefinisikan di bawah kunci `global` di `values.yaml` Chart induk akan dapat diakses oleh *semua* Chart (induk dan semua subchart) melalui objek `.Values.global`.

```yaml
# my-app/values.yaml
global: # Nilai di bawah 'global' akan tersedia untuk semua subcharts
  environment: production
  datacenter: dc1

replicaCount: 1
image: my-app:1.0

postgresql:
  # ... nilai postgresql ...
```

```yaml
# postgresql/templates/configmap.yaml (Template di dalam subchart)
apiVersion: v1
kind: ConfigMap
metadata:
  name: postgres-config
data:
  # Mengakses nilai global dari Chart induk
  environment: {{ .Values.global.environment | default "unknown" }}
  # Mengakses nilai spesifik subchart
  primary_user: {{ .Values.auth.username | quote }}
```

## Pertimbangan

*   **Kompleksitas Nilai:** Mengelola nilai untuk banyak subchart bisa menjadi rumit. Pertimbangkan untuk memecah file values induk atau menggunakan alias.
*   **Versi Subchart:** Perhatikan rentang versi yang Anda tentukan. Pembaruan subchart mungkin memerlukan penyesuaian pada Chart induk Anda. File `Chart.lock` membantu menjaga konsistensi.
*   **Namespace:** Secara default, semua sumber daya dari Chart induk dan subchartnya diinstal ke namespace yang sama yang ditentukan saat `helm install`.
*   **Nama Resource:** Berhati-hatilah terhadap potensi konflik nama resource antara Chart induk dan subchart. Gunakan fungsi helper `fullname` (seperti yang didefinisikan di `_helpers.tpl`) secara konsisten untuk memastikan nama unik berdasarkan nama rilis.

Dependensi dan subcharts adalah fitur penting Helm yang mendorong modularitas dan penggunaan kembali, memungkinkan Anda membangun dan mengelola aplikasi Kubernetes yang kompleks dengan lebih efisien.
