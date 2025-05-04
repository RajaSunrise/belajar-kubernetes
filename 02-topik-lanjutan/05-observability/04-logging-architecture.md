# Arsitektur Logging di Kubernetes

Selain metrik, **log** adalah pilar penting kedua dari observability. Log memberikan catatan peristiwa terperinci dari aplikasi dan komponen sistem, yang sangat berharga untuk:

*   **Debugging:** Memahami apa yang salah ketika terjadi error atau perilaku tak terduga.
*   **Auditing:** Melacak siapa melakukan apa dan kapan.
*   **Analisis Perilaku:** Memahami bagaimana pengguna atau sistem berinteraksi dengan aplikasi.

Namun, mengelola log di lingkungan yang dinamis seperti Kubernetes, di mana Pods (dan kontainer di dalamnya) terus-menerus dibuat dan dihancurkan, memiliki tantangan tersendiri. Kita memerlukan pendekatan **logging terpusat**.

## Masalah Logging di Lingkungan Kontainer

*   **Siklus Hidup Fana:** Log yang ditulis ke filesystem kontainer akan hilang saat kontainer (atau Pod) dihapus.
*   **Akses Terdistribusi:** Log tersebar di banyak Node dan Pods. Mengakses log secara manual (`kubectl logs`) tidak praktis untuk analisis atau pemantauan jangka panjang.
*   **Volume Besar:** Aplikasi terdistribusi dapat menghasilkan volume log yang sangat besar.

## Pola Logging Standar Kubernetes: Logging ke `stdout`/`stderr`

Praktik terbaik dan paling umum untuk logging aplikasi di Kubernetes adalah mengkonfigurasi aplikasi Anda untuk menulis lognya ke **standard output (`stdout`)** dan **standard error (`stderr`)**, bukan ke file di dalam kontainer.

**Mengapa?**

*   **Penangkapan Otomatis:** Container Runtime (Docker, containerd) secara otomatis menangkap aliran `stdout` dan `stderr` dari setiap kontainer.
*   **Akses via `kubectl logs`:** Kubernetes API (melalui Kubelet) dapat mengakses log yang ditangkap oleh container runtime ini, memungkinkan Anda melihatnya menggunakan perintah `kubectl logs <pod-name> [-c <container-name>]`.
*   **Integrasi dengan Backend Logging:** Mekanisme ini menjadi dasar bagi sebagian besar arsitektur logging terpusat.

## Arsitektur Logging Terpusat Umum

Tujuannya adalah mengumpulkan log dari semua Pods di semua Node dan mengirimkannya ke **backend logging terpusat** untuk penyimpanan, pencarian, dan analisis jangka panjang. Arsitektur paling umum melibatkan **agen logging level Node**.

**Komponen Utama:**

1.  **Aplikasi:** Menulis log ke `stdout`/`stderr`.
2.  **Container Runtime:** Menangkap `stdout`/`stderr` dan biasanya menyimpannya sementara ke file di Node host (misalnya, dalam format JSON di direktori seperti `/var/log/pods/` atau `/var/log/containers/`). Lokasi dan format dapat bervariasi.
3.  **Agen Logging (Node Agent):** Ini adalah **komponen kunci**. Sebuah agen logging (seperti Fluentd, Fluent Bit, Promtail, Logstash, Vector) di-deploy sebagai **`DaemonSet`**, yang berarti satu Pod agen berjalan di *setiap* Node di cluster. Tugas agen ini adalah:
    *   Menemukan file log kontainer di Node host.
    *   Membaca (tailing) log baru saat ditulis.
    *   **Parsing (Opsional tapi Penting):** Mengurai struktur log (misalnya, JSON, regex) untuk mengekstrak bidang data yang bermakna.
    *   **Enrichment (Opsional tapi Penting):** Menambahkan metadata Kubernetes yang relevan ke setiap entri log (seperti nama Pod, namespace, label Pod, nama kontainer, ID kontainer). Ini sangat penting untuk memfilter dan mengkorelasikan log nantinya. Agen biasanya mendapatkan metadata ini dengan berkomunikasi dengan API Server atau Kubelet.
    *   **Buffering:** Menyimpan log sementara jika backend tidak tersedia.
    *   **Forwarding:** Mengirim log yang telah diproses ke backend logging terpusat.
4.  **Backend Logging Terpusat:** Sistem penyimpanan dan analisis yang dirancang untuk menangani volume log yang besar. Pilihan populer:
    *   **Elasticsearch:** Mesin pencari dan analitik open-source yang sangat kuat dan populer untuk log. Menyediakan pencarian teks lengkap yang cepat dan kemampuan agregasi.
    *   **Loki:** Proyek open-source dari Grafana Labs yang terinspirasi oleh Prometheus. Fokus pada *indeksasi label* (seperti namespace, app, pod) daripada indeks teks lengkap dari konten log. Ini membuatnya lebih hemat sumber daya penyimpanan dan biaya, tetapi mungkin kurang fleksibel untuk pencarian teks bebas yang kompleks.
    *   Layanan Cloud (AWS CloudWatch Logs, Google Cloud Logging, Azure Monitor Logs).
    *   Splunk, Datadog Logs, Logz.io, dll.
