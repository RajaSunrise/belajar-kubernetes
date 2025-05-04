# Metodologi Umum Troubleshooting Kubernetes

Menghadapi masalah di sistem terdistribusi seperti Kubernetes bisa terasa menakutkan pada awalnya. Namun, dengan pendekatan yang sistematis dan pemahaman tentang alat yang tersedia, Anda dapat mendiagnosis dan menyelesaikan sebagian besar masalah secara efektif.

Metodologi umum troubleshooting melibatkan langkah-langkah berikut:

**1. Observasi & Pengumpulan Informasi Awal:**
   *   **Definisikan Masalah:** Apa yang *sebenarnya* terjadi? Apa perilaku yang diharapkan vs. perilaku aktual? Kapan masalah mulai terjadi? Apakah konsisten atau intermiten? Seberapa luas dampaknya (satu Pod, satu Node, seluruh cluster)?
   *   **Periksa Status Tingkat Tinggi:** Mulailah dengan perintah `kubectl get` untuk melihat status objek yang relevan (Pods, Deployments, Services, Nodes, PVCs, dll.). Perhatikan kolom `STATUS`, `READY`, `RESTARTS`, `AGE`.
     ```bash
     kubectl get pods -n <namespace> -o wide
     kubectl get deployments -n <namespace>
     kubectl get services -n <namespace>
     kubectl get nodes -o wide
     kubectl get events -n <namespace> --sort-by='.lastTimestamp' # SANGAT PENTING!
     ```
   *   **Periksa Events:** Events Kubernetes seringkali memberikan petunjuk pertama tentang apa yang salah (misalnya, `FailedScheduling`, `FailedMount`, `FailedSync`, `Unhealthy`, `ImagePullBackOff`). Selalu periksa events terbaru untuk namespace atau objek yang bermasalah.

**2. Persempit Lingkup Masalah:**
   *   Apakah masalah terjadi pada satu Pod atau semua replika? (Menunjukkan masalah Pod vs. konfigurasi/dependensi).
   *   Apakah masalah terjadi pada satu Node atau banyak Node? (Menunjukkan masalah Node vs. masalah cluster-wide).
   *   Apakah masalah hanya terjadi di satu Namespace? (Menunjukkan masalah konfigurasi/RBAC/Quota namespace).
   *   Apakah masalah terjadi setelah perubahan terakhir (deployment baru, perubahan konfigurasi)?

**3. Gali Lebih Dalam dengan `kubectl describe`:**
   *   Ini adalah **alat diagnostik terpenting** Anda. `kubectl describe <jenis-objek> <nama-objek> -n <namespace>` memberikan informasi detail tentang konfigurasi objek, statusnya saat ini, dan (yang terpenting) **Events** terbaru yang terkait langsung dengan objek tersebut.
   *   Periksa bagian `Conditions` (jika ada) dan `Events` di bagian bawah output `describe`. Ini seringkali menjelaskan *mengapa* objek berada dalam state tertentu (misalnya, mengapa Pod `Pending` atau `NotReady`).
     ```bash
     kubectl describe pod <nama-pod> -n <namespace>
     kubectl describe deployment <nama-deployment> -n <namespace>
     kubectl describe node <nama-node>
     kubectl describe pvc <nama-pvc> -n <namespace>
     ```

**4. Periksa Log:**
   *   **Log Aplikasi (Kontainer):** Jika Pod berjalan tetapi aplikasi tidak berfungsi, periksa lognya.
     ```bash
     kubectl logs <nama-pod> -n <namespace>
     kubectl logs <nama-pod> -c <nama-kontainer> -n <namespace> # Jika multi-kontainer
     kubectl logs -f <nama-pod> -n <namespace> # Streaming log
     kubectl logs --previous <nama-pod> -n <namespace> # Log dari kontainer yg crash sebelumnya
     ```
   *   **Log Komponen Sistem:** Jika masalah diduga berasal dari infrastruktur K8s (terutama pada cluster self-hosted), periksa log komponen Control Plane (API Server, Scheduler, Controller Manager, etcd) atau komponen Node (Kubelet, Kube-proxy, Container Runtime). Lokasi log bervariasi (sering di `/var/log` atau via `journalctl`).
     ```bash
     # Contoh untuk Kubelet (jika systemd)
     sudo journalctl -u kubelet -f
     # Contoh untuk API Server (jika berjalan sebagai Pod)
     kubectl logs kube-apiserver-<nama-node> -n kube-system
     ```

