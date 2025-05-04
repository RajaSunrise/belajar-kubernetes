# Studi Kasus: Hosting Database Relasional di Kubernetes

Menjalankan database stateful (seperti PostgreSQL, MySQL) di Kubernetes secara historis dianggap menantang, tetapi dengan adanya `StatefulSet`, `PersistentVolumes`, dan Operator Pattern, ini menjadi semakin umum dan layak dilakukan, terutama untuk lingkungan development, testing, atau bahkan produksi dengan perencanaan yang matang.

**Tujuan:** Menjelaskan pertimbangan utama dan pola arsitektur umum untuk menjalankan database relasional di Kubernetes, fokus pada persistensi data, identitas stabil, dan potensi ketersediaan tinggi (High Availability - HA).

**Peringatan:** Menjalankan database kritis produksi di Kubernetes memerlukan keahlian operasional Kubernetes dan database yang mendalam. Pertimbangkan baik-baik trade-off dibandingkan menggunakan layanan database terkelola (Managed Database) dari penyedia cloud (seperti AWS RDS, Google Cloud SQL, Azure Database) yang menangani banyak kompleksitas operasional (backup, patching, HA) untuk Anda.

## Tantangan Menjalankan Database di Kubernetes

*   **Statefulness:** Database menyimpan data penting yang harus persisten dan konsisten.
*   **Identitas Stabil:** Setiap instance database (replika) seringkali memerlukan identitas jaringan yang stabil dan dapat diprediksi untuk keperluan replikasi, koneksi klien, atau clustering.
*   **Penyimpanan Persisten:** Membutuhkan akses ke penyimpanan yang andal, performan, dan persisten yang tidak hilang saat Pod di-restart atau dipindahkan.
*   **Ketersediaan Tinggi (HA):** Seringkali memerlukan mekanisme replikasi (asinkron/sinkron), deteksi kegagalan, dan failover otomatis ke instance standby.
*   **Backup & Restore:** Prosedur backup dan restore yang andal sangat penting.
*   **Performa I/O:** Database seringkali sensitif terhadap latensi dan throughput penyimpanan.
*   **Manajemen Siklus Hidup:** Upgrade versi database, patching, perubahan konfigurasi perlu dilakukan dengan hati-hati untuk meminimalkan downtime dan risiko kehilangan data.

## Komponen Kubernetes Kunci

*   **`StatefulSet`:** Pengontrol utama untuk aplikasi stateful. Menyediakan:
    *   Identitas Pod yang stabil dan unik (ordinal: `-0`, `-1`, ...).
    *   Nama DNS Pod yang stabil (via Headless Service).
    *   Penyimpanan persisten yang stabil per Pod (via `volumeClaimTemplates`).
    *   Deployment, scaling, dan update yang terurut dan anggun.
*   **`PersistentVolumeClaim` (PVC) & `PersistentVolume` (PV):** Untuk menyediakan penyimpanan persisten. `volumeClaimTemplates` di StatefulSet memastikan setiap Pod mendapatkan PVC uniknya sendiri.
*   **`StorageClass`:** Untuk dynamic provisioning PV dengan karakteristik performa dan ketersediaan yang diinginkan (misalnya, disk SSD dengan IOPS tinggi). `volumeBindingMode: WaitForFirstConsumer` sering direkomendasikan.
*   **`Service`:**
    *   **Headless Service:** Penting untuk StatefulSet, menyediakan domain DNS untuk penemuan antar Pod replika.
    *   **ClusterIP Service (Read/Write):** Endpoint stabil untuk aplikasi terhubung ke instance primary/master.
    *   **ClusterIP Service (Read-Only) (Opsional):** Endpoint stabil untuk aplikasi terhubung ke instance read-replica (jika ada).
