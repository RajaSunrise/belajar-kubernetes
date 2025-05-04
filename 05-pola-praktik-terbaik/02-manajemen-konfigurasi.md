# Praktik Terbaik: Manajemen Konfigurasi dan Secrets

Mengelola konfigurasi aplikasi dan data sensitif (secrets) secara efektif dan aman adalah aspek fundamental dalam menjalankan aplikasi di lingkungan mana pun, termasuk Kubernetes. Praktik yang buruk di area ini dapat menyebabkan kesulitan deployment, masalah keamanan, dan inkonsistensi antar lingkungan.

Berikut adalah praktik terbaik untuk manajemen konfigurasi dan secrets di Kubernetes:

**1. Pisahkan Konfigurasi dari Kode & Image (Prinsip Twelve-Factor III)**
   *   **Jangan pernah** melakukan hardcode nilai konfigurasi (seperti URL API, nama database) atau secrets (password, kunci API) langsung di dalam kode aplikasi atau membakarnya ke dalam image kontainer.
   *   Ini membuat image tidak portabel, sulit dikelola antar lingkungan (dev, staging, prod), dan sangat tidak aman untuk secrets.

**2. Gunakan ConfigMaps untuk Konfigurasi Non-Sensitif**
   *   Manfaatkan objek `ConfigMap` Kubernetes untuk menyimpan data konfigurasi yang tidak bersifat rahasia.
   *   Data dapat berupa pasangan key-value sederhana atau konten file utuh.
   *   Contoh: URL endpoint eksternal, flag fitur, pengaturan level log, konfigurasi tema UI, konten file `nginx.conf` atau `settings.properties`.

**3. Gunakan Secrets untuk Data Sensitif**
   *   Gunakan objek `Secret` Kubernetes **khusus** untuk data sensitif seperti password, token API, kunci SSH, sertifikat TLS.
   *   **Pahami Batasan Keamanan Secret Bawaan:** Secara default, data Secret hanya di-encode base64 di etcd, **bukan dienkripsi**. Siapa pun dengan izin RBAC untuk membaca Secret dapat mendekodenya.
   *   **Tingkatkan Keamanan Secret:**
        *   **Aktifkan Enkripsi Etcd at-Rest:** Konfigurasikan API Server untuk mengenkripsi data Secret saat disimpan di etcd.
        *   **Terapkan RBAC Ketat:** Berikan izin `get`, `list`, `watch` pada Secrets seminimal mungkin (Prinsip Least Privilege). Hanya Service Accounts atau pengguna yang benar-benar membutuhkannya yang boleh memiliki akses.
        *   **Pertimbangkan Solusi Manajemen Secret Eksternal (untuk Keamanan Tingkat Lanjut):** Untuk kebutuhan keamanan yang lebih tinggi, integrasikan dengan solusi seperti:
            *   **HashiCorp Vault:** Sistem manajemen secret terpusat yang populer dengan fitur enkripsi kuat, audit, rotasi otomatis. Dapat diintegrasikan dengan K8s melalui sidecar injector atau CSI driver.
            *   **Secrets Store CSI Driver:** Memungkinkan pemasangan secrets dari penyedia eksternal (Vault, AWS Secrets Manager, Azure Key Vault, GCP Secret Manager) sebagai volume file atau env vars, tanpa menyimpan secret di K8s API.
            *   **External Secrets Operator:** Operator yang menyinkronkan secret dari penyedia eksternal ke objek `Secret` Kubernetes native.

