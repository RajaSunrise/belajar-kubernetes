# Manajemen Secrets yang Aman di Kubernetes

Objek `Secret` di Kubernetes dirancang untuk menyimpan sejumlah kecil data sensitif seperti kata sandi, token API, kunci SSH, atau sertifikat TLS. Memisahkan data ini dari konfigurasi aplikasi (ConfigMaps) dan image kontainer adalah praktik keamanan dasar. Namun, bagaimana kita memastikan Secrets ini dikelola dan digunakan dengan aman?

## Tantangan Keamanan Secrets Bawaan

Meskipun objek `Secret` lebih baik daripada hardcoding data sensitif, mekanisme bawaan Kubernetes memiliki beberapa keterbatasan keamanan yang perlu dipahami:

1.  **Encoding, Bukan Enkripsi (di API):** Data dalam objek `Secret` disimpan dalam format **Base64 encoding**, *bukan* enkripsi. Siapa pun yang memiliki izin RBAC untuk membaca (`get`, `list`, `watch`) objek Secret di suatu namespace dapat dengan mudah mendekode nilai Base64 tersebut.
    ```bash
    # Contoh mendapatkan nilai secret terenkode base64
    kubectl get secret my-db-secret -o jsonpath='{.data.password}' | base64 --decode
    ```
2.  **Penyimpanan di Etcd:** Secara default, data Secret (yang sudah di-encode Base64) disimpan sebagai plain text (atau hanya ter-encode Base64) di dalam `etcd`, database utama cluster. Jika seseorang mendapatkan akses langsung ke backup etcd atau ke etcd itu sendiri, mereka dapat membaca semua Secret.
3.  **Akses RBAC:** Izin untuk membuat atau membaca Secret adalah titik kontrol utama. Jika RBAC tidak dikonfigurasi dengan benar (terlalu permisif), pengguna atau Service Account yang tidak seharusnya bisa saja membaca data sensitif.
4.  **Log dan `describe`:** Meskipun `kubectl get secret ... -o yaml` tidak menampilkan data secara default, `kubectl describe secret` juga tidak. Namun, data bisa bocor melalui cara lain jika tidak hati-hati (misalnya, jika aplikasi mencetak nilai secret ke log).
5.  **Risiko Saat Digunakan:** Bagaimana Secret digunakan oleh Pod juga penting. Me-mount Secret sebagai environment variable umumnya dianggap kurang aman daripada me-mountnya sebagai volume file, karena environment variable dapat lebih mudah terekspos (misalnya, melalui sub-proses atau log debug).

## Praktik Terbaik Manajemen Secret di Kubernetes

Untuk mengatasi tantangan ini dan meningkatkan keamanan manajemen Secret, pertimbangkan praktik terbaik berikut:

**1. Terapkan RBAC dengan Hak Akses Minimum (Least Privilege):**
   *   Ini adalah lapisan pertahanan **paling penting**.
   *   Berikan izin `get`, `list`, `watch` pada objek `Secret` hanya kepada pengguna atau Service Account yang **benar-benar** membutuhkannya.
   *   Berikan izin `create`, `update`, `patch`, `delete` hanya kepada entitas yang bertanggung jawab mengelola siklus hidup Secret (misalnya, admin, pipeline CI/CD, operator).
   *   Gunakan `Roles` dan `RoleBindings` (namespaced) sebisa mungkin, hindari `ClusterRoles` dan `ClusterRoleBindings` untuk akses Secret kecuali mutlak diperlukan.

**2. Aktifkan Enkripsi Secret at-Rest di Etcd:**
   *   Konfigurasikan API Server (`--encryption-provider-config`) untuk mengenkripsi data Secret saat disimpan di etcd. Ini melindungi data jika seseorang mendapatkan akses ke backup etcd atau etcd secara langsung.
   *   Kubernetes mendukung beberapa provider enkripsi (misalnya, `aescbc`, `aesgcm`, `secretbox`) dan dapat diintegrasikan dengan Key Management Service (KMS) eksternal (seperti AWS KMS, Google Cloud KMS, Azure Key Vault, HashiCorp Vault) untuk manajemen kunci enkripsi yang lebih aman.
   *   **Penting:** Mengaktifkan enkripsi at-rest adalah langkah krusial untuk keamanan data sensitif di etcd.

