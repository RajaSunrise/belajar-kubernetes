# Detail Service Accounts: Identitas untuk Proses di Dalam Pod

Berbeda dengan "Normal Users" (manusia) yang identitasnya dikelola di luar Kubernetes, **Service Accounts (SA)** adalah jenis akun khusus yang dirancang untuk digunakan oleh **proses yang berjalan di dalam kontainer (Pods)**. SA menyediakan identitas bagi aplikasi atau sistem di dalam cluster untuk berinteraksi secara aman dengan Kubernetes API Server atau sistem eksternal lainnya.

## Mengapa Perlu Service Accounts?

Bayangkan sebuah Pod yang perlu melakukan tugas berikut:

*   Membaca ConfigMap yang berisi konfigurasinya.
*   Memantau Pod lain di namespace yang sama.
*   Membuat Job Kubernetes secara dinamis.
*   Berkomunikasi dengan API cloud provider untuk membuat sumber daya.

Agar dapat melakukan tindakan ini, proses di dalam Pod perlu **mengautentikasi** dirinya ke Kubernetes API Server (atau API eksternal) dan kemudian **diotorisasi** untuk melakukan tindakan tersebut. Service Account menyediakan mekanisme identitas dan kredensial standar untuk kasus penggunaan ini.

## Karakteristik Service Accounts

*   **Objek Kubernetes:** Service Accounts adalah objek API Kubernetes yang sebenarnya (`kind: ServiceAccount`, `apiVersion: v1`). Anda dapat membuat, mengelola, dan melihatnya menggunakan `kubectl`.
*   **Namespaced:** Service Accounts terikat pada Namespace tertentu. Setiap namespace memiliki Service Account default bernama `default`.
*   **Token Otomatis (Secara Default):** Kubernetes secara otomatis (kecuali dinonaktifkan) membuat kredensial berupa *token* (JSON Web Token - JWT) untuk setiap Service Account. Token ini disimpan dalam objek `Secret` tipe `kubernetes.io/service-account-token` (cara lama) atau dapat diminta secara dinamis melalui TokenRequest API (cara modern, menghasilkan token berjangka waktu).
*   **Mount Otomatis ke Pods:** Secara default (`automountServiceAccountToken: true`), token dari Service Account yang digunakan oleh Pod akan secara otomatis di-mount ke dalam setiap kontainer Pod di lokasi standar: `/var/run/secrets/kubernetes.io/serviceaccount/`. Lokasi ini berisi:
    *   `token`: File berisi token JWT Service Account.
    *   `ca.crt`: Sertifikat CA cluster untuk memverifikasi API Server.
    *   `namespace`: Nama namespace tempat Pod berjalan.
*   **Subjek RBAC:** Service Accounts dapat diberikan izin menggunakan RBAC (Role-Based Access Control) melalui `RoleBinding` atau `ClusterRoleBinding`, sama seperti Normal Users atau Groups. Nama subject untuk SA dalam RBAC adalah `system:serviceaccount:<namespace>:<service-account-name>`.

## Menggunakan Service Accounts pada Pods

Setiap Pod berjalan sebagai satu Service Account tertentu.

*   **Default:** Jika Anda tidak menentukan Service Account saat membuat Pod, Pod akan secara otomatis menggunakan Service Account bernama `default` di namespace tempat Pod tersebut dibuat.
*   **Menentukan Service Account:** Anda dapat secara eksplisit menentukan Service Account yang harus digunakan oleh Pod dengan field `spec.serviceAccountName` dalam definisi Pod. Pod hanya dapat menggunakan Service Account yang ada di **namespace yang sama**.

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: my-app-pod
  namespace: my-app-ns
spec:
  # Pod ini akan menggunakan ServiceAccount bernama 'my-app-sa'
  # yang harus sudah ada di namespace 'my-app-ns'
  serviceAccountName: my-app-sa
  containers:
    - name: my-app-container
      image: my-app:1.0
      # Token untuk 'my-app-sa' akan otomatis ter-mount ke
      # /var/run/secrets/kubernetes.io/serviceaccount/
      # jika automount tidak dinonaktifkan.
  # --- Opsi untuk menonaktifkan mount token otomatis ---
  # automountServiceAccountToken: false
