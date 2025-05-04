# Troubleshooting Masalah Performa Kubernetes

Masalah performa di Kubernetes dapat bermanifestasi dalam berbagai cara: aplikasi lambat merespons, throughput rendah, latensi tinggi, atau bahkan ketidakstabilan cluster. Mendiagnosis masalah performa seringkali lebih kompleks daripada masalah fungsional karena bisa melibatkan banyak faktor di berbagai lapisan (aplikasi, kontainer, Pod, Node, jaringan, storage, Control Plane).

**Pendekatan Umum:**

1.  **Definisikan Masalah Performa:** Apa metrik kunci yang menunjukkan masalah (latensi P99, throughput request, waktu pemrosesan batch)? Seberapa besar dampaknya? Kapan terjadinya (terus menerus, saat beban puncak, setelah perubahan)?
2.  **Identifikasi Bottleneck:** Di lapisan mana kemungkinan besar terjadi bottleneck? Aplikasi? Node (CPU/Memori/Disk/Network)? Jaringan antar Pod/Service? Storage? Control Plane?
3.  **Kumpulkan Metrik & Data:** Gunakan alat observability untuk mengumpulkan data kuantitatif tentang penggunaan resource dan performa di berbagai lapisan.
4.  **Analisis & Korelasi:** Cari korelasi antara metrik performa aplikasi yang buruk dengan metrik utilisasi sumber daya sistem atau komponen lain.

**Area Investigasi Umum & Alat Diagnostik:**

**1. Performa Aplikasi di Dalam Kontainer:**
   *   **Gejala:** Latensi aplikasi tinggi, throughput rendah, CPU/Memori tinggi di dalam Pod.
   *   **Diagnosa:**
        *   **Profiling Aplikasi:** Gunakan alat profiler spesifik bahasa pemrograman Anda (misalnya, `pprof` untuk Go, `cProfile`/`py-spy` untuk Python, VisualVM/JProfiler untuk Java, profiler .NET) untuk mengidentifikasi fungsi atau bagian kode yang memakan banyak CPU atau memori. Jalankan profiler via `kubectl exec`.
        *   **Analisis Log Aplikasi:** Cari pola log yang menunjukkan pemrosesan lambat, error berulang, atau antrian yang menumpuk.
        *   **Periksa Metrik Aplikasi Kustom (jika ada):** Lihat dashboard Grafana untuk latensi internal, tingkat error, ukuran antrian, dll.
        *   **Optimasi Kode:** Perbaiki algoritma yang tidak efisien, optimalkan query database, gunakan caching, implementasikan konkurensi/paralelisme dengan benar.
        *   **Periksa Dependensi:** Apakah aplikasi menunggu terlalu lama pada database, cache, atau layanan eksternal?

**2. Bottleneck Resource Pod (CPU/Memori):**
   *   **Gejala:** Aplikasi lambat, Pod di-OOMKill, CPU Throttling.
   *   **Diagnosa:**
        *   **Periksa Penggunaan Resource Pod:**
          ```bash
          # Memerlukan Metrics Server
          kubectl top pod <nama-pod> -n <namespace> --containers
          ```
        *   **Periksa Konfigurasi Request & Limit:**
          ```bash
          kubectl describe pod <nama-pod> -n <namespace> | grep -A3 Resources:
          ```
        *   **Periksa Metrik Detail (Prometheus/Grafana):** Lihat grafik historis `container_cpu_usage_seconds_total` (rate), `container_memory_working_set_bytes`, `container_cpu_cfs_throttled_periods_total` (rate).
        *   **Analisis CPU Throttling:** Jika metrik throttling tinggi, berarti `limits.cpu` Anda terlalu rendah untuk beban kerja aplikasi, atau ada masalah performa di aplikasi yang menyebabkan penggunaan CPU berlebihan.
        *   **Analisis OOMKill:** Jika Pod di-OOMKill (`describe pod` -> Reason: OOMKilled), berarti `limits.memory` terlalu rendah atau ada memory leak di aplikasi.
   *   **Solusi:**
        *   **Tuning Request/Limit:** Sesuaikan `requests` dan `limits` berdasarkan observasi penggunaan aktual (lihat [Praktik Terbaik Manajemen Resource](./../05-pola-praktik-terbaik/04-manajemen-resource.md)). Tingkatkan limit jika terjadi throttling/OOMKill yang tidak diinginkan.
        *   **Optimasi Aplikasi:** Kurangi penggunaan CPU/Memori oleh aplikasi.
        *   **Scaling Horizontal (HPA):** Jika aplikasi stateless, pertimbangkan untuk menambahkan lebih banyak replika Pod menggunakan HorizontalPodAutoscaler berdasarkan target CPU/Memori.

