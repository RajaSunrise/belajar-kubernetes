# Metrics Server: Sumber Metrik Resource Dasar

Salah satu kebutuhan paling dasar dalam mengelola cluster Kubernetes adalah mengetahui berapa banyak sumber daya (CPU dan Memori) yang sedang digunakan oleh Node dan Pods. Informasi ini penting untuk:

*   **Penskalaan Otomatis (Autoscaling):** Terutama untuk `HorizontalPodAutoscaler` (HPA), yang menyesuaikan jumlah replika Pod berdasarkan target penggunaan CPU atau Memori.
*   **Penjadwalan (Scheduling):** Membantu Scheduler membuat keputusan yang lebih baik dengan mengetahui penggunaan aktual Node.
*   **Pemantauan Dasar:** Memberikan gambaran cepat tentang utilisasi resource melalui perintah seperti `kubectl top`.

Di sinilah **Metrics Server** berperan.

## Apa itu Metrics Server?

Metrics Server adalah **aggregator metrik sumber daya *in-memory* skala cluster**. Tugas utamanya adalah mengumpulkan metrik penggunaan CPU dan Memori dasar dari **semua Kubelet** di setiap Node dan menyajikannya melalui **Metrics API** Kubernetes (`metrics.k8s.io`).

**Penting untuk Dibedakan:**

*   Metrics Server **berbeda** dari sistem monitoring penuh seperti **Prometheus**.
*   Metrics Server hanya menyimpan metrik **saat ini** (in-memory), bukan data historis.
*   Metrics Server hanya menyediakan metrik **inti** (CPU & Memori), bukan metrik aplikasi kustom atau metrik infrastruktur mendalam lainnya.

Metrics Server adalah komponen opsional, tetapi **sangat direkomendasikan** dan seringkali menjadi **prasyarat** untuk fungsionalitas seperti HPA berbasis CPU/Memori dan `kubectl top`.

## Bagaimana Metrics Server Bekerja?

1.  **Deployment:** Metrics Server biasanya di-deploy sebagai `Deployment` dengan satu atau lebih replika di namespace `kube-system`.
2.  **Penemuan Kubelet:** Pod Metrics Server menemukan semua Node di cluster melalui API Server.
3.  **Scraping Metrik:** Secara berkala (misalnya, setiap 60 detik), Metrics Server menghubungi endpoint `/metrics/resource` pada **summary API** Kubelet di setiap Node. Kubelet menyediakan data penggunaan CPU dan Memori terbaru untuk Node itu sendiri dan semua Pods yang berjalan di atasnya (data ini biasanya berasal dari cAdvisor yang terintegrasi dengan Kubelet).
4.  **Agregasi:** Metrics Server mengagregasi data yang dikumpulkan dari semua Kubelet.
5.  **Menyajikan Metrics API:** Metrics Server mendaftarkan dirinya ke API Server utama sebagai *API Aggregation Layer* untuk menyajikan API `metrics.k8s.io`.
6.  **Konsumsi Metrik:** Komponen lain seperti HPA controller atau `kubectl top` kemudian dapat membuat kueri ke API `metrics.k8s.io` (yang dilayani oleh Metrics Server) untuk mendapatkan data penggunaan CPU/Memori terbaru untuk Pods atau Nodes.

## Instalasi Metrics Server

Metrics Server tidak selalu terinstal secara default di semua distribusi Kubernetes. Cara instalasinya bisa bervariasi:

*   **Manifest YAML:** Cara paling umum adalah mengunduh manifest YAML resmi dari repositori [kubernetes-sigs/metrics-server](https://github.com/kubernetes-sigs/metrics-server) dan menerapkannya:
    ```bash
    # Selalu periksa versi terbaru yang kompatibel dengan versi K8s Anda!
    kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml
    ```
    **Catatan Penting:** Terkadang, manifest default perlu sedikit dimodifikasi (terutama argumen `--kubelet-insecure-tls` atau konfigurasi terkait CA Kubelet) tergantung pada bagaimana Kubelet di cluster Anda dikonfigurasi. Lihat [FAQ dan dokumentasi Metrics Server](https://github.com/kubernetes-sigs/metrics-server#readme) untuk detail troubleshooting umum.
*   **Addon Minikube/MicroK8s:** Beberapa alat seperti Minikube dan MicroK8s menyediakan addon untuk menginstal Metrics Server dengan mudah:
    ```bash
    minikube addons enable metrics-server
    # atau
    microk8s enable metrics-server
    ```
*   **Helm Chart:** Ada juga Helm chart yang tersedia.

**Verifikasi Instalasi:**

Setelah beberapa saat (perlu waktu untuk menarik image dan memulai), periksa apakah Pod Metrics Server berjalan:

```bash
kubectl get pods -n kube-system -l k8s-app=metrics-server
# Output harus menunjukkan Pod dalam status Running dan Ready (mis: 1/1)
```

Anda juga bisa memeriksa apakah Metrics API sudah terdaftar:

```bash
kubectl api-services | grep metrics.k8s.io
# Output harus menunjukkan service 'v1beta1.metrics.k8s.io' dengan AVAILABLE=True
```

## Menggunakan `kubectl top`

Setelah Metrics Server berjalan dan mengumpulkan data (mungkin perlu satu atau dua menit setelah startup), Anda dapat menggunakan perintah `kubectl top`:

*   **Melihat Penggunaan Resource Node:**
    ```bash
    kubectl top nodes
    # OUTPUT (Contoh):
    # NAME             CPU(cores)   CPU%   MEMORY(bytes)   MEMORY%
    # kind-control-plane   157m         7%     1455Mi          37%
    # kind-worker          47m          2%     727Mi           18%
    # kind-worker2         39m          1%     698Mi           18%
    ```
*   **Melihat Penggunaan Resource Pods (di namespace default):**
    ```bash
    kubectl top pods
    # OUTPUT (Contoh):
    # NAME                             CPU(cores)   MEMORY(bytes)
    # my-nginx-app-6dff4549b8-5z5qf   1m           10Mi
    # my-nginx-app-6dff4549b8-h9k7l   1m           10Mi
    ```
*   **Melihat Penggunaan Resource Pods di Namespace Tertentu:**
    ```bash
    kubectl top pods -n monitoring
    ```
*   **Melihat Penggunaan Resource Kontainer di Dalam Pod:**
    ```bash
    kubectl top pod <nama-pod> --containers
    ```

Nilai yang ditampilkan oleh `kubectl top` adalah penggunaan **saat ini** berdasarkan data terakhir yang dikumpulkan oleh Metrics Server.

## Troubleshooting

*   **`kubectl top` error "Metrics API not available"**: Pastikan Pod Metrics Server berjalan dan API service `metrics.k8s.io` tersedia (`kubectl api-services`).
*   **`kubectl top` tidak menampilkan data / menampilkan 0**: Metrics Server mungkin baru saja dimulai dan belum mengumpulkan data, atau ada masalah komunikasi antara Metrics Server dan Kubelet (seringkali terkait TLS/konfigurasi jaringan). Periksa log Pod Metrics Server: `kubectl logs -n kube-system -l k8s-app=metrics-server`. Sesuaikan argumen deployment Metrics Server jika perlu (lihat dokumentasi Metrics Server).

Metrics Server adalah komponen dasar yang penting untuk observability dan autoscaling di Kubernetes, menyediakan data penggunaan resource fundamental melalui Metrics API standar.
