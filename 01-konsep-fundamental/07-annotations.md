# Annotations: Catatan Tempel Metadata

Selain Labels, Kubernetes menyediakan mekanisme lain untuk melampirkan metadata ke objek: **Annotations**. Sama seperti Labels, Annotations adalah **pasangan key-value (kunci-nilai)** yang dapat Anda lampirkan ke objek pada bagian `metadata.annotations`.

## Apa Perbedaan Utama antara Annotations dan Labels?

Meskipun keduanya adalah pasangan key-value di `metadata`, mereka memiliki tujuan dan karakteristik yang berbeda:

| Fitur             | Labels (`metadata.labels`)                     | Annotations (`metadata.annotations`)                |
|-------------------|------------------------------------------------|---------------------------------------------------|
| **Tujuan Utama**  | **Identifikasi & Pemilihan (Selection)**       | **Metadata Non-Identifikasi**                     |
| **Digunakan oleh Selectors?** | **Ya** (inti dari cara kerja K8s)             | **Tidak** (tidak bisa digunakan utk memilih objek)|
| **Struktur Value**| Dibatasi (string, <= 63 karakter, aturan DNS) | Lebih Fleksibel (bisa string besar, JSON, dll.)* |
| **Ukuran Value**  | Relatif Kecil                                  | Bisa Lebih Besar* (tapi tetap ada batas ukuran objek K8s ~1MB) |
| **Target Pengguna**| Sistem K8s (Selectors), Manusia (Organisasi) | Alat Bantu (Tools), Library, Manusia (Deskripsi)  |

*) Meskipun value Annotations bisa lebih besar dan kompleks, praktik terbaiknya adalah menjaganya tetap ringkas. Jangan gunakan Annotations untuk menyimpan data besar yang seharusnya ada di database atau sistem file.

**Singkatnya:**

*   Gunakan **Labels** untuk data yang akan digunakan untuk **memilih atau mengelompokkan** objek.
*   Gunakan **Annotations** untuk informasi **tambahan** yang tidak digunakan untuk pemilihan, seringkali untuk keperluan alat bantu, debugging, atau deskripsi yang lebih panjang.

## Kasus Penggunaan Umum Annotations

Annotations digunakan secara luas oleh berbagai alat dan komponen dalam ekosistem Kubernetes:

*   **Informasi Deskriptif:** Menyimpan deskripsi panjang tentang objek, URL ke dokumentasi terkait, atau informasi kontak pemilik.
    *   `description: "Deployment utama untuk layanan otentikasi pengguna"`
    *   `contact-email: "sre-team@example.com"`
*   **Informasi Build/Rollout:**
    *   `kubernetes.io/change-cause`: Dicatat oleh `kubectl apply --record` (deprecated) atau `kubectl annotate` untuk melacak alasan perubahan pada Deployment. Digunakan oleh `kubectl rollout history`.
    *   `git-commit: "a1b2c3d4e5"`: Menyimpan commit hash dari build image.
    *   `build-timestamp: "2023-10-27T10:00:00Z"`
*   **Konfigurasi Alat Bantu (Tools):** Banyak alat menggunakan anotasi untuk mengkonfigurasi perilaku mereka terhadap objek tertentu.
    *   **Prometheus:** `prometheus.io/scrape: "true"`, `prometheus.io/path: "/metrics"`, `prometheus.io/port: "8080"` untuk menginstruksikan Prometheus agar men-scrape metrik dari Pod/Service.
    *   **Ingress Controllers:** Anotasi pada objek Ingress digunakan untuk mengkonfigurasi fitur spesifik controller (misalnya, `nginx.ingress.kubernetes.io/rewrite-target: /`, `cert-manager.io/cluster-issuer: letsencrypt-prod`).
    *   **ExternalDNS:** `external-dns.alpha.kubernetes.io/hostname: myapp.example.com.` untuk secara otomatis membuat record DNS.
    *   **Argo CD / Flux (GitOps):** Menggunakan anotasi untuk mengontrol sinkronisasi atau perilaku lainnya.
*   **Status atau Informasi Runtime:** Beberapa controller kustom mungkin menyimpan informasi status sementara atau pointer ke resource terkait dalam anotasi.
*   **Kebijakan atau Metadata Internal:** Informasi yang digunakan oleh admission controllers kustom atau logika bisnis internal.

## Contoh YAML dengan Annotations

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: frontend-deployment
  namespace: web
  labels:
    app: frontend
    tier: web
  annotations:
    # Deskripsi & Kontak
    description: "Deployment utama untuk frontend web e-commerce"
    owner: "frontend-team@example.com"
    documentation: "https://wiki.example.com/frontend-deployment"
    # Informasi Build & Rollout
    kubernetes.io/change-cause: "Upgrade to v2.5.1 - fix login bug"
    git-commit-sha: "f4b3a2d1"
    # Konfigurasi Tools
    prometheus.io/scrape: "true"
    prometheus.io/port: "80"
    external-dns.alpha.kubernetes.io/target: "elb-12345.example.com"
spec:
  replicas: 3
  selector:
    matchLabels:
      app: frontend
      tier: web
  template:
    metadata:
      labels:
        app: frontend
        tier: web
      annotations:
        # Anotasi bisa juga di level Pod Template
        sidecar.istio.io/inject: "true" # Contoh anotasi untuk service mesh Istio
    spec:
      containers:
      - name: frontend-app
        image: my-frontend:v2.5.1
        ports:
        - containerPort: 80
```

## Mengelola Annotations dengan `kubectl`

Sama seperti Labels, Anda dapat mengelola Annotations menggunakan `kubectl`:

*   **Menambahkan atau Memperbarui Anotasi:**
    ```bash
    kubectl annotate pod my-pod description="Pod aplikasi utama" --overwrite
    kubectl annotate deployment frontend-deployment contact="new-team@example.com" --overwrite
    # Gunakan --overwrite jika anotasi sudah ada
    ```
*   **Menghapus Anotasi:** Berikan nama anotasi diikuti tanda minus (`-`).
    ```bash
    kubectl annotate pod my-pod description-
    ```
*   **Melihat Anotasi:** Anotasi biasanya tidak ditampilkan oleh `kubectl get` default, tetapi terlihat di `kubectl describe` atau output YAML/JSON.
    ```bash
    kubectl describe pod my-pod
    kubectl get pod my-pod -o yaml
    ```

Annotations menyediakan cara yang fleksibel untuk menambahkan konteks dan metadata kaya ke objek Kubernetes Anda, terutama untuk integrasi dengan alat lain dan untuk menyimpan informasi yang tidak cocok untuk Labels.