**4. Pilih Metode Injeksi yang Tepat**
   Ada dua cara utama menyuntikkan data ConfigMap/Secret ke Pods:

   *   **Environment Variables:**
        *   Menggunakan `env` atau `envFrom` di definisi kontainer.
        *   **Kelebihan:** Mudah diakses oleh banyak aplikasi/framework.
        *   **Kekurangan:**
            *   **Kurang Aman untuk Secrets:** Env vars dapat bocor melalui log, output `kubectl describe`, UI dashboard, atau inspeksi proses (`/proc/[pid]/environ`).
            *   **Tidak Diperbarui Otomatis:** Nilai env var hanya dibaca saat kontainer dimulai. Jika ConfigMap/Secret sumber diubah, Pod perlu di-restart untuk mengambil nilai baru.
        *   **Gunakan untuk:** Konfigurasi non-sensitif yang tidak sering berubah. **Hindari untuk secrets produksi.**

   *   **Volume File Mounts:**
        *   Menggunakan `volumes` (tipe `configMap` atau `secret`) dan `volumeMounts` di definisi Pod. Setiap key di ConfigMap/Secret menjadi file di direktori mount.
        *   **Kelebihan:**
            *   **Lebih Aman untuk Secrets:** Data tidak mudah terekspos seperti env vars. Anda dapat mengatur izin file (misalnya, `defaultMode: 0400`).
            *   **Pembaruan Otomatis (Hot Reload):** Data file yang di-mount **diperbarui secara otomatis** oleh Kubelet (dengan sedikit penundaan) ketika ConfigMap/Secret sumber diubah. Aplikasi Anda dapat dirancang untuk mendeteksi perubahan file (misalnya, menggunakan inotify atau polling) dan memuat ulang konfigurasi tanpa perlu restart Pod.
            *   Cocok untuk konten file multi-baris atau biner.
        *   **Kekurangan:** Aplikasi perlu dimodifikasi untuk membaca konfigurasi/secret dari file, bukan env vars.
        *   **Gunakan untuk:** **Secrets (metode yang disarankan)**, file konfigurasi utuh, data yang mungkin perlu diperbarui tanpa restart Pod.

**5. Kelola Konfigurasi dan Secrets Secara Deklaratif (GitOps)**
   *   Simpan definisi ConfigMap dan Secret (atau referensi ke secret eksternal) Anda dalam sistem kontrol versi (Git) bersama dengan manifest aplikasi lainnya.
   *   Gunakan alat seperti `kubectl apply`, Kustomize, atau Helm untuk menerapkan perubahan konfigurasi secara deklaratif.
   *   **Untuk Secrets di Git:** JANGAN menyimpan secret plain text di Git. Gunakan alat enkripsi seperti:
        *   **SOPS (Secrets OPerationS):** Alat Mozilla/StackExchange untuk mengenkripsi file YAML/JSON dengan kunci KMS (AWS, GCP, Azure), PGP, atau age. File terenkripsi aman disimpan di Git. Alat CI/CD atau operator (seperti Flux dengan dukungan SOPS) dapat mendekripsinya saat deployment.
        *   **Helm Secrets:** Plugin Helm yang memungkinkan enkripsi/dekripsi nilai dalam `values.yaml` menggunakan SOPS.
        *   Pendekatan External Secrets (Vault, Secrets Store CSI Driver, External Secrets Operator) juga menghindari penyimpanan secret di Git.
   *   Adopsi alur kerja **GitOps** (menggunakan Argo CD, Flux) untuk menyinkronkan state konfigurasi dari Git ke cluster secara otomatis.

**6. Gunakan Nama yang Konsisten dan Deskriptif**
   *   Beri nama ConfigMap dan Secret Anda secara jelas untuk menunjukkan aplikasi dan lingkungan mana yang mereka layani (misalnya, `my-app-prod-config`, `my-app-staging-db-credentials`).
   *   Gunakan label untuk mengkategorikan dan memfilter ConfigMap/Secret.

**7. Audit dan Rotasi Secrets**
   *   Terapkan kebijakan untuk mengaudit akses ke Secrets secara berkala.
   *   Rotasi (ubah) secrets secara teratur, terutama yang berisiko tinggi. Otomatiskan proses rotasi jika memungkinkan (misalnya, menggunakan Vault atau solusi manajemen secret lainnya).

Manajemen konfigurasi dan secret yang baik adalah fondasi untuk aplikasi Kubernetes yang aman, dapat dikelola, dan portabel. Memisahkan konfigurasi, menggunakan alat yang tepat (ConfigMap vs Secret), memilih metode injeksi yang aman, dan mengelola semuanya secara deklaratif melalui Git adalah kunci keberhasilan.
