# Praktik Terbaik: Keamanan Kubernetes

Keamanan di Kubernetes adalah tanggung jawab berlapis yang melibatkan pengamanan infrastruktur cluster, platform Kubernetes itu sendiri, dan aplikasi yang berjalan di atasnya. Ini sering dirangkum sebagai "4C" Keamanan Cloud Native: Cloud/Corporate Datacenter, Cluster, Container, dan Code.

Berikut adalah praktik terbaik keamanan fundamental yang perlu diterapkan pada level **Cluster** dan **Container/Code** saat menggunakan Kubernetes:

**1. Terapkan Prinsip Hak Akses Minimum (Least Privilege) dengan RBAC**
   *   **RBAC (Role-Based Access Control)** adalah mekanisme otorisasi utama. Konfigurasikan `Roles`, `ClusterRoles`, `RoleBindings`, dan `ClusterRoleBindings` untuk memberikan izin seminimal mungkin yang diperlukan oleh pengguna, grup, atau **Service Accounts**.
   *   **Hindari `cluster-admin`:** Jangan memberikan peran `cluster-admin` secara sembarangan. Gunakan peran bawaan `admin`, `edit`, `view` yang terbatas pada namespace jika memungkinkan.
   *   **Gunakan Roles Namespaced:** Lebih pilih `Role` dan `RoleBinding` (terbatas pada namespace) daripada `ClusterRole` dan `ClusterRoleBinding` (berlaku cluster-wide) kecuali jika akses global benar-benar diperlukan.
   *   **Batasi Izin Service Account:** Service Accounts digunakan oleh Pods untuk berinteraksi dengan API Server. Berikan mereka izin seminimal mungkin melalui `Roles` atau `ClusterRoles`. Nonaktifkan mounting token otomatis (`automountServiceAccountToken: false` pada Pod atau ServiceAccount) jika Pod tidak memerlukan akses API.
   *   **Audit RBAC Secara Berkala:** Tinjau izin secara teratur.

**2. Gunakan Namespaces untuk Isolasi (Logis & Kebijakan)**
   *   Gunakan Namespaces untuk memisahkan lingkungan (dev, staging, prod), tim, atau aplikasi.
   *   Terapkan kebijakan (RBAC, NetworkPolicy, ResourceQuota, LimitRange) pada level Namespace untuk mengontrol akses dan sumber daya.
   *   Ingat: Namespaces *tidak* memberikan isolasi keamanan jaringan atau runtime yang kuat secara default; Anda perlu NetworkPolicies dan Security Contexts.

**3. Amankan Jaringan Cluster dengan Network Policies**
   *   Secara default, semua Pods dalam cluster dapat berkomunikasi satu sama lain. Ini seringkali terlalu permisif.
   *   Gunakan objek `NetworkPolicy` untuk membuat aturan firewall L3/L4 antar Pods dan Namespaces.
   *   **Terapkan Kebijakan Default Deny:** Mulailah dengan kebijakan default deny untuk ingress dan egress di setiap namespace, lalu secara eksplisit izinkan hanya traffic yang diperlukan antar aplikasi/tier.
   *   Gunakan label selector untuk menentukan Pods mana yang tunduk pada kebijakan dan Pods/Namespaces/IP mana yang diizinkan untuk berkomunikasi dengannya.
   *   Ini memerlukan plugin CNI (Container Network Interface) yang mendukung NetworkPolicy (seperti Calico, Cilium, Weave Net).

**4. Konfigurasi Security Contexts untuk Pods dan Kontainer**
   *   Gunakan `securityContext` pada level Pod atau Kontainer untuk mengontrol privilege dan isolasi proses.
   *   **Jalankan sebagai Non-Root:** Praktik paling penting! Set `securityContext.runAsNonRoot: true` dan `securityContext.runAsUser: <UID_NON_ROOT>` (misalnya > 1000). Hindari menjalankan kontainer sebagai user `root` (UID 0). Ini secara signifikan mengurangi dampak jika kontainer disusupi.
   *   **Filesystem Read-Only:** Jika memungkinkan, set `securityContext.readOnlyRootFilesystem: true` dan gunakan volume (`emptyDir`, PVC) untuk path yang memerlukan penulisan.
   *   **Batasi Privilege Escalation:** Set `securityContext.allowPrivilegeEscalation: false` untuk mencegah proses mendapatkan lebih banyak hak akses daripada proses induknya.
   *   **Drop Capabilities:** Hapus Linux capabilities yang tidak diperlukan oleh aplikasi Anda. Mulailah dengan `securityContext.capabilities.drop: ["ALL"]` lalu tambahkan hanya kapabilitas yang benar-benar dibutuhkan (`securityContext.capabilities.add: ["NET_BIND_SERVICE"]` jika perlu bind ke port < 1024 sebagai non-root, meskipun lebih baik menggunakan port > 1024).
   *   **Gunakan Seccomp, AppArmor, SELinux:** Manfaatkan profil keamanan Linux ini (jika didukung oleh OS Node dan runtime) melalui anotasi atau field `securityContext` (`seLinuxOptions`, `seccompProfile`, `appArmorProfile`) untuk lebih membatasi panggilan sistem (syscalls) yang dapat dilakukan oleh proses kontainer.