**5. Uji Konektivitas & Fungsionalitas Langsung:**
   *   **Exec ke Dalam Pod:** Gunakan `kubectl exec` untuk menjalankan perintah diagnostik (seperti `ping`, `curl`, `nslookup`, `ps`, `env`) di dalam kontainer yang sedang berjalan untuk menguji konektivitas jaringan atau memeriksa state internal aplikasi.
     ```bash
     kubectl exec -it <nama-pod> -n <namespace> -- /bin/sh # Atau /bin/bash
     # Di dalam shell Pod:
     # curl http://<nama-service-lain>: <port>
     # nslookup <nama-service>
     # ping <ip-pod-lain>
     # env | grep MY_VAR
     ```
   *   **Port Forward:** Gunakan `kubectl port-forward` untuk menghubungkan port lokal Anda langsung ke port pada Pod atau Service. Ini berguna untuk mengakses aplikasi secara langsung tanpa melalui Service/Ingress atau untuk debugging koneksi database.
     ```bash
     # Forward port lokal 8080 ke port 80 di Pod
     kubectl port-forward pod/<nama-pod> 8080:80 -n <namespace>
     # Forward port lokal 9000 ke port 80 pada Service
     kubectl port-forward svc/<nama-service> 9000:80 -n <namespace>
     # Sekarang akses http://localhost:8080 atau http://localhost:9000 dari browser/curl lokal Anda
     ```

**6. Bentuk Hipotesis & Uji:**
   *   Berdasarkan informasi yang dikumpulkan, bentuk hipotesis tentang kemungkinan penyebab masalah (misalnya, "Mungkin NetworkPolicy memblokir traffic", "Mungkin Pod kehabisan memori", "Mungkin selector Service salah").
   *   Uji hipotesis Anda. Lakukan perubahan kecil dan terisolasi (jika aman) atau gunakan alat diagnostik lebih lanjut untuk memvalidasi atau menyangkal hipotesis.

**7. Cari Dokumentasi & Komunitas:**
   *   Jika Anda terjebak, cari pesan error spesifik atau deskripsi masalah di dokumentasi Kubernetes resmi, GitHub issues proyek terkait, Stack Overflow (tag: kubernetes), atau forum komunitas lainnya. Seringkali orang lain pernah mengalami masalah serupa.

**8. Periksa Perubahan Terbaru:**
   *   Apakah masalah muncul setelah deployment baru? Gunakan `kubectl rollout history` dan `kubectl rollout undo` jika perlu.
   *   Apakah ada perubahan konfigurasi cluster atau Node baru-baru ini?

**9. Pertimbangkan Ketergantungan:**
   *   Apakah aplikasi Anda bergantung pada layanan eksternal atau layanan lain di dalam cluster? Pastikan dependensi tersebut berjalan dan dapat dijangkau.

**Alat Bantu Penting:**

*   `kubectl get`: Melihat status ringkasan.
*   `kubectl describe`: Melihat detail dan events. **Gunakan ini secara ekstensif!**
*   `kubectl logs`: Melihat output aplikasi.
*   `kubectl exec`: Menjalankan perintah di dalam kontainer.
*   `kubectl port-forward`: Mengakses Pod/Service secara langsung.
*   `kubectl top pod`/`kubectl top node`: Melihat penggunaan resource dasar (memerlukan Metrics Server).
*   Alat Observability: Dashboard Grafana (metrik), Kibana/Grafana (log), Jaeger/Tempo (trace).
*   Alat Diagnostik Jaringan: `ping`, `curl`, `wget`, `telnet`, `nslookup`, `dig`, `traceroute` (dijalankan via `kubectl exec`).
*   (Opsional) Alat seperti `k9s` atau `Lens` dapat mempercepat proses observasi dan interaksi.

Dengan mengikuti metodologi ini dan memanfaatkan alat yang tepat, Anda dapat secara signifikan mengurangi waktu yang dibutuhkan untuk mendiagnosis dan menyelesaikan masalah di lingkungan Kubernetes. Ingatlah untuk selalu memeriksa **Events** terlebih dahulu!
