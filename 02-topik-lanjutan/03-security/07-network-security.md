# Keamanan Jaringan di Kubernetes: Ringkasan

Mengamankan komunikasi jaringan di dalam dan di sekitar cluster Kubernetes adalah pilar penting dari postur keamanan keseluruhan. Bab-bab sebelumnya telah membahas beberapa alat utama, tetapi mari kita rangkum dan tekankan konsep kunci keamanan jaringan:

## 1. Segmentasi Jaringan dengan Network Policies

*   **Konsep:** Secara default, jaringan Kubernetes datar dan terbuka. Network Policies bertindak sebagai firewall stateful internal pada Layer 3/4 untuk mengontrol traffic antar Pods dan Namespace.
*   **Mengapa Penting:** Menerapkan prinsip *least privilege* pada jaringan. Membatasi radius ledakan (blast radius) jika sebuah Pod terkompromi; penyerang tidak dapat dengan mudah menjangkau Pod lain. Membantu memenuhi persyaratan kepatuhan (compliance).
*   **Cara Kerja:**
    *   Menggunakan `podSelector` untuk menargetkan Pods.
    *   Menggunakan `policyTypes: [Ingress, Egress]` untuk menentukan arah traffic yang dikontrol.
    *   Menggunakan aturan `ingress` (dengan `from`) dan `egress` (dengan `to`) untuk secara eksplisit *mengizinkan* traffic dari/ke `podSelector`, `namespaceSelector`, atau `ipBlock` tertentu pada `ports` spesifik.
    *   **Default Deny Implisit:** Segera setelah satu NetworkPolicy menargetkan Pod, semua traffic (sesuai `policyTypes`) yang tidak secara eksplisit diizinkan akan **diblokir**.
*   **Prasyarat:** Membutuhkan CNI yang mendukung NetworkPolicy (Calico, Cilium, Weave Net, dll.).
*   **Praktik Terbaik:** Mulai dengan `default-deny`, gunakan label secara efektif, uji coba, visualisasikan. Jangan lupakan kebijakan `egress`.

## 2. Mengamankan Akses Eksternal dengan Ingress & TLS

*   **Konsep:** Ingress Controllers (Nginx, Traefik, dll.) bertindak sebagai reverse proxy L7 untuk mengelola traffic HTTP/S masuk ke cluster.
*   **Keamanan:**
    *   **Terminasi TLS:** Ingress Controller dapat menghentikan koneksi TLS (HTTPS) menggunakan sertifikat yang disimpan di Secret Kubernetes (`kubernetes.io/tls`). Ini mengenkripsi traffic dari klien eksternal ke Ingress Controller.
    *   **Sentralisasi Kontrol:** Menyediakan titik kontrol tunggal untuk menerapkan kebijakan keamanan web dasar (misalnya, pembatasan rate, autentikasi dasar - tergantung fitur controller).
    *   **Menyembunyikan Topologi Internal:** Klien eksternal hanya berinteraksi dengan Ingress Controller, bukan langsung dengan Service atau Pod internal.
*   **Praktik Terbaik:** Selalu gunakan HTTPS (TLS) untuk traffic eksternal. Kelola sertifikat dengan aman (misalnya, gunakan `cert-manager` untuk otomatisasi Let's Encrypt). Konfigurasikan Ingress Controller dengan aman (nonaktifkan fitur berbahaya, perbarui secara berkala).

## 3. Keamanan Service-to-Service dengan Mutual TLS (mTLS) via Service Mesh

*   **Masalah:** NetworkPolicy mengontrol *apakah* Pod A boleh bicara ke Pod B, tetapi tidak mengenkripsi traffic *di antara* mereka di dalam cluster. Seorang penyerang yang sudah berada di dalam jaringan cluster (misalnya, dengan mengkompromi Node atau Pod lain) mungkin dapat mengendus (sniffing) traffic internal ini.
*   **Solusi: Mutual TLS (mTLS):** Mekanisme di mana *kedua* belah pihak (klien dan server) saling mengautentikasi identitas satu sama lain menggunakan sertifikat digital dan kemudian mengenkripsi semua komunikasi di antara mereka.
*   **Peran Service Mesh (Istio, Linkerd):** Service mesh **mengotomatiskan** penerapan mTLS antar layanan secara transparan.
    *   Control Plane mesh bertindak sebagai Certificate Authority (CA) internal, menerbitkan sertifikat identitas beban kerja (misalnya, sesuai SPIFFE standard) ke setiap proxy sidecar.
    *   Proxy sidecar secara otomatis memulai koneksi mTLS dengan proxy sidecar lain saat berkomunikasi antar layanan.
    *   Aplikasi itu sendiri tidak perlu diubah untuk mendukung mTLS.
*   **Manfaat:**
    *   **Enkripsi Traffic Internal:** Melindungi data sensitif saat bergerak di dalam cluster.
    *   **Autentikasi Kuat:** Memastikan bahwa layanan hanya berbicara dengan layanan lain yang identitasnya terverifikasi.
    *   **Otorisasi Halus (Lapis Tambahan):** Setelah mTLS terbentuk, service mesh dapat menerapkan kebijakan otorisasi yang lebih halus (misalnya, hanya service 'A' yang boleh memanggil metode `GET /users` pada service 'B').
*   **Kapan Menggunakan:** Jika keamanan traffic internal adalah prioritas tinggi, terutama di lingkungan zero-trust atau multi-tenant, atau untuk memenuhi persyaratan kepatuhan yang ketat.

## 4. Mengamankan API Server

*   Meskipun bukan murni "jaringan Pod", mengamankan akses ke API Server sangat penting karena ia adalah otak cluster.
*   **Autentikasi Kuat:** Gunakan metode autentikasi yang aman (OIDC, Sertifikat Klien), hindari token/password statis.
*   **Otorisasi Ketat (RBAC):** Terapkan least privilege.
*   **Akses Jaringan Terbatas:** Jika memungkinkan, batasi akses jaringan ke endpoint API Server hanya dari jaringan tepercaya (misalnya, menggunakan firewall atau security group cloud provider).
*   **Aktifkan Audit Logging:** Pantau siapa melakukan apa terhadap API Server.

## 5. Keamanan DNS

*   Pastikan Pods CoreDNS (atau DNS internal lainnya) berjalan dengan aman (misalnya, di bawah profil `restricted` PSA).
*   Gunakan Network Policies untuk membatasi siapa yang dapat berkomunikasi dengan Pods DNS (biasanya semua Pod perlu akses UDP/TCP port 53 ke CoreDNS).
*   Pertimbangkan DNS over TLS (DoT) atau DNS over HTTPS (DoH) jika perlu mengenkripsi kueri DNS ke server upstream di luar cluster.

## Ringkasan

Keamanan jaringan di Kubernetes adalah pendekatan berlapis:

*   **Network Policies:** Mengontrol *siapa* bisa bicara dengan *siapa* di dalam cluster (L3/L4 Firewall).
*   **Ingress + TLS:** Mengamankan titik masuk HTTP/S dari luar cluster.
*   **Service Mesh (mTLS):** Mengenkripsi dan mengautentikasi komunikasi *antar* layanan di dalam cluster.
*   **Pengamanan API Server & DNS:** Melindungi komponen kontrol penting.

Menerapkan kombinasi dari kontrol ini, berdasarkan model ancaman dan kebutuhan keamanan spesifik Anda, akan membantu membangun lingkungan Kubernetes yang jauh lebih tangguh terhadap serangan berbasis jaringan.