**3. Bottleneck Resource Node (CPU/Memori/Disk I/O/Network):**
   *   **Gejala:** Performa lambat untuk *semua* atau *banyak* Pod di Node tertentu, Node menjadi `NotReady`.
   *   **Diagnosa:**
        *   **Periksa Penggunaan Resource Node:**
          ```bash
          # Memerlukan Metrics Server
          kubectl top node <nama-node>
          kubectl describe node <nama-node> # Lihat bagian 'Allocated resources' vs 'Capacity'
          ```
        *   **Periksa Metrik Node Detail (Prometheus/Grafana via `node-exporter`):** Lihat CPU usage (per core, system, user, iowait), memory usage (total, available, buffers/cache), disk I/O (read/write bytes, iops, latency, utilization), network traffic (bytes/packets in/out).
        *   **Identifikasi Pod "Berisik":** Gunakan `kubectl top pod -n <namespace> --sort-by=cpu` atau `... --sort-by=memory` di semua namespace untuk menemukan Pods yang menggunakan resource paling banyak di Node tersebut.
   *   **Solusi:**
        *   **Pindahkan Beban Kerja:** Gunakan Taints/Tolerations atau Affinity untuk memindahkan Pods yang intensif resource ke Node lain atau Node yang lebih besar.
        *   **Tambah Kapasitas Node:** Tambahkan lebih banyak Node ke cluster atau tingkatkan ukuran Node (vertical scaling).
        *   **Optimalkan Pod "Berisik":** Atasi masalah performa atau sesuaikan request/limit Pod yang menggunakan resource berlebihan.
        *   **Periksa Disk I/O:** Jika `iowait` tinggi atau latensi disk tinggi, pertimbangkan untuk menggunakan tipe disk yang lebih cepat (misalnya, SSD) atau optimalkan pola I/O aplikasi.
        *   **Periksa Jaringan Node:** Jika traffic jaringan Node tinggi, periksa Pods mana yang menghasilkan traffic tersebut. Pertimbangkan CNI yang lebih performan atau jaringan Node yang lebih cepat.

**4. Masalah Latensi Jaringan Kubernetes:**
   *   **Gejala:** Latensi tinggi saat komunikasi antar Pods atau antara Pod dan Service.
   *   **Diagnosa:**
        *   **Ukur Latensi Antar Pod:** Gunakan `ping` (untuk RTT dasar) atau alat yang lebih canggih seperti `qperf` atau `iperf3` via `kubectl exec` antara Pods sumber dan tujuan (di Node yang sama vs. berbeda).
        *   **Ukur Latensi ke Service:** Ukur waktu respons saat menghubungi ClusterIP Service dari Pod lain. Bandingkan dengan waktu respons saat menghubungi IP Pod backend secara langsung. Perbedaan signifikan mungkin menunjukkan overhead pada `kube-proxy` atau lapisan jaringan Service.
        *   **Periksa Metrik CNI/Jaringan:** Beberapa plugin CNI (seperti Cilium) atau alat Service Mesh (Istio, Linkerd) menyediakan metrik latensi jaringan yang detail.
        *   **Periksa Beban `kube-proxy` / `iptables` / `IPVS`:** Di cluster besar dengan banyak Services/Endpoints, `kube-proxy` (terutama mode `iptables`) bisa menjadi bottleneck. Mode `IPVS` umumnya lebih scalable.
        *   **Periksa Network Policies:** Evaluasi NetworkPolicy dapat menambah sedikit overhead. Pastikan policy Anda efisien.
   *   **Solusi:**
        *   Optimalkan komunikasi aplikasi (misalnya, kurangi jumlah panggilan jaringan).
        *   Gunakan CNI yang lebih performan.
        *   Pertimbangkan mode `IPVS` untuk `kube-proxy`.
        *   Gunakan Service Mesh untuk fitur traffic management lanjutan (retries, timeouts) yang dapat menyembunyikan latensi sementara.
        *   Pastikan jaringan fisik/virtual antar Node memiliki latensi rendah.

**5. Masalah Performa Storage:**
   *   **Gejala:** Aplikasi lambat saat membaca/menulis ke Persistent Volume, throughput I/O rendah.
   *   **Diagnosa:**
        *   **Periksa Metrik Disk I/O Node:** Gunakan `node-exporter` dan Grafana untuk melihat metrik disk I/O pada Node tempat Pod dan PV terpasang (lihat poin 3).
        *   **Periksa Metrik Backend Storage:** Pantau performa (IOPS, throughput, latensi) dari sistem penyimpanan backend Anda (disk cloud, NFS, Ceph).
        *   **Uji Performa Volume:** Gunakan alat seperti `fio` atau `dd` via `kubectl exec` di dalam Pod untuk mengukur performa I/O langsung pada volume yang di-mount.
   *   **Solusi:**
        *   Gunakan tipe penyimpanan (StorageClass) yang lebih cepat/sesuai dengan kebutuhan I/O aplikasi Anda.
        *   Optimalkan pola I/O aplikasi (misalnya, caching, batching write).
        *   Pastikan tidak ada bottleneck pada jaringan jika menggunakan storage jaringan.

**6. Masalah Performa Control Plane (Self-Hosted):**
   *   **Gejala:** `kubectl` lambat, penjadwalan Pod lambat, update objek lambat, API Server tidak responsif.
   *   **Diagnosa:** Lihat [Troubleshooting Control Plane](./05-masalah-control-plane.md). Fokus pada metrik performa API Server, etcd (terutama latensi disk!), Scheduler, dan Controller Manager. Periksa penggunaan resource pada node Control Plane.
   *   **Solusi:** Tingkatkan resource node Control Plane, optimalkan performa etcd (disk lebih cepat, tuning), periksa query API yang berlebihan dari controller/aplikasi kustom.

Troubleshooting performa memerlukan pendekatan multi-lapisan dan penggunaan alat observability yang baik. Mulailah dari lapisan aplikasi, lalu bergerak ke bawah menuju Pod, Node, jaringan, dan storage, sambil terus mengumpulkan metrik dan mengkorelasikan data untuk menemukan bottleneck sebenarnya.