*   **`Secret`:** Untuk menyimpan kredensial database (password superuser, password user aplikasi).
*   **`ConfigMap`:** Untuk menyimpan konfigurasi database (misalnya, `postgresql.conf`, `my.cnf`).
*   **`PodDisruptionBudget` (PDB):** Memastikan sejumlah minimum Pods database tetap tersedia selama aktivitas pemeliharaan cluster sukarela (seperti upgrade Node).
*   **Probes (`livenessProbe`, `readinessProbe`):** Untuk memeriksa kesehatan instance database (misalnya, cek koneksi, status replikasi).
*   **(Opsional tapi Sangat Direkomendasikan) Operator Database:** Pola yang menggunakan CRD dan custom controller untuk mengotomatisasi tugas manajemen database yang kompleks (setup replikasi, backup, restore, failover, upgrade).

## Pola Arsitektur Umum (Contoh: PostgreSQL dengan Replikasi Streaming)

Ini adalah contoh pola yang relatif umum untuk HA dasar. Implementasi detail dapat bervariasi.

```mermaid
graph TD
    subgraph "Cluster Kubernetes (Namespace: database-prod)"
        ServiceRW[Service <br/> pg-rw-svc <br/> (Menunjuk ke Primary)]
        ServiceRO[Service <br/> pg-ro-svc <br/> (Menunjuk ke Standby(s))]
        ServiceHeadless[Service (Headless) <br/> pg-headless-svc]

        StatefulSetPG(StatefulSet <br/> postgresql)

        subgraph "Pod Primary"
            style Pod Primary fill:#cfc
            PodPG0(Pod <br/> postgresql-0 <br/> [Role: Primary])
            PVC0[PVC <br/> data-postgresql-0]
            PV0[(PV-SSD-1)]
        end

        subgraph "Pod Standby 1"
            style Pod Standby 1 fill:#eef
            PodPG1(Pod <br/> postgresql-1 <br/> [Role: Standby])
            PVC1[PVC <br/> data-postgresql-1]
            PV1[(PV-SSD-2)]
        end

        subgraph "Pod Standby 2"
            style Pod Standby 2 fill:#eef
            PodPG2(Pod <br/> postgresql-2 <br/> [Role: Standby])
            PVC2[PVC <br/> data-postgresql-2]
            PV2[(PV-SSD-3)]
        end

        ConfigMapPG[ConfigMap <br/> pg-config]
        SecretPG[Secret <br/> pg-credentials]
        PDB_PG[PodDisruptionBudget]

        ClientApp(Aplikasi Klien) --> ServiceRW
        ClientApp --> ServiceRO

        ServiceRW -.-> PodPG0
        ServiceRO -.-> PodPG1
        ServiceRO -.-> PodPG2

        StatefulSetPG -- Manages --> PodPG0
        StatefulSetPG -- Manages --> PodPG1
        StatefulSetPG -- Manages --> PodPG2

        StatefulSetPG -- Requires --> ServiceHeadless

        PodPG0 -- Mounts --> PVC0
        PodPG1 -- Mounts --> PVC1
        PodPG2 -- Mounts --> PVC2

        PodPG0 -- Reads --> ConfigMapPG
        PodPG1 -- Reads --> ConfigMapPG
        PodPG2 -- Reads --> ConfigMapPG

        PodPG0 -- Reads --> SecretPG
        PodPG1 -- Reads --> SecretPG
        PodPG2 -- Reads --> SecretPG

        PVC0 -- Bound --> PV0
        PVC1 -- Bound --> PV1
        PVC2 -- Bound --> PV2

        PDB_PG -- Protects --> StatefulSetPG # Logika: Melindungi minimal N Pods dari StatefulSet
    end

    style ClientApp fill:#fec
```

**Penjelasan Komponen:**

