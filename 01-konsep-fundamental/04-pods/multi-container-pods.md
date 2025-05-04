# Pola Multi-Container Pods: Sidecars, Adapters, Ambassadors

Meskipun pola paling umum di Kubernetes adalah menjalankan **satu kontainer utama per Pod**, desain Pod secara eksplisit memungkinkan Anda menjalankan **beberapa kontainer** yang sangat erat terkait dalam satu Pod yang sama. Kontainer-kontainer ini berjalan bersama di Node yang sama dan berbagi sumber daya penting seperti namespace jaringan dan volume penyimpanan.

Pola multi-container ini sangat berguna untuk memisahkan tugas-tugas pendukung dari logika aplikasi utama, menjaga kontainer utama tetap fokus dan ramping. Ada beberapa pola desain umum untuk multi-container Pods:

## 1. Pola Sidecar

Ini adalah pola multi-container yang paling umum. **Sidecar** adalah kontainer tambahan yang berjalan di samping kontainer aplikasi utama untuk menyediakan fungsionalitas pendukung atau tambahan.

*   **Tujuan:** Memperluas atau meningkatkan kemampuan kontainer utama tanpa perlu mengubah kode aplikasi utama atau menggembungkan image-nya.
*   **Cara Kerja:** Sidecar biasanya berbagi sumber daya dengan kontainer utama, seperti:
    *   **Volume:** Sidecar dapat membaca log yang ditulis oleh kontainer utama ke volume bersama, atau menyediakan data konfigurasi ke kontainer utama melalui volume.
    *   **Jaringan:** Sidecar dapat bertindak sebagai proxy jaringan untuk kontainer utama (berkomunikasi via `localhost`), mencegat atau memodifikasi lalu lintas masuk/keluar.
*   **Contoh Umum Sidecar:**
    *   **Agen Logging:** Kontainer seperti Fluentd, Fluent Bit, atau Promtail yang membaca file log dari volume bersama (yang ditulis oleh kontainer utama) dan mengirimkannya ke sistem logging terpusat.
    *   **Agen Monitoring/Metrics:** Kontainer yang mengumpulkan metrik dari aplikasi utama (misalnya, melalui endpoint `/metrics` di `localhost`) atau dari sistem (seperti cAdvisor) dan mengeksposnya untuk di-scrape oleh Prometheus.
    *   **Proxy Service Mesh:** Kontainer seperti Envoy (untuk Istio) atau linkerd-proxy (untuk Linkerd) yang mencegat semua lalu lintas jaringan masuk dan keluar dari kontainer utama untuk menyediakan fitur seperti mTLS, observability, dan kontrol lalu lintas.
    *   **Penyinkron Konfigurasi/Data:** Kontainer yang secara berkala menarik konfigurasi atau data terbaru dari sumber eksternal (misalnya, Git repo, Consul, Vault) dan menyediakannya ke kontainer utama melalui volume bersama.
    *   **Web Server/Proxy Statis:** Kontainer Nginx atau web server lain yang menyajikan file statis dari volume bersama yang mungkin dihasilkan atau diperbarui oleh kontainer utama.

**Diagram Sidecar (Contoh Logging):**

```
+------------------------- POD -------------------------+
|                                                         |
|  +---------------------+   +------------------------+  |
|  |   Aplikasi Utama    |<--|    Volume Bersama      |  |
|  |   (Menulis log      |   |    (/var/log/app)      |  |
|  |    ke /var/log/app) |-->|                        |  |
|  +---------------------+   +-----------+------------+  |
|        |                                |              |
|        |                                |              |
|        |                                v              |
|        |                      +---------------------+ |
|        |                      |   Sidecar Logging   | |
|        |                      |   (Membaca log,     | |
|        |                      |    mengirim ke luar)| |
|        +--------------------->|                     +------> Sistem Logging
|                               +---------------------+ |
|                                                         |
|       Namespace Jaringan & IPC Bersama (localhost)      |
+---------------------------------------------------------+
                IP Pod: 10.1.2.3
```

## 2. Pola Adapter

