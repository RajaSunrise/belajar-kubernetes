# CronJobs: Menjalankan Tugas Terjadwal

Seringkali, Anda perlu menjalankan tugas (`Job`) secara **berkala** berdasarkan jadwal waktu, bukan hanya sekali jalan. Contohnya:

*   Menjalankan backup database setiap malam.
*   Mengirim laporan email setiap minggu.
*   Membersihkan data lama atau file sementara setiap jam.
*   Memicu pipeline analisis data secara periodik.

Untuk kebutuhan ini, Kubernetes menyediakan controller **CronJob**.

## Fungsi Utama CronJob

*   **Menjalankan Job Berdasarkan Jadwal:** CronJob adalah controller tingkat tinggi yang **membuat objek `Job`** secara otomatis berdasarkan jadwal waktu yang Anda tentukan.
*   **Jadwal Gaya Cron:** Jadwal ditentukan menggunakan format **[Cron](https://en.wikipedia.org/wiki/Cron)** standar Linux.
*   **Manajemen Riwayat Job:** CronJob dapat dikonfigurasi untuk menyimpan sejumlah Job yang berhasil dan gagal sebelumnya untuk tujuan audit atau debugging.

## Bagaimana CronJob Bekerja?

1.  **Definisi CronJob:** Anda membuat objek CronJob, menentukan:
    *   `spec.schedule`: Jadwal waktu dalam format Cron.
    *   `spec.jobTemplate`: **Template** untuk objek `Job` yang akan dibuat oleh CronJob setiap kali jadwal terpenuhi. Ini berisi `spec` (termasuk `template` Pod) untuk Job tersebut.
    *   Konfigurasi lain seperti kebijakan konkurensi, batas waktu, dan batas riwayat.
2.  **CronJob Controller:** Controller ini berjalan di Control Plane dan terus memeriksa semua objek CronJob.
3.  **Pemeriksaan Jadwal:** Pada setiap interval waktu (biasanya setiap menit), CronJob Controller memeriksa apakah ada CronJob yang jadwalnya cocok dengan waktu saat ini.
4.  **Pembuatan Job:** Jika jadwal cocok dan sesuai dengan kebijakan konkurensi:
    *   CronJob Controller akan **membuat objek `Job` baru** berdasarkan `spec.jobTemplate` dari CronJob.
    *   Nama Job biasanya `[nama-cronjob]-[timestamp]`.
5.  **Eksekusi Job:** Job yang baru dibuat kemudian akan berjalan seperti Job biasa (membuat Pod, memastikan penyelesaian, menangani kegagalan). CronJob Controller *tidak* secara langsung mengelola Pods; itu hanya membuat Job.
6.  **Pembersihan Riwayat:** CronJob Controller juga akan membersihkan Job lama (dan Pods terkaitnya, jika Job tidak punya TTL sendiri) berdasarkan `successfulJobsHistoryLimit` dan `failedJobsHistoryLimit`.

## Format Jadwal Cron (`spec.schedule`)

Formatnya terdiri dari lima field yang dipisahkan spasi, merepresentasikan:

```
┌───────────── menit (0 - 59)
│ ┌───────────── jam (0 - 23)
│ │ ┌───────────── hari dalam bulan (1 - 31)
│ │ │ ┌───────────── bulan (1 - 12)
│ │ │ │ ┌───────────── hari dalam minggu (0 - 6) (Minggu=0 atau 7)
│ │ │ │ │
│ │ │ │ │
* * * * *
```

Karakter khusus yang dapat digunakan:

*   `*`: Cocok dengan nilai apa pun (setiap menit, setiap jam, dll.).
*   `,`: Memisahkan beberapa nilai (mis: `0,15,30,45` untuk setiap 15 menit).
*   `-`: Menentukan rentang (mis: `9-17` untuk jam 9 pagi hingga 5 sore).
*   `/`: Menentukan langkah (mis: `*/15` di field menit berarti setiap 15 menit; `0 */2 * * *` berarti setiap 2 jam pada menit ke-0).

**Contoh Jadwal:**

*   `0 * * * *`: Setiap jam, pada menit ke-0.
*   `*/15 * * * *`: Setiap 15 menit.
*   `0 0 * * *`: Setiap hari pada tengah malam (00:00).
*   `0 4 * * SUN`: Setiap hari Minggu jam 4:00 pagi.
*   `0 0 1 * *`: Pada hari pertama setiap bulan, jam 00:00.

**Zona Waktu:** Jadwal CronJob dievaluasi berdasarkan **zona waktu Kube-Controller-Manager** yang menjalankannya.

## Konfigurasi CronJob Penting

Selain `schedule` dan `jobTemplate`, ada beberapa field `spec` lain yang berguna:

*   **`spec.concurrencyPolicy`:** Mengontrol bagaimana CronJob menangani eksekusi Job jika Job sebelumnya dari jadwal yang sama masih berjalan.
    *   `Allow` (Default): Memungkinkan Job berjalan secara bersamaan. Jika jadwal terlewat, beberapa Job bisa dimulai sekaligus.
    *   `Forbid`: Melarang eksekusi bersamaan. Jika Job sebelumnya masih berjalan saat jadwal berikutnya tiba, jadwal tersebut akan **dilewati**.
    *   `Replace`: Jika Job sebelumnya masih berjalan saat jadwal berikutnya tiba, Job lama akan **dibatalkan (dihapus)** dan digantikan oleh Job baru.
*   **`spec.suspend`:** Jika diatur ke `true`, CronJob Controller **tidak akan** membuat Job baru, tetapi Job yang sudah berjalan tidak akan terpengaruh. Berguna untuk menonaktifkan CronJob sementara tanpa menghapusnya. Default: `false`.
*   **`spec.successfulJobsHistoryLimit`:** Jumlah maksimum Job yang berhasil selesai yang akan disimpan riwayatnya. Default: 3.
*   **`spec.failedJobsHistoryLimit`:** Jumlah maksimum Job yang gagal yang akan disimpan riwayatnya. Default: 1. Mengatur batas ini ke 0 berarti Job yang gagal tidak akan disimpan.
*   **`spec.startingDeadlineSeconds`:** Batas waktu (dalam detik) untuk memulai Job jika jadwal terlewat (misalnya, karena cluster down). Jika Job tidak dapat dimulai dalam batas waktu ini setelah waktu jadwal seharusnya, Job tersebut akan dihitung sebagai gagal. Jika tidak diatur, tidak ada batas waktu.

## Contoh YAML CronJob (Backup Harian)

```yaml
# daily-backup-cronjob.yaml
apiVersion: batch/v1 # Grup API 'batch' (bukan batch/v1beta1 lagi)
kind: CronJob
metadata:
  name: daily-database-backup
  namespace: backups
spec:
  # Jadwal: Setiap hari jam 2:30 pagi
  schedule: "30 2 * * *"
  # Batas waktu jika jadwal terlewat (mis: 5 menit)
  startingDeadlineSeconds: 300
  # Jangan jalankan job baru jika yg lama masih jalan
  concurrencyPolicy: Forbid
  # Simpan riwayat 5 job sukses, 2 job gagal
  successfulJobsHistoryLimit: 5
  failedJobsHistoryLimit: 2
  # Template untuk Job yang akan dibuat
  jobTemplate:
    spec:
      # Beri waktu 10 menit utk job selesai sblm dianggap gagal
      # activeDeadlineSeconds: 600 # Bisa diatur di Job spec juga
      # Hapus Job & Pod 1 jam setelah selesai
      ttlSecondsAfterFinished: 3600
      template: # Template Pod untuk Job
        spec:
          containers:
          - name: db-backup-container
            image: my-backup-tool:latest
            args:
            - "--database=prod-db"
            - "--storage-bucket=s3://my-backup-bucket/daily"
            # Mungkin perlu env vars untuk kredensial (ambil dari Secret!)
            envFrom:
            - secretRef:
                name: backup-credentials
            resources:
              requests:
                memory: "256Mi"
                cpu: "200m"
              limits:
                memory: "512Mi"
                cpu: "500m"
          # PENTING: Restart policy untuk Pod Job
          restartPolicy: OnFailure # Coba lagi jika skrip backup gagal
```

## Mengelola CronJob dengan `kubectl`

*   **Membuat CronJob:**
    ```bash
    kubectl apply -f daily-backup-cronjob.yaml -n backups
    ```
*   **Melihat CronJobs:**
    ```bash
    kubectl get cronjobs -n backups
    # atau 'kubectl get cj'
    # OUTPUT CONTOH:
    # NAME                    SCHEDULE      SUSPEND   ACTIVE   LAST SCHEDULE   AGE
    # daily-database-backup   30 2 * * *    False     0        <none>          1m
    ```
*   **Melihat Jobs yang Dibuat oleh CronJob:** CronJob menambahkan label ke Jobs yang dibuatnya.
    ```bash
    # Temukan nama CronJob, lalu filter Job berdasarkan label itu
    # (Labelnya tidak standar, mungkin perlu describe cj utk lihat job template label)
    # Atau lihat semua Job di namespace
    kubectl get jobs -n backups
    # Akan muncul Job dengan nama seperti daily-database-backup-1672626600
    ```
*   **Memicu Job Secara Manual (dari CronJob Template):**
    ```bash
    kubectl create job --from=cronjob/daily-database-backup manual-backup-run -n backups
    ```
*   **Menangguhkan (Suspend) CronJob:**
    ```bash
    kubectl patch cronjob daily-database-backup -p '{"spec" : {"suspend" : true }}' -n backups
    ```
*   **Melanjutkan CronJob:**
    ```bash
    kubectl patch cronjob daily-database-backup -p '{"spec" : {"suspend" : false }}' -n backups
    ```
*   **Menghapus CronJob:**
    ```bash
    kubectl delete cronjob daily-database-backup -n backups
    # Ini TIDAK akan menghapus Job atau Pods yang sedang berjalan yg dibuatnya.
    # Anda mungkin perlu menghapus Job lama secara manual jika perlu.
    ```

CronJob adalah alat yang sangat berguna untuk mengotomatisasi tugas-tugas berulang di cluster Kubernetes Anda, menggantikan kebutuhan akan sistem `cron` tradisional di luar cluster.