**5. Terapkan Standar Keamanan Pod (Pod Security Admission)**
   *   PSA (pengganti PodSecurityPolicy) adalah admission controller bawaan yang menerapkan standar keamanan Pod di level Namespace.
   *   Konfigurasikan label pada Namespace (misalnya, `pod-security.kubernetes.io/enforce: restricted`) untuk menerapkan profil keamanan:
        *   `privileged`: Tidak ada batasan (jangan gunakan kecuali benar-benar diperlukan).
        *   `baseline`: Mencegah eskalasi privilege yang diketahui, menerapkan beberapa batasan keamanan dasar.
        *   `restricted`: Sangat terbatas, mengikuti praktik terbaik keamanan Pod saat ini (misalnya, runAsNonRoot, drop ALL capabilities).
   *   Terapkan profil `restricted` atau `baseline` sebisa mungkin. Gunakan mode `audit` atau `warn` untuk transisi.

**6. Amankan Supply Chain Kontainer Anda**
   *   **Gunakan Image Terpercaya:** Gunakan image dasar resmi dan minimalis. Hindari image acak dari registry publik.
   *   **Pindai Image untuk Kerentanan:** Integrasikan pemindai image (seperti Trivy, Clair, Snyk, atau fitur bawaan registry Anda) ke dalam pipeline CI Anda untuk mendeteksi kerentanan keamanan yang diketahui dalam dependensi OS dan aplikasi sebelum deployment. Perbaiki atau mitigasi kerentanan berisiko tinggi.
   *   **Gunakan Image Immutable:** Beri tag versi spesifik pada image Anda (hindari `:latest`). Pastikan image yang sama digunakan di semua lingkungan.
   *   **Pertimbangkan Penandatanganan Image (Image Signing):** Gunakan alat seperti Cosign untuk menandatangani image Anda secara kriptografis. Konfigurasikan policy engine (seperti Kyverno atau Gatekeeper) untuk memverifikasi tanda tangan image sebelum mengizinkan Pod dijalankan, memastikan integritas dan asal image.

**7. Manajemen Secrets yang Aman**
   *   Gunakan objek `Secret` Kubernetes, bukan ConfigMap atau env vars plain text, untuk data sensitif.
   *   Aktifkan enkripsi etcd at-rest.
   *   Batasi akses RBAC ke Secrets.
   *   **Jangan commit secret plain text ke Git.** Gunakan SOPS, Helm Secrets, atau solusi manajemen secret eksternal (Vault, KMS Cloud, Secrets Store CSI Driver, External Secrets Operator).
   *   Lebih pilih mount Secret sebagai **volume file read-only** daripada environment variables.
   *   Rotasi secrets secara berkala.

**8. Jaga Komponen Kubernetes Tetap Terbarui**
   *   Secara teratur update cluster Kubernetes Anda (Control Plane dan Kubelet) ke versi patch terbaru untuk mendapatkan perbaikan keamanan dan bug. Ikuti kebijakan dukungan versi Kubernetes.
   *   Update komponen add-on (CNI, CoreDNS, Ingress Controller, dll.) secara teratur.

**9. Aktifkan dan Konfigurasi Audit Logging**
   *   Aktifkan [Audit Logs](https://kubernetes.io/docs/tasks/debug/debug-cluster/audit/) pada API Server. Log ini mencatat siapa melakukan apa, kapan, dan ke mana pada API Kubernetes.
   *   Konfigurasikan kebijakan audit yang sesuai untuk menangkap event yang relevan (terutama permintaan yang mengubah state atau akses sensitif).
   *   Kirim log audit ke sistem logging terpusat untuk analisis dan penyimpanan jangka panjang.

**10. Amankan API Server**
    *   Batasi akses jaringan ke API Server hanya dari sumber yang tepercaya.
    *   Gunakan autentikasi yang kuat (misalnya, OIDC, sertifikat) daripada metode yang lebih lemah.
    *   Konfigurasikan otorisasi (RBAC) dengan benar.

Keamanan adalah proses berkelanjutan, bukan tujuan akhir. Menerapkan praktik terbaik ini di berbagai lapisan akan secara signifikan mengurangi permukaan serangan dan meningkatkan postur keamanan cluster Kubernetes dan aplikasi Anda.
