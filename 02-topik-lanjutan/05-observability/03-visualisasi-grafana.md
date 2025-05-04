# Visualisasi Metrik dengan Grafana

Setelah Anda berhasil mengumpulkan metrik historis menggunakan sistem monitoring seperti Prometheus, langkah selanjutnya adalah **memvisualisasikan** data tersebut agar mudah dipahami, dianalisis, dan digunakan untuk membuat keputusan operasional. Di sinilah **Grafana** berperan.

## Apa itu Grafana?

Grafana adalah **platform analitik dan visualisasi interaktif open-source** terkemuka. Ini memungkinkan Anda untuk:

*   **Membuat Kueri (Query):** Terhubung ke berbagai sumber data (Data Sources) yang berbeda.
*   **Memvisualisasikan (Visualize):** Menampilkan data metrik dalam berbagai format grafik, tabel, pengukur (gauge), heatmap, dll.
*   **Membuat Dashboard:** Menggabungkan beberapa visualisasi (panel) ke dalam dashboard yang kohesif dan dapat disesuaikan untuk memantau sistem atau aplikasi tertentu.
*   **Memberi Peringatan (Alerting):** Grafana juga memiliki mesin alerting bawaan (meskipun Alertmanager Prometheus seringkali lebih disukai untuk alerting berbasis metrik Prometheus).
*   **Berbagi Dashboard:** Mudah berbagi dashboard dengan tim atau pemangku kepentingan lainnya.

## Grafana & Prometheus: Pasangan Sempurna

Meskipun Grafana mendukung banyak sumber data (InfluxDB, Elasticsearch, MySQL, PostgreSQL, AWS CloudWatch, Azure Monitor, dll.), kombinasi **Prometheus sebagai sumber data** dan **Grafana sebagai alat visualisasi** adalah pasangan yang sangat umum dan kuat di ekosistem cloud-native dan Kubernetes.

*   Grafana memiliki dukungan bawaan yang sangat baik untuk Prometheus sebagai sumber data.
*   Grafana memahami dan memungkinkan Anda menulis kueri **PromQL** langsung di dalam editor panelnya.
*   Banyak **dashboard Grafana pra-bangun (pre-built)** tersedia untuk memvisualisasikan metrik dari exporter umum seperti `node-exporter`, `kube-state-metrics`, dan komponen Kubernetes lainnya, yang dapat Anda impor dan gunakan dengan cepat.

## Komponen Utama Grafana

*   **Data Sources:** Konfigurasi koneksi ke sistem backend tempat data Anda disimpan (misalnya, URL server Prometheus Anda).
*   **Dashboards:** Kumpulan dari satu atau lebih **Panel** yang diatur dalam **Rows**.
*   **Panels:** Unit visualisasi individual (grafik garis, batang, tabel, pengukur, teks, dll.). Setiap panel biasanya terikat pada satu atau lebih kueri ke sumber data.
*   **Queries:** Permintaan yang dikirim ke sumber data untuk mengambil data yang akan divisualisasikan (misalnya, kueri PromQL).
*   **Variables:** Memungkinkan pembuatan dashboard yang dinamis dan interaktif. Anda dapat mendefinisikan variabel (misalnya, memilih namespace, Pod, atau interval waktu) yang dapat digunakan dalam kueri panel, memungkinkan pengguna memfilter atau mengubah data yang ditampilkan tanpa mengedit dashboard.
*   **Alerting:** Memungkinkan definisi aturan alert berdasarkan hasil kueri panel.
*   **Plugins:** Memperluas fungsionalitas Grafana dengan menambahkan tipe panel baru, sumber data baru, atau aplikasi.

## Menjalankan Grafana di Kubernetes

Sama seperti Prometheus, cara paling umum untuk men-deploy Grafana di Kubernetes adalah:

