# Pod Security Admission (PSA): Menegakkan Standar Keamanan Pod

Menjalankan kontainer dengan privilege berlebih merupakan risiko keamanan signifikan di Kubernetes. Meskipun `SecurityContext` memungkinkan definisi kontrol privilege per Pod/Container, bagaimana cara memastikan bahwa *semua* Pod yang dibuat di cluster (atau dalam namespace tertentu) mematuhi standar keamanan minimum? Di sinilah **Pod Security Admission (PSA)** berperan.

PSA adalah **admission controller** bawaan Kubernetes (aktif secara default di versi modern) yang menerapkan **Pod Security Standards (PSS)** pada Pod saat mereka dibuat atau diperbarui.

## Apa itu Pod Security Standards (PSS)?

PSS adalah sekumpulan **standar keamanan pre-defined** yang mengkategorikan tingkat keamanan Pod. Ada tiga standar (atau profil) utama:

1.  **`privileged` (Paling Tidak Aman):**
    *   Kebijakan yang sangat permisif. Pada dasarnya tidak memberlakukan batasan keamanan apa pun.
    *   Memungkinkan eskalasi privilege yang diketahui.
    *   **Tujuan:** Untuk beban kerja tingkat sistem atau infrastruktur tepercaya yang memang memerlukan akses tingkat tinggi, atau untuk migrasi dari lingkungan yang kurang aman. **Harus digunakan dengan sangat hati-hati dan terbatas.**

2.  **`baseline` (Keamanan Dasar):**
    *   Kebijakan "cukup aman" yang bertujuan untuk mencegah eskalasi privilege yang *umum diketahui*.
    *   Melarang penggunaan `hostNetwork`, `hostPID`, `hostIPC`, volume `hostPath` yang berbahaya, kontainer `privileged: true`, dll.
    *   Membutuhkan beberapa `SecurityContext` dasar (misalnya, membatasi capabilities).
    *   **Tujuan:** Standar minimum yang direkomendasikan untuk sebagian besar beban kerja non-kritis. Mudah diadopsi.

3.  **`restricted` (Paling Aman):**
    *   Kebijakan yang sangat membatasi, mengikuti praktik terbaik keamanan Pod saat ini.
    *   Mencakup semua batasan `baseline` dan menambahkan persyaratan lebih ketat, seperti:
        *   Harus berjalan sebagai non-root (`runAsNonRoot: true`).
        *   Harus menonaktifkan eskalasi privilege (`allowPrivilegeEscalation: false`).
        *   Harus menghapus *semua* Linux capabilities (`drop: ["ALL"]`) dan hanya menambahkan yang diizinkan secara eksplisit (biasanya tidak ada yang diizinkan secara default).
        *   Membutuhkan profil Seccomp (`RuntimeDefault` atau lebih baik).
    *   **Tujuan:** Untuk beban kerja yang sangat peduli keamanan dan dapat berjalan dengan set privilege yang sangat terbatas. Mungkin memerlukan penyesuaian aplikasi atau konfigurasi Pod.

## Bagaimana Pod Security Admission (PSA) Bekerja?

PSA berfungsi sebagai *admission controller* yang mencegat permintaan pembuatan atau pembaruan Pod ke API Server. Ia memeriksa spesifikasi Pod terhadap standar PSS yang dikonfigurasi untuk Namespace tempat Pod akan dibuat.

**Konfigurasi PSA dilakukan melalui LABEL pada objek `Namespace`:**

Anda menerapkan label khusus pada metadata Namespace untuk menentukan standar PSS mana yang harus diterapkan dan dalam mode apa:

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: my-secure-namespace
  labels:
    # --- Label Konfigurasi PSA ---
    # Mode: enforce - Tolak Pod yang tidak sesuai standar 'restricted'.
    pod-security.kubernetes.io/enforce: restricted
    # Versi standar PSS yang akan ditegakkan (opsional, default ke 'latest').
    pod-security.kubernetes.io/enforce-version: v1.28

    # Mode: audit - Catat peringatan di log audit jika Pod tidak sesuai 'baseline'.
    pod-security.kubernetes.io/audit: baseline
    # Versi standar PSS untuk diaudit.
    pod-security.kubernetes.io/audit-version: v1.28

    # Mode: warn - Tampilkan peringatan ke pengguna (via kubectl) jika Pod tidak sesuai 'baseline'.
    pod-security.kubernetes.io/warn: baseline
    # Versi standar PSS untuk diperingatkan.
    pod-security.kubernetes.io/warn-version: v1.28
    # -----------------------------
