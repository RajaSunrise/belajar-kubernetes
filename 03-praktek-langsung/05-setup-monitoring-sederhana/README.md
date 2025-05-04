# Lab 05: Setup Monitoring Dasar dengan Prometheus & Grafana (via Helm)

**Tujuan:** Lab ini menunjukkan cara cepat untuk men-setup tumpukan (stack) monitoring dasar di cluster Kubernetes Anda menggunakan Prometheus (untuk pengumpulan metrik & alerting) dan Grafana (untuk visualisasi dashboard). Kita akan menggunakan Helm chart `kube-prometheus-stack` yang populer, yang menyederhanakan proses instalasi secara signifikan.

**Konsep yang Dipelajari:**

*   Pentingnya monitoring di Kubernetes.
*   Peran Prometheus (scraping, TSDB, PromQL, alerting) dan Grafana (dashboard).
*   Menggunakan Helm untuk menginstal paket aplikasi yang kompleks.
*   Menambahkan repositori Helm.
*   Menginstal chart `kube-prometheus-stack`.
*   Memverifikasi komponen monitoring (Prometheus, Grafana, Alertmanager, Node Exporter, Kube State Metrics).
*   Mengakses UI Prometheus dan Grafana (via `port-forward`).
*   Menjelajahi target scrape Prometheus.
*   Mengimpor dan melihat dashboard Grafana bawaan untuk Kubernetes.

**Prasyarat:**