```

## Token Service Account

Token yang di-mount ke Pod memungkinkan aplikasi di dalamnya untuk:

1.  **Membaca Token:** Aplikasi membaca file `token`.
2.  **Membuat Permintaan API:** Aplikasi membuat permintaan HTTPS ke Kubernetes API Server.
3.  **Menambahkan Header Otorisasi:** Aplikasi menambahkan header `Authorization: Bearer <token-yang-dibaca>` ke permintaan.
4.  **Autentikasi:** API Server menerima permintaan, memvalidasi tanda tangan JWT pada token menggunakan kunci publiknya, dan mengekstrak identitas Service Account (`system:serviceaccount:<namespace>:<name>`).
5.  **Otorisasi:** API Server kemudian memeriksa (melalui RBAC) apakah Service Account tersebut memiliki izin untuk melakukan tindakan yang diminta pada sumber daya yang dituju.

**Token Terikat (Bound Service Account Tokens - Fitur Modern):**
Versi Kubernetes yang lebih baru memperkenalkan token Service Account yang lebih aman:
*   **Berjangka Waktu:** Memiliki masa berlaku terbatas.
*   **Terikat Audience:** Hanya valid untuk digunakan terhadap audience (penerima) tertentu (misalnya, hanya API Server Kubernetes, bukan API lain).
*   **Terikat Objek:** Terikat pada objek spesifik seperti Pod.
*   Diminta melalui `TokenRequest` API, bukan hanya di-mount dari Secret statis.
*   Kubelet secara otomatis me-refresh token ini di dalam Pod sebelum kedaluwarsa. Ini adalah praktik yang lebih aman daripada token Secret yang tidak kedaluwarsa.

## `imagePullSecrets`

Salah satu penggunaan umum Service Account (meskipun tidak terkait langsung dengan akses API Server) adalah untuk menyediakan kredensial guna menarik (pull) image dari **private container registry**.

Anda dapat menambahkan referensi ke Secret tipe `kubernetes.io/dockerconfigjson` (yang berisi kredensial registry) ke field `imagePullSecrets` pada Service Account. *Setiap Pod yang menggunakan Service Account tersebut akan secara otomatis mewarisi `imagePullSecrets` ini*, memungkinkan Kubelet untuk mengautentikasi ke registry privat saat menarik image untuk Pod tersebut.

```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: builder-sa
  namespace: ci-cd
imagePullSecrets: # Pods yang pakai SA ini bisa pull dari 'my-private-registry'
- name: my-registry-secret # Nama Secret tipe dockerconfigjson
---
apiVersion: v1
kind: Pod
metadata:
  name: build-pod
  namespace: ci-cd
spec:
  serviceAccountName: builder-sa # Menggunakan SA di atas
  containers:
  - name: kaniko
    image: my-private-registry/kaniko-executor:latest # Image dari registry privat
    # ... args, command ...
```

## Praktik Terbaik Service Account

1.  **Buat Service Account Spesifik:** Jangan terlalu bergantung pada SA `default`. Buat SA terpisah untuk setiap aplikasi atau komponen yang memerlukan izin API yang berbeda.
2.  **Terapkan Hak Akses Minimum (Least Privilege):** Berikan hanya izin RBAC yang benar-benar diperlukan oleh proses di dalam Pod melalui SA-nya. Hindari memberikan izin luas seperti `cluster-admin` ke Service Accounts.
3.  **Nonaktifkan Mount Token Otomatis Jika Tidak Perlu:** Jika Pod tidak perlu berkomunikasi dengan API Server, set `automountServiceAccountToken: false` pada Pod `spec` atau pada Service Account itu sendiri. Ini mengurangi permukaan serangan jika Pod terkompromi.
4.  **Gunakan Token Terikat (Bound Tokens):** Manfaatkan fitur token modern yang berjangka waktu dan terikat audience jika didukung oleh versi K8s dan aplikasi klien Anda.
5.  **Kelola `imagePullSecrets` dengan Hati-hati:** Pastikan Secret kredensial registry aman dan hanya ditambahkan ke SA yang membutuhkannya.

Service Accounts adalah mekanisme identitas fundamental untuk beban kerja di dalam cluster Kubernetes, memungkinkan interaksi yang aman dan terkontrol dengan API Server dan sumber daya lainnya.
