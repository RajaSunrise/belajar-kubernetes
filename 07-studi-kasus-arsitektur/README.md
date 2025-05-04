# Bagian Tujuh: Studi Kasus dan Arsitektur Referensi

Memahami konsep dan praktik terbaik Kubernetes adalah satu hal, melihat bagaimana mereka diterapkan dalam skenario aplikasi dunia nyata adalah hal lain. Bagian ini menyajikan beberapa studi kasus arsitektur umum yang di-deploy di Kubernetes.

Tujuannya adalah untuk mengilustrasikan bagaimana berbagai objek dan pola Kubernetes (Deployments, StatefulSets, Services, Ingress, ConfigMaps, Secrets, PV/PVC, Operators, dll.) dapat digabungkan untuk membangun solusi yang berbeda, menyoroti pertimbangan desain dan trade-off untuk setiap kasus.

## Studi Kasus yang Dicakup

1.  **[Aplikasi Web Multi-Tier](./01-web-app-multi-tier.md):**
    *   **Skenario:** Aplikasi web klasik dengan lapisan frontend (misalnya, SPA yang disajikan Nginx), backend API stateless (misalnya, Node.js/Python/Go), dan database relasional (misalnya, PostgreSQL).
    *   **Konsep Kunci:** Deployment (Frontend, Backend), Service (ClusterIP), Ingress (eksposur eksternal), StatefulSet (Database), PVC/PV (Storage Database), ConfigMap/Secret (Konfigurasi/Kredensial), HPA (Scaling Backend).
    *   **Fokus:** Menunjukkan interaksi standar antar komponen stateless dan stateful, service discovery internal, dan eksposur eksternal.

2.  **[Pipeline Pemrosesan Data Asinkron](./02-pipeline-data-processing.md):**
    *   **Skenario:** Sistem di mana tugas (misalnya, pemrosesan gambar, pengiriman email, pembuatan laporan) dimasukkan ke dalam antrian (message queue) dan diproses secara asinkron oleh sekumpulan worker.
    *   **Konsep Kunci:** Deployment (Workers), Message Queue (misalnya, RabbitMQ atau Kafka yang di-deploy di K8s atau sebagai layanan eksternal), Jobs/CronJobs (untuk tugas terjadwal/batch), HPA (scaling workers berdasarkan panjang antrian - memerlukan adapter metrik kustom), ConfigMap/Secret.
    *   **Fokus:** Mengilustrasikan pola worker-queue, penskalaan berdasarkan metrik kustom, dan penggunaan Jobs untuk pemrosesan batch.

3.  **[Hosting Database Relasional (HA)](./03-hosting-database.md):**
    *   **Skenario:** Menjalankan database seperti PostgreSQL atau MySQL dengan fokus pada persistensi data, identitas stabil, dan potensi ketersediaan tinggi (replikasi dan failover).
    *   **Konsep Kunci:** StatefulSet, Headless Service, PersistentVolumeClaim (volumeClaimTemplates), StorageClass (performa I/O, WaitForFirstConsumer), ConfigMap/Secret, PodDisruptionBudget, Service (untuk endpoint R/W dan R/O), Operator Pattern (sangat direkomendasikan).
    *   **Fokus:** Menyoroti tantangan menjalankan beban kerja stateful, pentingnya identitas dan storage stabil, dan kompleksitas dalam mencapai HA tanpa atau dengan Operator. Membahas trade-off vs layanan database terkelola.

## Tujuan Pembelajaran

Dengan mempelajari studi kasus ini, Anda diharapkan dapat:

*   Memahami bagaimana memilih objek Kubernetes yang tepat untuk berbagai jenis komponen aplikasi (stateless vs stateful, web vs worker vs batch).
*   Melihat bagaimana objek-objek ini saling terhubung melalui Services, Selectors, dan Ingress.
*   Menghargai pentingnya manajemen konfigurasi, secrets, dan penyimpanan persisten dalam arsitektur nyata.
*   Mengenali pola umum seperti multi-tier, worker-queue, dan HA stateful.
*   Memahami pertimbangan desain dan trade-off saat membangun arsitektur spesifik di Kubernetes.

Studi kasus ini berfungsi sebagai contoh praktis dan titik awal untuk merancang arsitektur aplikasi Anda sendiri di platform Kubernetes.
