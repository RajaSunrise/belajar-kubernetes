# Autentikasi (Authentication) di Kubernetes: Menjawab "Siapa Anda?"

Sebelum Kubernetes dapat memutuskan *apa* yang boleh Anda lakukan (Otorisasi), ia perlu tahu *siapa* Anda. Proses verifikasi identitas ini disebut **Autentikasi (Authentication - AuthN)**.

Kubernetes memiliki model autentikasi yang fleksibel dan pluggable. Penting untuk dipahami bahwa Kubernetes **tidak memiliki objek `User` internal**. Ia tidak menyimpan daftar pengguna atau password secara native. Sebaliknya, Kubernetes mengandalkan satu atau lebih **modul autentikasi** yang dikonfigurasi pada API Server untuk memvalidasi kredensial yang disertakan dalam setiap permintaan API.

## Sumber Identitas di Kubernetes

Ada dua kategori utama identitas yang perlu diautentikasi:

1.  **Normal Users (Pengguna Manusia):**
    *   Ini adalah administrator, developer, atau siapa saja yang berinteraksi dengan cluster melalui `kubectl` atau dashboard UI.
    *   Kubernetes *tidak mengelola* akun pengguna ini secara langsung. Mereka biasanya dikelola oleh sistem identitas eksternal (seperti sistem SSO perusahaan, file statis, atau sertifikat yang dikelola admin).
    *   Saat melakukan permintaan, pengguna manusia harus menyajikan kredensial yang dapat divalidasi oleh salah satu modul autentikasi yang aktif.

2.  **Service Accounts (Akun Layanan untuk Proses):**
    *   Ini adalah identitas yang digunakan oleh **proses yang berjalan di dalam Pods** untuk berkomunikasi dengan API Server (misalnya, controller kustom, aplikasi yang perlu membaca ConfigMaps, dll.).
    *   Berbeda dengan Normal Users, Service Accounts **dikelola oleh Kubernetes API**. Anda dapat membuat, melihat, dan menghapus objek `ServiceAccount` menggunakan `kubectl`.
    *   Setiap namespace memiliki Service Account default (`default`).
    *   Kubernetes secara otomatis membuat *token* (JSON Web Token - JWT) untuk Service Accounts, yang kemudian dapat di-mount ke dalam Pods untuk digunakan saat melakukan panggilan API.

## Strategi/Modul Autentikasi Umum

API Server dapat dikonfigurasi untuk mencoba beberapa modul autentikasi secara berurutan. Modul pertama yang berhasil memvalidasi kredensial akan menentukan identitas pengguna untuk permintaan tersebut. Beberapa strategi umum meliputi:

1.  **Sertifikat Klien X.509 (Client Certificates):**
    *   **Cara Kerja:** Pengguna menyajikan sertifikat klien yang ditandatangani oleh Certificate Authority (CA) yang dipercaya oleh API Server (dikonfigurasi dengan flag `--client-ca-file`). Common Name (CN) dari sertifikat digunakan sebagai *username*, dan Organization (O) digunakan sebagai *group membership*.
    *   **Penggunaan:** Sangat umum untuk autentikasi antar komponen Control Plane (Kubelet ke API Server, Scheduler ke API Server) dan sering digunakan untuk autentikasi administrator cluster. Kredensial ini biasanya tertanam dalam file `kubeconfig`.
    *   **Pros:** Sangat aman jika dikelola dengan benar.
    *   **Cons:** Manajemen siklus hidup sertifikat (penerbitan, perpanjangan, pencabutan) bisa rumit.

2.  **Static Token File:**
    *   **Cara Kerja:** Administrator membuat file CSV (`token,user,uid,"group1,group2"`) yang berisi token statis dan memetakannya ke pengguna/grup. Path file ini diberikan ke API Server (`--token-auth-file`). Pengguna menyertakan token ini dalam header `Authorization: Bearer <token>` pada permintaan API.
    *   **Penggunaan:** Cara sederhana untuk token statis, tetapi kurang fleksibel dan aman.
    *   **Pros:** Mudah diatur untuk kasus sederhana.
    *   **Cons:** Token statis, sulit dicabut, tidak diskalakan dengan baik, file token perlu didistribusikan dan diamankan. **Umumnya tidak direkomendasikan untuk produksi.**

3.  **Bootstrap Tokens:**
    *   **Cara Kerja:** Token sementara dengan masa berlaku terbatas, disimpan sebagai Secret di dalam cluster. Digunakan khusus untuk proses *bootstrap* cluster, terutama untuk Node baru agar dapat bergabung dengan cluster dan mendapatkan sertifikat klien jangka panjang.
    *   **Penggunaan:** Internal untuk proses join `kubeadm`.