**3. Gunakan Volume Mounts daripada Environment Variables:**
   *   Saat menyuntikkan Secret ke dalam Pod, **utamakan** me-mount Secret sebagai file dalam volume (`spec.volumes[].secret`).
   *   Ini mencegah Secret muncul dalam variabel lingkungan proses, yang bisa bocor melalui `exec`, log, atau inspeksi lainnya.
   *   Mount volume Secret menggunakan `tmpfs` (filesystem berbasis memori) secara default, mengurangi risiko data tertulis ke disk Node.
   *   Set `readOnly: true` pada `volumeMounts` untuk mencegah aplikasi secara tidak sengaja mengubah file secret.

   ```yaml
   # Contoh mount sebagai volume (lebih disukai)
   spec:
     containers:
     - name: myapp
       volumeMounts:
       - name: db-creds-vol
         mountPath: "/etc/secrets/db"
         readOnly: true
     volumes:
     - name: db-creds-vol
       secret:
         secretName: my-db-secret
         # items: # Opsional: pilih key tertentu
         # - key: password
         #   path: db_password.txt
   ```

**4. Hindari Menyimpan Manifest Secret di Git (Plain Text):**
   *   Jangan menyimpan file YAML Secret dengan data sensitif (bahkan yang ter-encode Base64) langsung di repositori Git Anda.
   *   Gunakan solusi seperti:
        *   **Sealed Secrets (Bitnami/deprecated tapi konsepnya bagus):** Enkripsi Secret *sebelum* dimasukkan ke Git. Hanya controller Sealed Secrets di cluster yang memiliki kunci privat untuk mendekripsinya saat objek `SealedSecret` dibuat.
        *   **SOPS (Mozilla):** Alat enkripsi file YAML/JSON/ENV/INI yang dapat diintegrasikan dengan KMS (AWS, GCP, Azure, PGP, age). Anda mengenkripsi file sebelum commit, dan mendekripsinya saat apply (misalnya, di pipeline CI/CD atau dengan helper `kubectl`).
        *   **Integrasi Vault/External Secrets Operator:** Lihat poin berikutnya.

**5. Integrasikan dengan External Secrets Manager (Solusi Paling Kuat):**
   *   Untuk keamanan dan manajemen siklus hidup secret yang lebih canggih, gunakan solusi manajemen secret eksternal seperti:
        *   **HashiCorp Vault:** Solusi manajemen secret open-source yang sangat populer dan kaya fitur.
        *   **AWS Secrets Manager / Parameter Store**
        *   **Google Cloud Secret Manager**
        *   **Azure Key Vault**
   *   Gunakan **Kubernetes Operators** untuk menjembatani antara sistem eksternal ini dan cluster K8s Anda:
        *   **External Secrets Operator (ESO):** Mengawasi resource kustom `ExternalSecret`. Ketika dibuat, ESO akan mengambil secret dari provider eksternal (Vault, AWS SM, GCP SM, Azure KV, dll.) dan secara otomatis membuat/menyinkronkan objek `Secret` Kubernetes native di namespace yang sesuai. Aplikasi Anda kemudian menggunakan Secret K8s native seperti biasa.
        *   **Vault Agent Injector / CSI Driver:** Memungkinkan Pod untuk secara langsung meminta dan me-mount secret dari Vault ke dalam filesystem Pod (seringkali via `tmpfs`) tanpa perlu membuat Secret K8s perantara. Ini adalah pola yang sangat aman.
   *   **Keuntungan:** Manajemen secret terpusat, rotasi otomatis, audit trail, kebijakan akses halus, enkripsi kuat.

**6. Rotasi Secret Secara Berkala:**
   *   Ganti kredensial (password, token, kunci) secara berkala.
   *   Solusi eksternal seperti Vault atau KMS cloud seringkali memiliki fitur untuk membantu mengotomatiskan rotasi. Jika mengelola secara manual, buat proses untuk rotasi reguler.

**7. Audit Akses Secret:**
   *   Aktifkan Audit Logging di API Server Kubernetes.
   *   Pantau log audit untuk akses (terutama `get`, `list`) ke objek `Secret` untuk mendeteksi aktivitas yang mencurigakan atau tidak sah.

Manajemen secret yang aman adalah aspek fundamental dari keamanan Kubernetes. Dengan memahami keterbatasan bawaan dan menerapkan praktik terbaik seperti RBAC yang ketat, enkripsi at-rest, dan idealnya integrasi dengan manajer secret eksternal, Anda dapat secara signifikan mengurangi risiko kebocoran data sensitif.