Kontainer **Adapter** bertugas **menyesuaikan atau menstandarkan** antarmuka (input atau output) dari kontainer utama agar sesuai dengan sistem atau standar eksternal.

*   **Tujuan:** Menyembunyikan kompleksitas atau ketidaksesuaian antarmuka kontainer utama dari seluruh sistem.
*   **Cara Kerja:** Adapter dapat menerima data dari kontainer utama (misalnya, melalui volume atau `localhost`), mengubah formatnya, dan kemudian mengeksposnya dalam format standar, atau sebaliknya.
*   **Contoh Adapter:**
    *   Kontainer yang mengambil log dalam format non-standar dari aplikasi utama, mengubahnya menjadi format JSON standar, dan menyediakannya untuk dibaca oleh sidecar logging generik.
    *   Kontainer yang mengekspos metrik aplikasi utama (yang mungkin dalam format kustom) dalam format standar Prometheus melalui endpoint `/metrics`.
    *   Kontainer yang menyediakan API RESTful yang lebih sederhana di depan aplikasi utama yang mungkin memiliki API RPC yang kompleks.

## 3. Pola Ambassador

Kontainer **Ambassador** bertindak sebagai **proxy lokal** yang menyederhanakan cara kontainer utama **berkomunikasi dengan dunia luar** (layanan eksternal atau Pod lain).

*   **Tujuan:** Menyembunyikan detail koneksi jaringan, penemuan layanan, atau logika percobaan ulang/circuit breaking dari aplikasi utama.
*   **Cara Kerja:** Kontainer utama berkomunikasi dengan Ambassador (biasanya via `localhost`). Ambassador kemudian menangani logika untuk menemukan layanan target yang sebenarnya, membuka koneksi, menangani kegagalan sementara, dan mungkin melakukan load balancing sederhana.
*   **Contoh Ambassador:**
    *   Proxy yang terhubung ke replika set database (misalnya, master/slave atau sharded), menyajikan satu endpoint `localhost` ke aplikasi utama, dan secara otomatis mengarahkan kueri baca/tulis ke node database yang sesuai.
    *   Proxy yang menangani koneksi ke layanan eksternal dengan logika retry atau circuit breaking bawaan, sehingga aplikasi utama tidak perlu mengimplementasikannya.
    *   Proxy sederhana yang mengelola koneksi pool ke layanan lain.

**Kapan Memilih Pola yang Tepat?**

*   **Sidecar:** Jika Anda ingin *menambah* fungsionalitas (logging, monitoring, keamanan) tanpa mengubah aplikasi utama.
*   **Adapter:** Jika Anda perlu *mengubah format atau antarmuka* input/output aplikasi utama.
*   **Ambassador:** Jika Anda ingin *menyederhanakan atau mengelola interaksi jaringan keluar* dari aplikasi utama.

## Pertimbangan Penting

*   **Kompleksitas:** Menambahkan lebih banyak kontainer ke Pod meningkatkan kompleksitas definisi Pod dan potensi titik kegagalan.
*   **Resource Overhead:** Setiap kontainer tambahan mengkonsumsi resource (CPU, Memori). Pastikan untuk mengatur `requests` dan `limits` dengan benar untuk semua kontainer.
*   **Tight Coupling:** Kontainer dalam satu Pod sangat erat terkait. Jika satu kontainer membutuhkan versi library yang berbeda dari yang lain, itu bisa menjadi masalah. Mereka juga berbagi nasib; jika Pod dijadwalkan ulang, semua kontainer pindah bersama.
*   **Urutan Startup:** Gunakan [Init Containers](./init-containers.md) jika Anda memerlukan urutan startup yang terjamin antar kontainer. Kontainer aplikasi utama dan sidecar biasanya dimulai secara paralel.

Pola multi-container adalah alat yang ampuh dalam arsitektur Kubernetes untuk membangun aplikasi yang modular dan dapat dikelola, tetapi gunakanlah dengan bijak ketika kontainer-kontainer tersebut benar-benar perlu berjalan bersama dan berbagi sumber daya secara erat.
