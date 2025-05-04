# Praktik Terbaik: Konvensi Penamaan dan Pelabelan (Labels)

Meskipun Kubernetes fleksibel dalam hal penamaan dan pelabelan objek, menerapkan **konvensi yang konsisten** di seluruh cluster dan tim Anda sangat penting untuk:

*   **Keterbacaan & Pemahaman:** Memudahkan siapa saja untuk mengidentifikasi tujuan dan hubungan antar objek.
*   **Otomatisasi:** Memungkinkan pemilihan objek yang andal menggunakan label selectors untuk Services, Deployments, NetworkPolicies, monitoring, alerting, dll.
*   **Manajemen Kebijakan:** Menerapkan kebijakan (RBAC, NetworkPolicy, OPA/Kyverno) berdasarkan label.
*   **Manajemen Biaya:** Mengelompokkan dan melacak penggunaan sumber daya berdasarkan aplikasi, tim, atau lingkungan.
*   **Troubleshooting:** Memfilter log dan metrik berdasarkan label untuk mempersempit masalah.

## Konvensi Penamaan Objek (`metadata.name`)

Nama objek Kubernetes (Pods, Deployments, Services, dll.) harus unik dalam satu namespace (atau cluster-wide untuk objek non-namespaced).

*   **Deskriptif:** Nama harus mencerminkan tujuan objek. Hindari nama generik seperti `test`, `temp`, atau `service`.
*   **Konsisten:** Gunakan pola yang sama untuk objek terkait.
    *   **Pola Umum:** `<aplikasi>-<komponen>-<lingkungan>`
        *   Contoh Deployment: `frontend-web-prod`, `backend-api-staging`, `user-db-dev`
        *   Contoh Service: `frontend-web-svc-prod`, `backend-api-svc-staging`
        *   Contoh ConfigMap: `frontend-web-cm-prod`, `backend-api-cm-staging`
    *   Awalan atau akhiran yang jelas membantu mengelompokkan objek saat listing.
