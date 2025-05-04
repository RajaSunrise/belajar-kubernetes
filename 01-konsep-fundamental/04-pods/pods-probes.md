# Pod Probes: Memeriksa Kesehatan & Kesiapan Kontainer

Menjalankan kontainer saja tidak cukup. Kubernetes perlu tahu apakah aplikasi di dalam kontainer tersebut benar-benar **hidup (sehat)** dan **siap (ready)** untuk melayani lalu lintas. Tanpa mekanisme ini, Kubernetes mungkin mengirim traffic ke Pod yang crash atau belum siap, atau gagal me-restart Pod yang macet.

Di sinilah **Probes** berperan. Probes adalah pemeriksaan diagnostik periodik yang dilakukan oleh **Kubelet** pada kontainer untuk memahami state kesehatannya. Ada tiga jenis probe utama:

## 1. Liveness Probe (`livenessProbe`)

*   **Tujuan:** Untuk mendeteksi apakah kontainer **masih hidup dan responsif**. Apakah aplikasi di dalamnya macet (deadlock) atau dalam keadaan tidak sehat yang tidak dapat dipulihkan?
*   **Aksi Jika Gagal:** Jika `livenessProbe` gagal beberapa kali berturut-turut (sesuai `failureThreshold`), Kubelet akan **membunuh (kill)** kontainer tersebut.
*   **Restart:** Apa yang terjadi selanjutnya tergantung pada `restartPolicy` Pod:
    *   `Always` (Default untuk Pod Deployment/StatefulSet): Kubelet akan mencoba me-restart kontainer yang gagal.
    *   `OnFailure`: Kubelet akan mencoba me-restart kontainer.
    *   `Never`: Kontainer tidak akan di-restart, dan Pod mungkin akan masuk ke fase `Failed`.
*   **Kapan Menggunakan:** Gunakan `livenessProbe` untuk aplikasi yang bisa macet atau masuk ke state tidak responsif tanpa benar-benar crash (keluar). Jika aplikasi Anda selalu crash (keluar) saat tidak sehat, `livenessProbe` mungkin tidak terlalu diperlukan karena `restartPolicy` sudah akan menanganinya. Namun, probe ini tetap bisa berguna untuk mendeteksi deadlock.

## 2. Readiness Probe (`readinessProbe`)

*   **Tujuan:** Untuk mendeteksi apakah kontainer **siap dan mampu melayani lalu lintas**. Apakah aplikasi sudah selesai inisialisasi? Apakah sudah terhubung ke database? Apakah siap menerima permintaan baru?
*   **Aksi Jika Gagal:** Jika `readinessProbe` gagal:
    *   Kubelet **tidak** akan membunuh atau me-restart kontainer.
    *   **Penting:** Endpoint Controller (atau EndpointSlice Controller) akan **menghapus alamat IP Pod** dari daftar endpoint Service yang menargetkan Pod tersebut.
*   **Efek:** Traffic dari Service **tidak akan lagi diarahkan** ke Pod yang tidak `Ready`. Ini mencegah pengguna atau layanan lain mengirim permintaan ke instance aplikasi yang belum siap atau sedang sibuk/tidak sehat sementara. Setelah probe berhasil lagi, endpoint akan ditambahkan kembali.
*   **Kapan Menggunakan:** Gunakan `readinessProbe` untuk *semua* kontainer yang melayani traffic atau perlu waktu untuk inisialisasi. Ini sangat penting untuk memastikan zero-downtime rolling updates dan mencegah pengguna mengalami error saat aplikasi baru dimulai atau sedang dalam maintenance sementara.

## 3. Startup Probe (`startupProbe`)

*   **Tujuan:** Untuk aplikasi yang membutuhkan waktu **startup yang lama** sebelum siap untuk diperiksa oleh liveness/readiness probe. Terkadang, aplikasi yang lambat startup bisa terbunuh oleh `livenessProbe` sebelum sempat menjadi sehat.
*   **Cara Kerja:** Jika `startupProbe` didefinisikan:
    *   Semua probe lain (`livenessProbe`, `readinessProbe`) akan **dinonaktifkan** sampai `startupProbe` **berhasil**.
    *   `startupProbe` akan dijalankan secara periodik.
    *   Jika `startupProbe` berhasil, Kubelet akan mengambil alih dengan `livenessProbe` dan `readinessProbe` seperti biasa.
    *   Jika `startupProbe` gagal melewati `failureThreshold` *sebelum* berhasil, Kubelet akan membunuh kontainer (sama seperti `livenessProbe` yang gagal).
*   **Kapan Menggunakan:** Gunakan `startupProbe` jika aplikasi Anda membutuhkan waktu inisialisasi yang signifikan (misalnya, puluhan detik atau beberapa menit) dan Anda ingin mencegah `livenessProbe` yang terlalu agresif membunuhnya sebelum waktunya. Anda mungkin perlu mengatur `failureThreshold * periodSeconds` pada `startupProbe` agar cukup panjang untuk menutupi waktu startup terburuk aplikasi Anda.

## Tipe-tipe Pemeriksaan Probe

Ketiga jenis probe (Liveness, Readiness, Startup) dapat melakukan pemeriksaan menggunakan salah satu dari tiga mekanisme berikut:

