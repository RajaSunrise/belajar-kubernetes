# Pengenalan Distributed Tracing (Pelacakan Terdistribusi)

Dalam arsitektur microservices, satu permintaan pengguna seringkali melibatkan pemanggilan berantai ke beberapa layanan backend yang berbeda. Misalnya, permintaan ke API gateway mungkin memicu panggilan ke layanan autentikasi, layanan profil pengguna, dan layanan rekomendasi, yang masing-masing mungkin memanggil database atau layanan lainnya.

**Masalah:** Ketika terjadi masalah performa (latensi tinggi) atau error dalam alur permintaan yang kompleks ini, sangat sulit untuk menentukan:

*   Layanan mana yang menyebabkan bottleneck?
*   Layanan mana yang menghasilkan error?
*   Bagaimana alur permintaan sebenarnya mengalir melalui sistem?
*   Berapa lama waktu yang dihabiskan di setiap layanan dan dalam komunikasi jaringan antar layanan?

Metrik dan Log memberikan gambaran agregat atau peristiwa individual, tetapi sulit untuk melihat **gambaran keseluruhan dari satu permintaan tunggal** saat melintasi banyak layanan. Di sinilah **Distributed Tracing (Pelacakan Terdistribusi)** sangat berharga.

## Apa itu Distributed Tracing?

Distributed Tracing adalah metode untuk **memprofil dan memantau aplikasi microservice** dengan melacak **keseluruhan siklus hidup sebuah permintaan** saat ia bergerak melalui berbagai layanan dalam sistem terdistribusi.

Ini bekerja dengan menyebarkan **informasi konteks (context propagation)** antar layanan untuk setiap permintaan, memungkinkan rekonstruksi alur panggilan lengkap.

## Konsep Inti Distributed Tracing

1.  **Trace:** Merepresentasikan **keseluruhan perjalanan** sebuah permintaan tunggal melalui sistem. Sebuah Trace terdiri dari satu atau lebih **Spans**. Setiap Trace memiliki ID unik (Trace ID).
2.  **Span:** Merepresentasikan **satu unit pekerjaan** atau operasi logis tunggal dalam Trace (misalnya, satu panggilan HTTP, satu kueri database, satu pemanggilan fungsi). Setiap Span memiliki:
    *   Nama operasi (misalnya, "HTTP GET /users", "DB SELECT").
    *   Waktu mulai (start timestamp) dan durasi.
    *   ID unik Span (Span ID).
    *   ID Trace tempat ia berada.
    *   ID Span induk (Parent Span ID), yang menunjukkan Span mana yang memicu Span ini (kecuali untuk root span).
    *   **Tags (Atribut):** Key-value pairs yang memberikan metadata tentang operasi (misalnya, URL HTTP, status code, nama query DB, versi host, region).
    *   **Logs (Events):** Timestamped event yang terjadi selama durasi Span (misalnya, log error spesifik).
    *   **Context (Baggage):** Informasi konteks (Trace ID, Span ID, dan data kustom lainnya) yang perlu disebarkan ke pemanggilan berikutnya (downstream calls).
3.  **Context Propagation:** Mekanisme **kunci** dalam tracing. Ketika layanan A memanggil layanan B:
    *   Layanan A menyuntikkan (inject) konteks tracing saat ini (minimal Trace ID dan Span ID A) ke dalam metadata permintaan (misalnya, sebagai header HTTP seperti `traceparent` dan `tracestate` dalam standar W3C Trace Context, atau header B3).
    *   Layanan B mengekstrak (extract) konteks tracing dari permintaan masuk.
    *   Layanan B membuat Span *baru* untuk pekerjaannya sendiri, menetapkan Trace ID yang sama, dan menetapkan Span ID A sebagai Parent Span ID-nya.
    *   Jika Layanan B memanggil Layanan C, ia akan menyuntikkan konteksnya sendiri (Trace ID yang sama, Span ID B).
4.  **Sampling:** Karena melacak *setiap* permintaan bisa menghasilkan overhead yang signifikan (terutama di sistem bervolume tinggi), sistem tracing seringkali melakukan **sampling**. Hanya sebagian kecil dari permintaan (misalnya, 1 dari 1000, atau berdasarkan head-based/tail-based sampling) yang akan dilacak sepenuhnya.
5.  **Backend Tracing:** Data Span yang dihasilkan oleh berbagai layanan dikirim (biasanya secara asinkron) ke **backend tracing terpusat**. Backend ini bertanggung jawab untuk:
    *   Menerima data Span (seringkali melalui agen kolektor).
    *   Menyimpan data Span.
    *   Merakit Spans menjadi Traces berdasarkan Trace ID dan hubungan Parent/Child.
    *   Menyediakan API untuk mengkueri data Trace.
    *   Menyediakan UI untuk memvisualisasikan Traces (misalnya, sebagai diagram Gantt yang menunjukkan latensi dan hubungan antar Span).