*   **Format:** Nama harus mengikuti [konvensi nama subdomain DNS](https://kubernetes.io/docs/concepts/overview/working-with-objects/names/#dns-subdomain-names):
    *   Maksimal 253 karakter.
    *   Hanya berisi karakter alfanumerik lowercase (`a-z`, `0-9`), tanda hubung (`-`), dan titik (`.`).
    *   Dimulai dan diakhiri dengan karakter alfanumerik.
*   **Hindari Nama Rilis Helm Secara Langsung (Jika Terlalu Panjang/Generik):** Jika menggunakan Helm, nama objek seringkali menyertakan nama rilis (misalnya, `release-name-chart-name-component`). Pertimbangkan menggunakan `fullnameOverride` di `values.yaml` atau helper `fullname` yang terstruktur di `_helpers.tpl` untuk menghasilkan nama yang lebih bersih dan lebih dapat diprediksi jika nama rilis terlalu panjang atau kurang deskriptif.

## Konvensi Pelabelan (`metadata.labels`)

Labels adalah key-value pairs yang dilampirkan ke objek untuk mengidentifikasi atribut yang relevan bagi pengguna tetapi tidak secara langsung bermakna bagi sistem inti. Labels adalah **perekat utama** di Kubernetes, digunakan oleh selectors.

*   **Gunakan Label Standar yang Direkomendasikan:** Kubernetes merekomendasikan serangkaian [label standar](https://kubernetes.io/docs/concepts/overview/working-with-objects/common-labels/) untuk mendeskripsikan aplikasi secara konsisten. Sangat disarankan untuk mengadopsi ini:
    *   **`app.kubernetes.io/name`**: Nama aplikasi (misalnya, `mysql`, `nginx`, `my-web-app`).
    *   **`app.kubernetes.io/instance`**: Nama instance unik yang membedakan aplikasi ini (misalnya, nama rilis Helm: `my-web-app-prod-abcde`). Ini penting jika Anda men-deploy aplikasi yang sama beberapa kali.
    *   **`app.kubernetes.io/version`**: Versi aplikasi saat ini (misalnya, `5.7.21`, `1.19.0`, tag Git).
    *   **`app.kubernetes.io/component`**: Komponen dalam arsitektur Anda (misalnya, `database`, `web`, `api`, `cache`).
    *   **`app.kubernetes.io/part-of`**: Nama aplikasi tingkat lebih tinggi yang merupakan bagian dari aplikasi ini (misalnya, `wordpress`).
    *   **`app.kubernetes.io/managed-by`**: Alat yang digunakan untuk mengelola aplikasi (misalnya, `helm`, `kustomize`, `argocd`).
*   **Tambahkan Label Spesifik Organisasi/Tim:** Selain label standar, tambahkan label yang relevan untuk konteks Anda:
    *   **`environment`**: Lingkungan deployment (`dev`, `staging`, `production`, `qa`).
    *   **`team` / `owner`**: Tim atau individu yang bertanggung jawab.
    *   **`tier`**: Lapisan arsitektur (misalnya, `frontend`, `backend`, `data`).
    *   **`project`**: Nama proyek terkait.
    *   **`cost-center`**: Untuk pelacakan biaya.
*   **Konsisten dalam Penggunaan:** Terapkan set label yang sama (atau subset yang relevan) ke semua objek yang terkait dengan satu aplikasi (Deployment, StatefulSet, Service, Pods, ConfigMap, Secret, Ingress, dll.). Ini memudahkan pemilihan semua resource terkait.
    *   **Khususnya:** Label pada `spec.template.metadata.labels` di dalam Deployment/StatefulSet/dll. **harus cocok** dengan `spec.selector.matchLabels` agar controller dapat menemukan Pods yang dikelolanya. Praktik yang baik adalah menggunakan set label yang sama di kedua tempat, ditambah mungkin label tambahan (seperti `version`) pada template Pod.
*   **Format Kunci dan Nilai:**
    *   Kunci bisa memiliki prefix namespace opsional (`mycompany.com/cost-center`). Prefix direkomendasikan untuk label spesifik organisasi. Kunci tanpa prefix dianggap privat bagi pengguna.
    *   Nama kunci (bagian setelah prefix, atau seluruh kunci jika tanpa prefix) dan nilai harus:
        *   Maksimal 63 karakter.
        *   Hanya berisi karakter alfanumerik (`a-z`, `A-Z`, `0-9`), tanda hubung (`-`), underscore (`_`), dan titik (`.`).
        *   Dimulai dan diakhiri dengan karakter alfanumerik.
*   **Jangan Gunakan Terlalu Banyak Label Unik:** Hindari menggunakan label untuk menyimpan data yang sangat dinamis atau unik per Pod (seperti timestamp atau ID request). Ini dapat membebani etcd dan sistem query. Gunakan **Annotations** untuk metadata semacam itu.
*   **Dokumentasikan Konvensi Anda:** Dokumentasikan konvensi penamaan dan pelabelan yang Anda pilih dan pastikan semua tim mengikutinya.

**Contoh Set Label yang Baik untuk Pod/Deployment:**

```yaml
metadata:
  name: my-app-backend-prod
  labels:
    app.kubernetes.io/name: my-app
    app.kubernetes.io/instance: my-app-backend-prod-a1b2c3d4 # Misal dari Helm release
    app.kubernetes.io/version: "v2.5.1"
    app.kubernetes.io/component: backend-api
    app.kubernetes.io/part-of: my-app
    app.kubernetes.io/managed-by: helm
    environment: production
    team: backend-devs
    tier: backend
```

Menerapkan konvensi penamaan dan pelabelan yang disiplin mungkin terasa seperti pekerjaan tambahan di awal, tetapi akan sangat terbayar dalam jangka panjang dengan membuat cluster Kubernetes Anda lebih mudah dipahami, dikelola, diamankan, dan diotomatisasi.