5.  **Antarmuka Pengguna (UI) / Visualisasi:** Alat untuk mencari, memfilter, memvisualisasikan, dan menganalisis log di backend.
    *   **Kibana:** UI standar untuk Elasticsearch.
    *   **Grafana:** UI standar untuk Loki (dan juga dapat terhubung ke Elasticsearch dan sumber lain).
    *   UI yang disediakan oleh layanan cloud atau vendor lainnya.

**Stack Populer:**

*   **EFK:** Elasticsearch, Fluentd (atau Fluent Bit), Kibana. Stack logging open-source klasik dan sangat matang. Fluentd kaya fitur tetapi bisa memakan resource lebih banyak; Fluent Bit lebih ringan.
*   **PLG:** Promtail, Loki, Grafana. Stack modern yang lebih ringan, fokus pada indeksasi label, integrasi erat dengan Prometheus/Grafana. Promtail adalah agen logging khusus untuk Loki.

**Diagram Alur Sederhana (Node Agent):**

```
[App in Pod] -> stdout/stderr -> [Container Runtime] -> [Log File on Node (/var/log/pods/...)]
      ^                                                                     |
      |                                                                     | (Reads)
      +---------------------------------------------------------------------+
                                                                            |
     [Logging Agent DaemonSet (Fluentd/Fluent Bit/Promtail) on Node] <-----> [K8s API (Metadata)]
      | (Parse, Enrich, Buffer)
      | (Forwards)
      V
[Centralized Logging Backend (Elasticsearch/Loki/Cloud)] <--- [UI (Kibana/Grafana)]
```

## Alternatif: Pola Sidecar Logging

Dalam beberapa kasus, Anda mungkin ingin menggunakan pola sidecar:

*   **Deskripsi:** Anda men-deploy kontainer agen logging sebagai *sidecar* di dalam Pod yang sama dengan kontainer aplikasi Anda.
*   **Cara Kerja:** Aplikasi mungkin menulis log ke file dalam volume `emptyDir` yang dibagi antara kontainer aplikasi dan kontainer sidecar. Sidecar kemudian membaca file log ini, memprosesnya, dan mengirimkannya ke backend.
*   **Kelebihan:** Isolasi (masalah agen tidak mempengaruhi Pod lain), fleksibilitas (bisa menggunakan agen berbeda per aplikasi).
*   **Kekurangan:** Overhead resource lebih tinggi (satu agen per Pod vs satu per Node), konfigurasi lebih kompleks (perlu menambahkan sidecar ke setiap definisi Pod), tidak menangkap log `stdout`/`stderr` kontainer aplikasi secara langsung (kecuali jika diarahkan ke file).
*   **Penggunaan:** Lebih jarang digunakan untuk logging umum, terkadang digunakan untuk kasus khusus di mana aplikasi tidak dapat dengan mudah menulis ke `stdout`/`stderr` atau memerlukan pemrosesan log yang sangat spesifik sebelum dikirim.

## Praktik Terbaik Logging

*   **Log ke `stdout`/`stderr`:** Jadikan ini standar untuk aplikasi Anda.
*   **Gunakan Format Terstruktur (JSON):** Jika memungkinkan, buat aplikasi Anda menghasilkan log dalam format JSON. Ini membuat parsing oleh agen logging jauh lebih mudah dan andal daripada menggunakan regex pada teks biasa. Sertakan konteks penting (seperti ID request) dalam log terstruktur.
*   **Deploy Agen Logging sebagai DaemonSet:** Ini adalah pendekatan paling efisien dan umum.
*   **Enrich Log dengan Metadata K8s:** Pastikan agen logging Anda menambahkan label Pod, namespace, nama kontainer, dll. Ini krusial untuk analisis.
*   **Pilih Backend yang Sesuai:** Pertimbangkan volume log, kebutuhan retensi, kompleksitas kueri, dan biaya saat memilih backend (Elasticsearch vs Loki vs Cloud).
*   **Konfigurasi Parsing & Filtering di Agen:** Lakukan parsing dan filtering awal di agen (jika perlu) untuk mengurangi beban pada backend dan menghemat biaya penyimpanan/indeksasi.
*   **Monitor Agen Logging Itu Sendiri:** Pastikan agen logging Anda berjalan dengan baik dan tidak kehilangan log.

Logging terpusat adalah komponen vital untuk memahami dan memecahkan masalah sistem terdistribusi seperti Kubernetes. Dengan mengadopsi pola standar dan memilih arsitektur yang tepat, Anda dapat memperoleh wawasan berharga dari log aplikasi dan sistem Anda.