1.  **`exec`:**
    *   Menjalankan sebuah **perintah** di dalam kontainer.
    *   Probe dianggap **berhasil** jika perintah keluar dengan **exit code 0**.
    *   Probe dianggap **gagal** jika perintah keluar dengan exit code non-zero.
    *   *Contoh:* Menjalankan skrip shell kecil yang memeriksa koneksi database atau status file.
    ```yaml
    livenessProbe:
      exec:
        command:
        - cat # Perintah sederhana
        - /tmp/healthy # File yg akan dicek keberadaannya
    ```

2.  **`httpGet`:**
    *   Mengirim permintaan **HTTP GET** ke alamat IP Pod pada path dan port yang ditentukan.
    *   Probe dianggap **berhasil** jika respons memiliki **status code antara 200 dan 399 (inklusif)**.
    *   Probe dianggap **gagal** jika mendapatkan status code lain atau koneksi gagal.
    *   *Contoh:* Mengakses endpoint `/healthz` atau `/ready` pada aplikasi web.
    ```yaml
    readinessProbe:
      httpGet:
        path: /ready # Path endpoint kesiapan
        port: 8080 # Port tempat aplikasi listen
        scheme: HTTP # Bisa HTTP atau HTTPS
        # httpHeaders: # Opsional: header kustom
        # - name: Custom-Header
        #   value: Awesome
    ```

3.  **`tcpSocket`:**
    *   Mencoba membuka **koneksi TCP socket** ke port yang ditentukan pada alamat IP Pod.
    *   Probe dianggap **berhasil** jika koneksi **berhasil dibuat**.
    *   Probe dianggap **gagal** jika koneksi ditolak atau timeout.
    *   *Contoh:* Memeriksa apakah server database atau layanan lain yang berjalan di kontainer menerima koneksi di port tertentu.
    ```yaml
    livenessProbe:
      tcpSocket:
        port: 6379 # Port Redis, misalnya
    ```
4.  **`grpc` (Alpha/Beta):**
    *   Melakukan panggilan prosedur jarak jauh (RPC) menggunakan gRPC.
    *   Probe dianggap **berhasil** jika status yang dikembalikan oleh pemeriksaan kesehatan gRPC adalah `SERVING`.
    *   Memerlukan endpoint gRPC Health Checking Protocol diimplementasikan oleh aplikasi.

## Konfigurasi Probe Umum

Setiap probe dapat dikonfigurasi lebih lanjut dengan parameter berikut:

*   **`initialDelaySeconds`:** Berapa detik Kubelet harus menunggu *setelah kontainer dimulai* sebelum melakukan probe pertama. Berguna untuk memberi waktu aplikasi memulai. Default: 0.
*   **`periodSeconds`:** Seberapa sering (dalam detik) Kubelet harus melakukan probe. Default: 10. Minimum: 1.
*   **`timeoutSeconds`:** Berapa detik Kubelet harus menunggu respons probe sebelum menganggapnya gagal (timeout). Default: 1. Minimum: 1.
*   **`successThreshold`:** Jumlah minimum keberhasilan berturut-turut agar probe dianggap berhasil setelah sebelumnya gagal. Default: 1. Harus 1 untuk Liveness dan Startup Probes.
*   **`failureThreshold`:** Jumlah minimum kegagalan berturut-turut agar probe dianggap gagal. Setelah gagal, Kubelet akan mengambil tindakan (restart untuk Liveness/Startup, hapus endpoint untuk Readiness). Default: 3. Minimum: 1.
*   **`terminationGracePeriodSeconds` (Pada Pod Spec):** Meskipun bukan bagian dari probe, ini penting. Ketika Pod dihentikan (misalnya karena Liveness Probe gagal atau saat update), Kubelet mengirim sinyal SIGTERM ke proses utama kontainer dan menunggu selama durasi ini sebelum mengirim SIGKILL (paksa berhenti). Pastikan aplikasi Anda menangani SIGTERM untuk graceful shutdown. Probe tidak akan dijalankan selama periode ini.

## Praktik Terbaik

*   **Gunakan Readiness Probe:** Hampir selalu gunakan `readinessProbe` untuk kontainer yang melayani traffic untuk memastikan zero-downtime updates.
*   **Implementasikan Endpoint Kesehatan:** Buat endpoint HTTP ringan (misalnya, `/healthz`, `/ready`) di aplikasi Anda yang dapat digunakan oleh probe `httpGet`. Endpoint ini harus cepat dan tidak membebani.
    *   `/healthz` (Liveness): Hanya memeriksa apakah proses masih berjalan dan tidak deadlock.
    *   `/ready` (Readiness): Memeriksa apakah *semua* dependensi siap dan aplikasi siap melayani traffic.
*   **Hati-hati dengan Liveness Probe:** Liveness probe yang terlalu agresif atau memeriksa dependensi eksternal dapat menyebabkan restart kontainer yang tidak perlu. Fokuskan pada kesehatan internal proses itu sendiri.
*   **Gunakan Startup Probe untuk Aplikasi Lambat:** Jika aplikasi Anda butuh waktu lama untuk start, gunakan `startupProbe` untuk mencegah Liveness/Readiness membunuhnya terlalu dini.
*   **Sesuaikan Parameter Probe:** Jangan hanya menggunakan default. Sesuaikan `initialDelaySeconds`, `periodSeconds`, `timeoutSeconds`, dan `failureThreshold` sesuai dengan karakteristik dan kebutuhan aplikasi Anda.

Probes adalah mekanisme vital di Kubernetes untuk membangun aplikasi yang tangguh dan andal dengan memastikan hanya instance yang sehat dan siap yang menerima traffic, dan instance yang macet dapat di-restart secara otomatis.