*   **Bagian dari Stack Monitoring (Helm):** Jika Anda menginstal `kube-prometheus-stack` Helm chart, Grafana biasanya sudah termasuk di dalamnya, sudah dikonfigurasi sebelumnya dengan Prometheus sebagai sumber data dan beberapa dashboard bawaan untuk Kubernetes. Ini adalah cara termudah untuk memulai.
*   **Helm Chart Grafana Terpisah:** Jika Anda hanya membutuhkan Grafana atau ingin mengelolanya secara terpisah, gunakan [Helm chart Grafana resmi](https://github.com/grafana/helm-charts). Anda perlu mengkonfigurasi sumber data Prometheus secara manual setelah instalasi.
*   **Manifest YAML:** Anda juga dapat men-deploy Grafana menggunakan objek Deployment dan Service standar, mengkonfigurasi penyimpanan persisten untuk dashboard dan pengaturannya (jika diperlukan).

**Mengakses UI Grafana:**
Setelah terinstal, Grafana biasanya diekspos melalui `Service` Kubernetes. Anda mungkin perlu menggunakan `kubectl port-forward` atau mengkonfigurasi `Ingress` untuk mengakses UI web Grafana dari browser Anda. Kredensial login default seringkali `admin`/`prom-operator` atau `admin`/`admin` (segera ganti setelah login pertama!).

```bash
# Contoh port-forward jika Grafana diinstal oleh kube-prometheus-stack di namespace 'monitoring'
kubectl port-forward svc/my-prom-stack-grafana 3000:80 -n monitoring
# Akses di browser: http://localhost:3000
```

## Membuat Dashboard Kubernetes Dasar

Meskipun banyak dashboard bagus yang bisa diimpor, memahami cara membuat panel dasar itu berguna:

1.  **Login ke Grafana.**
2.  **Konfigurasi Data Source:** Pastikan sumber data Prometheus Anda sudah ditambahkan dan berfungsi (biasanya otomatis jika menggunakan `kube-prometheus-stack`).
3.  **Buat Dashboard Baru:** Klik ikon '+' -> Dashboard -> Add new panel.
4.  **Pilih Data Source:** Pilih sumber data Prometheus Anda.
5.  **Tulis Kueri PromQL:** Di editor kueri, masukkan kueri PromQL untuk metrik yang ingin Anda visualisasikan. Contoh:
    *   Penggunaan CPU Cluster: `sum(rate(container_cpu_usage_seconds_total{id="/"}[5m]))`
    *   Penggunaan Memori Node (persen): `100 * (node_memory_MemTotal_bytes - node_memory_MemAvailable_bytes) / node_memory_MemTotal_bytes`
    *   Jumlah Pod Ready per Namespace: `sum(kube_pod_status_ready{condition="true"}) by (namespace)`
6.  **Format Legenda:** Gunakan label dari kueri PromQL untuk membuat legenda yang informatif (misalnya, `{{namespace}}` atau `{{pod}}`).
7.  **Pilih Tipe Visualisasi:** Pilih tipe grafik yang sesuai (Time series, Stat, Gauge, Table, dll.) dari menu visualisasi.
8.  **Kustomisasi Panel:** Atur judul panel, unit sumbu (misalnya, 'cores', 'bytes', 'percent'), ambang batas warna, dll.
9.  **Simpan Panel & Dashboard:** Simpan panel dan beri nama dashboard Anda.

**Mengimpor Dashboard Pra-Bangun:**
*   Cari dashboard di [Grafana Labs Dashboards](https://grafana.com/grafana/dashboards/). Banyak dashboard bagus untuk Node Exporter, Kubernetes, dll.
*   Salin ID Dashboard atau URL JSON-nya.
*   Di Grafana, klik ikon '+' -> Import. Tempel ID/URL atau unggah file JSON.
*   Pilih sumber data Prometheus Anda saat diminta.
*   Dashboard akan dibuat secara otomatis.

## Menggunakan Variabel Dashboard

Variabel membuat dashboard Anda interaktif.

1.  Buka Pengaturan Dashboard (ikon roda gigi) -> Variables -> Add variable.
2.  **Nama:** Nama variabel (misalnya, `namespace`, `pod`).
3.  **Tipe:** Biasanya `Query`.
4.  **Data source:** Pilih Prometheus.
5.  **Query:** Kueri PromQL untuk mendapatkan daftar nilai variabel. Contoh:
    *   Untuk daftar namespace: `label_values(kube_pod_info, namespace)`
    *   Untuk daftar Pod di namespace terpilih: `label_values(kube_pod_info{namespace="$namespace"}, pod)` (menggunakan variabel `$namespace`).
6.  **Aktifkan "Multi-value" / "Include All option"** jika diinginkan.
7.  Simpan variabel.
8.  **Gunakan Variabel dalam Kueri Panel:** Ganti nilai hardcoded dalam kueri PromQL Anda dengan variabel (misalnya, `sum(rate(container_cpu_usage_seconds_total{namespace="$namespace", pod=~"$pod"}[5m])) by (pod)`).

Sekarang pengguna dapat memilih namespace atau Pod dari dropdown di bagian atas dashboard untuk memfilter data yang ditampilkan.

Grafana adalah alat visualisasi yang sangat kuat dan fleksibel. Menguasainya memungkinkan Anda mengubah data metrik mentah dari Prometheus menjadi wawasan operasional yang dapat ditindaklanjuti untuk memahami dan mengelola cluster Kubernetes Anda secara efektif.