*   Cluster Kubernetes lokal berjalan (Minikube, Kind, K3s, Docker Desktop).
*   `kubectl` terinstal dan terkonfigurasi.
*   **Helm v3** terinstal. (Verifikasi dengan `helm version`). Jika belum, instal dari [helm.sh](https://helm.sh/docs/intro/install/).
*   Koneksi internet untuk mengunduh Helm chart dan image kontainer.
*   **Sumber Daya Cluster yang Cukup:** Stack monitoring ini bisa memakan resource (terutama Prometheus & Grafana). Pastikan cluster lokal Anda memiliki setidaknya 2 CPU dan 4GB RAM yang dialokasikan (lebih banyak lebih baik).

**Catatan:** `kube-prometheus-stack` adalah chart yang sangat komprehensif dan menginstal banyak komponen, termasuk Prometheus Operator, yang mengelola Prometheus/Alertmanager via CRD. Untuk lab ini, kita akan fokus pada penggunaan dasar, bukan konfigurasi mendalam operator itu sendiri.

## Langkah 1: Membuat Namespace

Kita akan menginstal stack monitoring di namespace terpisah.

```bash
kubectl create namespace monitoring
kubectl config set-context --current --namespace=monitoring
```

## Langkah 2: Menambahkan Repositori Helm Prometheus Community

Chart `kube-prometheus-stack` dikelola oleh komunitas Prometheus.

```bash
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update
```

## Langkah 3: Menginstal Chart `kube-prometheus-stack`

Kita akan menginstal chart dengan nama rilis `prom-stack` di namespace `monitoring`.

```bash
# Instal dengan konfigurasi default (mungkin cukup untuk lab lokal)
helm install prom-stack prometheus-community/kube-prometheus-stack --namespace monitoring

# Perintah di atas akan menginstal:
# - Prometheus Operator
# - Prometheus (dikelola oleh Operator via CRD Prometheus)
# - Alertmanager (dikelola oleh Operator via CRD Alertmanager)
# - Grafana (dengan sumber data Prometheus sudah dikonfigurasi)
# - node-exporter (DaemonSet untuk metrik Node OS)
# - kube-state-metrics (Deployment untuk metrik state objek K8s)
# - Berbagai Service, ConfigMap, Secrets, Roles, Bindings, dll.
```

Instalasi ini mungkin memakan waktu beberapa menit karena perlu menarik banyak image kontainer.

**Kustomisasi (Opsional):** Untuk lingkungan nyata, Anda mungkin ingin mengkustomisasi instalasi (misalnya, mengaktifkan Ingress untuk Grafana/Prometheus, mengkonfigurasi penyimpanan persisten, menyesuaikan resource limits). Ini dilakukan dengan membuat file `values.yaml` kustom dan menggunakannya saat instalasi: `helm install ... -f my-values.yaml`. Lihat [dokumentasi chart](https://github.com/prometheus-community/helm-charts/tree/main/charts/kube-prometheus-stack) untuk semua opsi konfigurasi.

## Langkah 4: Verifikasi Instalasi

Tunggu beberapa menit hingga semua Pods dimulai dan menjadi `Ready`.

```bash
# Lihat semua Pods di namespace monitoring
kubectl get pods -n monitoring -w

# Setelah semua Running/Completed, periksa objek utama:
kubectl get prometheus -n monitoring # Harus ada 'prom-stack-kube-prom-prometheus'
kubectl get alertmanager -n monitoring # Harus ada 'prom-stack-kube-prom-alertmanager'
kubectl get deployment -n monitoring # Akan ada grafana, kube-state-metrics, operator
kubectl get daemonset -n monitoring # Akan ada node-exporter
kubectl get service -n monitoring # Akan ada service untuk grafana, prometheus, alertmanager, dll.
```
Pastikan Pods utama (prometheus-..., grafana-..., alertmanager-..., node-exporter-..., kube-state-metrics-...) dalam status `Running`.

## Langkah 5: Mengakses UI Prometheus

Kita gunakan `port-forward` untuk mengakses UI Prometheus dari mesin lokal.

```bash
# Service Prometheus biasanya bernama <release-name>-kube-prom-prometheus
# Ganti jika nama rilis Anda berbeda dari 'prom-stack'
kubectl port-forward svc/prom-stack-kube-prom-prometheus 9090:9090 -n monitoring
# Biarkan terminal ini berjalan
```

Buka browser Anda dan navigasi ke `http://localhost:9090`.

Di UI Prometheus:
*   Klik menu **Status -> Targets**. Anda akan melihat daftar target yang secara otomatis ditemukan oleh Prometheus (node-exporter, kube-state-metrics, apiserver, grafana, dll.). Statusnya harus `UP`.
*   Klik menu **Graph**. Coba masukkan kueri PromQL sederhana seperti `up` atau `rate(container_cpu_usage_seconds_total[1m])` dan klik **Execute**.

## Langkah 6: Mengakses UI Grafana

Grafana juga diinstal oleh chart ini.

1.  **Dapatkan Password Admin Grafana:** Password default biasanya disimpan dalam Secret.
    ```bash
    kubectl get secret prom-stack-grafana -n monitoring -o jsonpath="{.data.admin-password}" | base64 --decode ; echo
    # (Ganti 'prom-stack-grafana' jika nama service/secret Grafana Anda berbeda)
    # Catat password ini. Username default adalah 'admin'.
    ```
2.  **Port-forward ke Service Grafana:**
    ```bash
    # Buka terminal BARU
    # Service Grafana biasanya bernama <release-name>-grafana
    kubectl port-forward svc/prom-stack-grafana 3000:80 -n monitoring
    # Biarkan terminal ini berjalan
    ```
3.  **Login ke Grafana:** Buka browser Anda dan navigasi ke `http://localhost:3000`. Login dengan username `admin` dan password yang Anda dapatkan dari Secret. Anda akan diminta untuk mengubah password pada login pertama.
4.  **Jelajahi Dashboard Bawaan:** Chart `kube-prometheus-stack` menyertakan beberapa dashboard Kubernetes yang sangat berguna secara default.
    *   Klik ikon "Dashboards" (empat kotak) di menu kiri.
    *   Jelajahi folder seperti "Kubernetes / Compute Resources / Cluster", "Kubernetes / Compute Resources / Namespace (Pods)", "Kubernetes / Compute Resources / Node (Pods)", dll.
    *   Lihat visualisasi penggunaan CPU, Memori, Jaringan, Disk untuk cluster, node, dan pod Anda.

## Langkah 7: Pembersihan

```bash
# Hentikan proses port-forward (Ctrl+C di terminalnya)

# Uninstall Helm release
helm uninstall prom-stack --namespace monitoring

# Tunggu beberapa saat, lalu hapus CRD (jika tidak ada Operator lain yg pakai)
# kubectl delete crd prometheuses.monitoring.coreos.com alertmanagers.monitoring.coreos.com ... (lihat dokumentasi chart untuk daftar CRD)

# Kembali ke namespace default
# kubectl config set-context --current --namespace=default

# Hapus namespace monitoring (akan menghapus semua resource tersisa)
kubectl delete namespace monitoring
```

**Selamat!** Anda telah berhasil men-deploy stack monitoring dasar menggunakan Prometheus dan Grafana via Helm. Ini adalah titik awal yang bagus untuk mulai memantau kesehatan dan performa cluster Kubernetes Anda. Anda dapat memperluasnya dengan menambahkan exporter kustom, alert, dan dashboard yang lebih spesifik.
