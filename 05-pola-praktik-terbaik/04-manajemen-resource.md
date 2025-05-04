# Praktik Terbaik: Manajemen Sumber Daya (CPU & Memori)

Manajemen sumber daya komputasi (CPU dan Memori) adalah aspek krusial dalam menjalankan aplikasi secara efisien dan stabil di Kubernetes. Kegagalan dalam mengelola resource dapat menyebabkan:

*   **Penjadwalan yang Tidak Efisien:** Pods mungkin ditempatkan di Node yang tidak memiliki cukup resource.
*   **Performa Buruk:** Aplikasi mungkin tidak mendapatkan cukup CPU atau Memori yang dibutuhkannya.
*   **Ketidakstabilan Node:** Pods yang menggunakan resource berlebihan dapat membuat Node tidak stabil atau crash (terutama karena kehabisan memori - Out Of Memory / OOM).
*   **Pemborosan Sumber Daya:** Mengalokasikan resource lebih banyak dari yang dibutuhkan menyebabkan biaya infrastruktur yang tidak perlu.

Berikut adalah praktik terbaik untuk manajemen resource di Kubernetes:

**1. *Selalu* Tentukan `requests` dan `limits` untuk Setiap Kontainer**
   Ini adalah praktik terbaik **paling fundamental**. Di dalam `spec.containers[]` pada definisi Pod (atau template Deployment/StatefulSet/dll.), tentukan:

   *   **`resources.requests`:**
        *   `cpu`: Jumlah minimum CPU yang *dijamin* akan diterima oleh kontainer. Scheduler Kubernetes **hanya** akan menempatkan Pod di Node yang memiliki kapasitas CPU *tersedia* (kapasitas node - total request CPU Pods lain) setidaknya sebesar nilai `requests.cpu` ini. Dinyatakan dalam unit [CPU Kubernetes](https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/#meaning-of-cpu) (misalnya, `100m` untuk 0.1 core, `0.5` untuk setengah core, `1` untuk 1 core).
        *   `memory`: Jumlah minimum Memori yang *dijamin* untuk kontainer. Scheduler hanya akan menempatkan Pod di Node dengan memori tersisa setidaknya sebesar nilai ini. Dinyatakan dalam [byte](https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/#meaning-of-memory) (misalnya, `64Mi` untuk Mebibytes, `1Gi` untuk Gibibytes).
   *   **`resources.limits`:**
        *   `cpu`: Batas *maksimum* CPU yang boleh digunakan kontainer. Jika kontainer mencoba menggunakan lebih banyak, CPU-nya akan di-**throttle** (dibatasi).
        *   `memory`: Batas *maksimum* Memori yang boleh digunakan kontainer. Jika kontainer mencoba menggunakan lebih banyak, prosesnya kemungkinan besar akan **dihentikan (OOMKilled)** oleh Kubelet/Kernel.

   ```yaml
   spec:
     containers:
     - name: my-app
       image: my-image
       resources:
         requests:
           memory: "128Mi"
           cpu: "250m" # 0.25 core
         limits:
           memory: "512Mi"
           cpu: "1" # 1 core
   ```

**2. Pahami dan Manfaatkan Kelas Quality of Service (QoS)**
   Kubernetes mengklasifikasikan Pods ke dalam tiga kelas QoS berdasarkan `requests` dan `limits` yang ditentukan untuk *semua* kontainer di dalamnya. Kelas QoS mempengaruhi bagaimana Scheduler memprioritaskan Pod dan bagaimana Kubelet menangani Pod saat terjadi tekanan resource (terutama OOMKilling).

   *   **`Guaranteed`:**
        *   **Kondisi:** *Setiap* kontainer dalam Pod harus memiliki `limits` CPU dan Memori, dan `requests` harus **sama persis** dengan `limits` untuk *kedua* resource (CPU dan Memori).
        *   **Perilaku:** Pods ini mendapatkan jaminan resource tertinggi. Mereka adalah yang **paling terakhir** dipertimbangkan untuk di-OOMKill jika Node kehabisan memori. Penjadwalannya juga paling ketat.
        *   **Gunakan untuk:** Beban kerja paling kritis yang membutuhkan performa dan ketersediaan terjamin (misalnya, database penting, komponen control plane).
   *   **`Burstable`:**
        *   **Kondisi:** Setidaknya satu kontainer dalam Pod memiliki `requests` CPU atau Memori, tetapi tidak semua kontainer memenuhi kriteria `Guaranteed` (misalnya, `requests` < `limits`, atau hanya `requests` yang ditentukan, atau hanya beberapa kontainer yang punya requests/limits).
        *   **Perilaku:** Mendapatkan jaminan resource sesuai `requests`. Dapat menggunakan lebih banyak resource hingga `limits` jika tersedia di Node (bursting). Jika terjadi tekanan memori, Pods `Burstable` akan di-OOMKill *setelah* Pods `BestEffort` tetapi *sebelum* Pods `Guaranteed`.
        *   **Gunakan untuk:** Sebagian besar beban kerja umum (aplikasi web, API). Ini adalah kelas QoS yang paling umum.
   *   **`BestEffort`:**
        *   **Kondisi:** *Tidak ada* kontainer dalam Pod yang menentukan `requests` atau `limits` untuk CPU atau Memori.
        *   **Perilaku:** Tidak ada jaminan resource. Pods dapat menggunakan resource apa pun yang tersisa di Node. Mereka adalah yang **pertama** di-OOMKill jika Node kehabisan memori. Penjadwalannya paling fleksibel tetapi performanya paling tidak dapat diprediksi.
        *   **Gunakan untuk:** Beban kerja prioritas rendah, tugas batch yang bisa ditoleransi jika gagal, atau saat pengembangan awal (meskipun sebaiknya segera beralih ke Burstable/Guaranteed). **Hindari di produksi untuk layanan penting.**

**3. Tetapkan Nilai Request dan Limit yang Masuk Akal**
   *   **Request Awal:** Mulailah dengan perkiraan berdasarkan pengujian lokal atau pengalaman sebelumnya. Jangan terlalu rendah (risiko performa buruk) atau terlalu tinggi (pemborosan resource, penjadwalan sulit).
   *   **Limit Awal:** Seringkali, limit bisa ditetapkan sedikit lebih tinggi dari request (misalnya, 2x hingga 4x) untuk memungkinkan bursting sementara, terutama untuk CPU. Untuk memori, limit yang terlalu tinggi meningkatkan risiko OOMKill pada Pod lain atau ketidakstabilan Node jika banyak Pod mencoba burst sekaligus. Limit memori yang terlalu dekat dengan request mungkin menyebabkan OOMKill pada aplikasi Anda jika terjadi lonjakan sesaat.
   *   **Observasi dan Tuning:** **Langkah paling penting!** Gunakan alat monitoring (Prometheus, Grafana, `kubectl top`) untuk mengamati penggunaan resource *aktual* aplikasi Anda di bawah beban kerja nyata. Sesuaikan `requests` dan `limits` secara berkala berdasarkan data observasi ini.
        *   Jika penggunaan aktual secara konsisten jauh di bawah `requests`, Anda mungkin bisa menurunkannya.
        *   Jika penggunaan aktual sering mendekati atau melebihi `limits` (menyebabkan throttling CPU atau OOMKills), Anda perlu meningkatkannya (atau mengoptimalkan aplikasi).
        *   Idealnya, `requests` harus mendekati penggunaan rata-rata atau persentil yang lebih tinggi (misalnya, P95) untuk memastikan performa yang stabil.

**4. Gunakan LimitRanges untuk Menetapkan Default dan Batasan**
   *   Seperti dibahas sebelumnya, gunakan `LimitRange` di setiap namespace untuk:
        *   Menetapkan `defaultRequest` dan `default` untuk kontainer yang tidak menentukannya (memastikan tidak ada Pod `BestEffort` yang tidak disengaja dan kompatibilitas dengan ResourceQuota).
        *   Menetapkan batas `min` dan `max` untuk mencegah pengguna meminta resource yang tidak realistis.
        *   Membatasi rasio `limit`/`request`.

**5. Gunakan ResourceQuotas untuk Mengontrol Penggunaan Namespace**
   *   Gunakan `ResourceQuota` untuk membatasi *total* `requests` dan `limits` (serta jumlah objek) yang dapat dikonsumsi oleh satu namespace, mencegah satu tim/aplikasi memonopoli cluster.

**6. Pertimbangkan Vertical Pod Autoscaler (VPA) - (Lebih Lanjut)**
   *   VPA adalah komponen Kubernetes (perlu diinstal terpisah) yang dapat secara otomatis menyesuaikan `requests` CPU dan Memori untuk kontainer berdasarkan observasi penggunaan historis. Ini dapat membantu menjaga nilai request tetap optimal.
   *   VPA dapat berjalan dalam mode `Off` (hanya rekomendasi), `Initial` (set request saat Pod dibuat), atau `Auto`/`Recreate` (memperbarui request dan me-restart Pod).
   *   VPA **tidak dapat** digunakan bersamaan dengan Horizontal Pod Autoscaler (HPA) pada metrik yang sama (CPU/Memori).

Manajemen sumber daya yang efektif adalah kunci untuk menjalankan cluster Kubernetes yang stabil, berperforma baik, dan hemat biaya. Menentukan `requests` dan `limits` secara konsisten, memahami QoS, mengamati penggunaan aktual, dan menggunakan LimitRanges serta ResourceQuotas adalah praktik fundamental yang harus diterapkan.