1.  **StatefulSet (`postgresql`):** Mengelola 3 Pods (`postgresql-0`, `postgresql-1`, `postgresql-2`).
2.  **Headless Service (`pg-headless-svc`):** Menyediakan DNS stabil (`postgresql-0.pg-headless-svc...`, `postgresql-1...`, `postgresql-2...`) yang digunakan untuk setup replikasi streaming antar Pods.
3.  **PVCs & PVs:** Setiap Pod mendapatkan PVC uniknya sendiri yang terikat ke PV (dibuat dinamis via StorageClass `fast-ssd` dengan `volumeBindingMode: WaitForFirstConsumer`).
4.  **ConfigMap (`pg-config`):** Menyimpan konfigurasi PostgreSQL (misalnya, pengaturan replikasi, `shared_buffers`, dll.). Di-mount sebagai file ke semua Pods. Perubahan memerlukan restart Pod (dikelola oleh rollout StatefulSet).
5.  **Secret (`pg-credentials`):** Menyimpan password superuser dan user replikasi. Di-mount sebagai file atau env var.
6.  **Service Read/Write (`pg-rw-svc`):** Endpoint untuk aplikasi melakukan operasi tulis. **Tantangan:** Service ini perlu *secara dinamis* menunjuk ke Pod mana yang saat ini menjadi *primary*. Ini **tidak terjadi secara otomatis** hanya dengan selector biasa. Diperlukan mekanisme tambahan:
    *   **Operator:** Operator database (seperti Crunchy Data PGO, Zalando Postgres Operator) akan menangani deteksi primary dan memperbarui selector/endpoints Service `pg-rw-svc` secara otomatis saat terjadi failover.
    *   **Solusi Eksternal/Skrip Startup:** Skrip di dalam kontainer atau proses eksternal dapat memperbarui label pada Pod primary (misalnya, `role=primary`), dan selector Service `pg-rw-svc` diatur untuk menargetkan label tersebut. Ini lebih kompleks dan rapuh.
7.  **Service Read-Only (`pg-ro-svc`) (Opsional):** Endpoint untuk aplikasi melakukan operasi baca. Bisa menggunakan selector yang menargetkan Pods dengan label `role=standby` (jika label diatur) atau menargetkan semua Pods (jika replika dapat melayani bacaan).
8.  **PodDisruptionBudget (PDB):** Mengkonfigurasi (misalnya) `minAvailable: 2` untuk StatefulSet `postgresql`. Ini memberitahu Kubernetes untuk tidak menghentikan lebih dari satu Pod database secara bersamaan selama maintenance node sukarela, menjaga kuorum HA.
9.  **Probes:**
    *   `readinessProbe`: Memeriksa apakah instance siap menerima koneksi (dan mungkin apakah sudah sinkron dengan primary untuk standby).
    *   `livenessProbe`: Memeriksa apakah proses PostgreSQL masih berjalan.

**Pertimbangan Tambahan:**

*   **Manajemen Replikasi & Failover:** Ini adalah bagian paling kompleks. Tanpa Operator, Anda perlu mengimplementasikan logika ini sendiri (misalnya, menggunakan Patroni, repmgr di dalam kontainer, atau skrip kustom). Operator sangat menyederhanakan ini.
*   **Backup:** Backup reguler sangat penting. Gunakan `pg_dump` (via CronJob), snapshot volume (jika konsisten), atau fitur backup dari Operator. Simpan backup di lokasi eksternal (misalnya, S3).
*   **Koneksi Pooling:** Gunakan connection pooler seperti PgBouncer (bisa sebagai sidecar atau Deployment terpisah) untuk mengelola koneksi dari aplikasi ke database secara efisien.
*   **Performa Storage:** Pilih StorageClass yang tepat dengan performa I/O yang dibutuhkan database Anda. Uji performa.
*   **Observability:** Pantau metrik database spesifik (jumlah koneksi, latensi query, status replikasi, penggunaan disk) menggunakan exporter Prometheus (seperti `postgres_exporter`).

**Kesimpulan:**

Menjalankan database relasional di Kubernetes *memungkinkan* dengan alat seperti StatefulSet dan PVC. Namun, mencapai ketersediaan tinggi, manajemen siklus hidup otomatis, dan operasi yang andal seringkali memerlukan upaya signifikan atau penggunaan **Operator Database** yang meng-encode best practices operasional ke dalam otomatisasi. Evaluasi dengan cermat apakah manfaat menjalankan database di K8s (konsistensi platform, otomatisasi dasar) melebihi kompleksitas operasionalnya dibandingkan dengan layanan database terkelola jika tersedia. Untuk development/testing, menjalankan database di K8s seringkali merupakan pilihan yang sangat baik.