4.  **Static Password File:**
    *   **Cara Kerja:** Mirip Static Token File, tetapi menggunakan username/password (Basic Auth). File (`password,user,uid,"group1,group2"`) diberikan ke API Server (`--basic-auth-file`). Kredensial dikirim dalam header `Authorization: Basic <base64-encoded-username-password>`.
    *   **Penggunaan:** **Sangat tidak direkomendasikan** karena mengirim password dalam bentuk yang mudah didekode.

5.  **Service Account Tokens:**
    *   **Cara Kerja:** Kubernetes secara otomatis membuat token JWT untuk objek `ServiceAccount`. Token ini dapat diambil dari Secret terkait atau (di versi K8s lebih baru) diminta melalui TokenRequest API (menghasilkan token dengan masa berlaku terbatas dan audience spesifik). Token disertakan dalam header `Authorization: Bearer <token>`. API Server memvalidasi tanda tangan token menggunakan kunci privatnya.
    *   **Penggunaan:** **Metode standar** untuk autentikasi proses di dalam cluster (Pods) ke API Server.
    *   **Pros:** Terintegrasi, dikelola K8s, lebih aman (terutama token terikat waktu/audience).
    *   **Cons:** Perlu pengelolaan RBAC yang tepat untuk Service Account.

6.  **OpenID Connect (OIDC) Tokens:**
    *   **Cara Kerja:** Memungkinkan integrasi dengan **Identity Provider (IdP)** eksternal yang mendukung OIDC (misalnya, Google, Okta, Keycloak, Dex). Pengguna melakukan autentikasi dengan IdP, mendapatkan ID Token (JWT). Token ini dikirim ke API Server (`Authorization: Bearer <id_token>`). API Server dikonfigurasi (`--oidc-issuer-url`, `--oidc-client-id`, dll.) untuk memvalidasi tanda tangan token dan mengekstrak informasi pengguna (username, groups) dari klaim di dalam token.
    *   **Penggunaan:** **Metode standar dan direkomendasikan** untuk mengintegrasikan autentikasi pengguna manusia dengan sistem SSO/IdP perusahaan. `kubectl` sering memerlukan plugin helper (seperti `kubelogin`) untuk menangani alur OIDC.
    *   **Pros:** Memanfaatkan sistem identitas yang ada, manajemen pengguna terpusat, mendukung SSO, lebih aman daripada token/password statis.
    *   **Cons:** Memerlukan penyiapan IdP dan konfigurasi API Server yang sesuai.

7.  **Authenticating Proxy:**
    *   **Cara Kerja:** Anda menempatkan proxy di depan API Server. Proxy menangani autentikasi (menggunakan metode apa pun yang didukungnya) dan kemudian meneruskan permintaan ke API Server, menambahkan header khusus (seperti `X-Remote-User`, `X-Remote-Group`) yang dipercaya oleh API Server (dikonfigurasi dengan flag `--requestheader-client-ca-file`, `--requestheader-allowed-names`, dll.).
    *   **Penggunaan:** Integrasi dengan sistem autentikasi kustom atau yang kompleks.

8.  **Webhook Token Authentication:**
    *   **Cara Kerja:** API Server dikonfigurasi (`--authentication-token-webhook-config`) untuk mengirim token yang diterima ke layanan (webhook) eksternal melalui permintaan POST. Webhook eksternal bertanggung jawab memvalidasi token dan mengembalikan informasi pengguna jika valid.
    *   **Penggunaan:** Integrasi dengan sistem autentikasi token kustom.

## Informasi Pengguna Hasil Autentikasi

Setelah modul autentikasi berhasil memvalidasi kredensial, ia akan memberikan informasi berikut kepada API Server untuk digunakan dalam langkah Otorisasi:

*   **Username:** String unik yang mengidentifikasi pengguna (misalnya, `system:kube-scheduler`, `jane@example.com`, `system:serviceaccount:myapp-ns:my-sa`). Prefix `system:` dicadangkan untuk penggunaan internal Kubernetes.
*   **UID:** String unik yang lebih stabil daripada username (opsional).
*   **Groups:** Daftar string yang menunjukkan keanggotaan grup pengguna (misalnya, `system:masters`, `system:authenticated`, `dev-leads`). Grup `system:authenticated` otomatis ditambahkan untuk semua pengguna yang berhasil diautentikasi.
*   **Extra Fields:** Data key-value tambahan (opsional).

## Ringkasan

*   Kubernetes tidak mengelola akun pengguna manusia secara native.
*   Service Accounts adalah objek K8s untuk identitas proses dalam Pod.
*   API Server menggunakan modul autentikasi yang dapat dicolokkan (pluggable).
*   Metode umum termasuk Sertifikat Klien, Token Service Account, dan OIDC (untuk pengguna manusia via IdP).
*   Hindari metode statis seperti Static Token/Password File untuk produksi.
*   Hasil autentikasi (username, groups) digunakan oleh sistem Otorisasi (RBAC) untuk menentukan izin.

Memilih dan mengkonfigurasi metode autentikasi yang tepat adalah langkah pertama yang krusial dalam mengamankan cluster Kubernetes Anda.