```

**Mode Penerapan:**

*   **`enforce`:** Kebijakan yang paling ketat. Jika Pod tidak memenuhi standar yang ditentukan, permintaan pembuatan/pembaruan Pod akan **ditolak** oleh API Server.
*   **`audit`:** Jika Pod tidak memenuhi standar yang ditentukan, pelanggaran akan **dicatat dalam log audit** API Server (jika audit logging diaktifkan), tetapi Pod tetap diizinkan dibuat/diperbarui. Berguna untuk memahami dampak kebijakan sebelum menerapkannya (`enforce`).
*   **`warn`:** Jika Pod tidak memenuhi standar yang ditentukan, **peringatan akan ditampilkan kepada pengguna** yang membuat/memperbarui Pod (misalnya, di output `kubectl apply`), tetapi Pod tetap diizinkan dibuat/diperbarui. Berguna untuk memberitahu pengguna tentang praktik terbaik.

**Versi Standar (`<mode>-version`):**
Anda dapat (dan sebaiknya) menentukan versi PSS yang ingin Anda gunakan (misalnya, `v1.28`). Ini memastikan bahwa perilaku kebijakan tetap konsisten bahkan jika standar PSS diperbarui di versi Kubernetes mendatang. Jika tidak ditentukan, akan menggunakan `latest`.

**Konfigurasi Cluster-Wide (Opsional):**
Selain label Namespace, administrator cluster dapat mengkonfigurasi standar PSS default dan pengecualian (exemptions) untuk Namespace sistem (seperti `kube-system`) dalam file konfigurasi Admission Controller di API Server.

## Mengapa PSA Penting?

*   **Keamanan Default:** Menyediakan mekanisme bawaan untuk menegakkan praktik keamanan Pod dasar di seluruh cluster atau per namespace.
*   **Menggantikan PodSecurityPolicy (PSP):** PSA adalah pengganti yang lebih sederhana dan lebih mudah dikelola untuk PodSecurityPolicy (PSP) yang telah *dihapus* mulai Kubernetes v1.25.
*   **Kemudahan Penggunaan:** Konfigurasi melalui label Namespace relatif mudah dipahami dan diterapkan.
*   **Fleksibilitas Mode:** Mode `warn` dan `audit` memungkinkan penerapan bertahap dan analisis dampak sebelum memberlakukan (`enforce`) kebijakan yang ketat.

## Strategi Penerapan PSA

1.  **Audit Namespace yang Ada:** Mulailah dengan menerapkan label `audit=baseline` dan `warn=baseline` pada namespace yang ada untuk melihat Pod mana yang mungkin tidak memenuhi standar dasar. Analisis log audit dan peringatan.
2.  **Terapkan `baseline`:** Setelah analisis, terapkan `enforce=baseline` pada sebagian besar namespace aplikasi. Ini memberikan peningkatan keamanan yang signifikan dengan usaha adopsi yang relatif rendah.
3.  **Identifikasi Beban Kerja untuk `restricted`:** Identifikasi aplikasi atau namespace yang memerlukan keamanan lebih tinggi dan dapat berjalan di bawah batasan profil `restricted`. Uji coba secara menyeluruh.
4.  **Terapkan `restricted`:** Terapkan `enforce=restricted` pada namespace yang membutuhkan keamanan maksimum. Bersiaplah untuk menyesuaikan `SecurityContext` Pod jika diperlukan.
5.  **Gunakan `privileged` dengan Sangat Terbatas:** Hanya terapkan `enforce=privileged` pada namespace di mana benar-benar diperlukan (misalnya, namespace sistem tertentu yang sudah dikecualikan secara default, atau namespace khusus untuk beban kerja infrastruktur tepercaya) dan pahami risikonya.
6.  **Tentukan Versi Standar:** Selalu gunakan label `*-version` untuk memastikan prediktabilitas.

Pod Security Admission adalah lapisan pertahanan penting dalam model keamanan Kubernetes, membantu memastikan bahwa Pod berjalan dengan privilege seminimal mungkin sesuai dengan standar keamanan yang telah ditentukan.