## Standar dan Alat Populer

*   **Standar:**
    *   **OpenTelemetry (OTel):** Proyek CNCF yang bertujuan menjadi standar industri *tunggal* untuk **semua** sinyal telemetri (traces, metrics, logs). Menyediakan API, SDK (untuk instrumentasi kode), dan protokol standar (OTLP - OpenTelemetry Protocol) untuk mengirim data telemetri ke berbagai backend. **Ini adalah arah masa depan dan sangat direkomendasikan.**
    *   **OpenTracing (Legacy):** Standar API sebelumnya (sekarang diarsipkan dan digabungkan ke OpenTelemetry).
    *   **OpenCensus (Legacy):** Proyek Google sebelumnya untuk tracing dan metrics (sekarang diarsipkan dan digabungkan ke OpenTelemetry).
    *   **W3C Trace Context:** Standar W3C untuk format header HTTP (`traceparent`, `tracestate`) untuk context propagation. Didukung oleh OpenTelemetry dan banyak sistem tracing.
*   **Backend Tracing Open Source:**
    *   **Jaeger:** Dikembangkan oleh Uber, sekarang proyek kelulusan CNCF. Sangat populer, kaya fitur, UI bagus.
    *   **Zipkin:** Terinspirasi oleh Google Dapper, proyek lama yang matang.
    *   **Tempo:** Backend tracing dari Grafana Labs, dirancang untuk skalabilitas masif dan integrasi erat dengan Loki, Prometheus, dan Grafana (menggunakan ID trace untuk korelasi).
*   **Backend Tracing Komersial/SaaS:** Datadog APM, Dynatrace, New Relic, Honeycomb, Lightstep, AWS X-Ray, Google Cloud Trace, Azure Application Insights.

## Implementasi di Kubernetes

1.  **Instrumentasi Aplikasi:** Ini adalah langkah **paling penting**. Kode aplikasi Anda perlu diinstrumentasi menggunakan SDK OpenTelemetry (atau SDK tracing lainnya) untuk:
    *   Memulai dan mengakhiri Spans untuk operasi penting.
    *   Menyuntikkan dan mengekstrak konteks tracing saat melakukan atau menerima panggilan jaringan.
    *   Menambahkan tags dan logs yang relevan ke Spans.
    *   Mengirim data Span ke kolektor atau backend.
    *   Banyak framework web dan library klien RPC modern memiliki instrumentasi otomatis atau semi-otomatis yang tersedia.
2.  **Penyebaran Kolektor (Opsional tapi Umum):** Menggunakan **OpenTelemetry Collector** (di-deploy sebagai DaemonSet atau Deployment) sering direkomendasikan. Aplikasi mengirim trace ke Collector, dan Collector menangani buffering, pemrosesan/sampling, dan pengiriman ke satu atau lebih backend tracing. Ini memisahkan aplikasi dari detail backend.
3.  **Penyebaran Backend Tracing:** Deploy backend pilihan Anda (Jaeger, Tempo, dll.) di dalam atau di luar cluster.
4.  **Integrasi Service Mesh:** Service mesh seperti Istio dan Linkerd dapat secara **otomatis** menghasilkan Spans dan menangani context propagation untuk traffic yang melewati proxy sidecar mereka, memberikan tracing dasar *tanpa* perlu instrumentasi kode aplikasi (meskipun instrumentasi masih diperlukan untuk melihat detail *di dalam* aplikasi). Data trace dari mesh perlu dikonfigurasi untuk dikirim ke backend tracing.

## Manfaat Utama

*   **Debugging Lintas Layanan:** Cepat mengidentifikasi layanan mana yang lambat atau error dalam rantai panggilan.
*   **Analisis Performa:** Memahami latensi end-to-end dan kontribusi setiap layanan/komponen.
*   **Optimalisasi:** Menemukan bottleneck tersembunyi atau panggilan yang tidak perlu.
*   **Pemahaman Dependensi:** Memvisualisasikan bagaimana layanan saling berinteraksi.

Distributed Tracing adalah alat observability yang sangat kuat, terutama dalam arsitektur microservice. Meskipun memerlukan upaya instrumentasi (atau penggunaan service mesh), wawasan yang diberikannya seringkali sangat berharga untuk menjaga kesehatan dan performa sistem terdistribusi yang kompleks. OpenTelemetry menyederhanakan proses adopsi dengan menyediakan standar terpadu.
