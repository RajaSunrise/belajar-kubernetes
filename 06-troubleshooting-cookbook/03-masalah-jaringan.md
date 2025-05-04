# Troubleshooting Masalah Jaringan Kubernetes

Masalah jaringan bisa menjadi salah satu area yang paling membingungkan untuk di-debug di Kubernetes karena melibatkan banyak lapisan abstraksi (CNI, kube-proxy, CoreDNS, Services, Ingress, Network Policies). Berikut adalah pendekatan untuk mendiagnosis masalah jaringan umum:

**Alat Diagnostik Utama:**

*   `kubectl exec -it <source-pod> -n <ns> -- /bin/sh`: Menjalankan perintah dari dalam Pod sumber.
*   Perintah Jaringan (via `kubectl exec`): `ping`, `curl`, `wget`, `telnet`, `nc` (netcat), `nslookup`, `dig`. Pastikan image Pod Anda memiliki alat ini (gunakan image debug seperti `busybox`, `netshoot`, atau tambahkan ke image Anda).
*   `kubectl logs <pod> -n <ns>`: Untuk Pods aplikasi, CoreDNS, Ingress Controller, agen CNI, kube-proxy.
*   `kubectl describe <service|ingress|networkpolicy|pod|endpoints> ...`: Memeriksa konfigurasi dan Events.
*   `kubectl get endpoints <service-name> -n <ns>`: Memverifikasi apakah Service menemukan Pods backend yang benar.

## Masalah 1: Pod-ke-Pod Lain di Namespace yang Sama Tidak Bisa Berkomunikasi

**Skenario:** Pod A tidak bisa mencapai Pod B pada IP Pod B, padahal mereka berada di namespace yang sama.

**Diagnosa:**

1.  **Verifikasi IP Pod Tujuan:** Dapatkan IP Pod B: `kubectl get pod <pod-b> -o wide -n <namespace>`.
2.  **Test Konektivitas dari Pod Sumber:**
    ```bash
    kubectl exec -it <pod-a> -n <namespace> -- ping <ip-pod-b> # Tes L3
    kubectl exec -it <pod-a> -n <namespace> -- curl -v http://<ip-pod-b>:<port-pod-b> # Tes L4/L7
    kubectl exec -it <pod-a> -n <namespace> -- telnet <ip-pod-b> <port-pod-b> # Tes koneksi TCP
    ```
3.  **Periksa Network Policies:** Apakah ada NetworkPolicy di namespace tersebut yang mungkin memblokir traffic egress dari Pod A atau ingress ke Pod B?
    ```bash
    kubectl get networkpolicy -n <namespace>
    kubectl describe networkpolicy <nama-policy> -n <namespace>
    ```
    Periksa `podSelector` pada policy dan aturan `ingress`/`egress`. Hapus atau sesuaikan policy untuk pengujian (jika aman).
4.  **Periksa Masalah CNI:** (Lebih jarang) Jika konektivitas dasar antar Pod di Node yang sama atau berbeda gagal, mungkin ada masalah dengan plugin CNI (misalnya, konfigurasi, agen CNI crash). Periksa log agen CNI (seringkali DaemonSet di `kube-system`) dan log Kubelet di Node yang terlibat.

## Masalah 2: Pod Tidak Bisa Mencapai Service (ClusterIP) di Namespace yang Sama/Lain

**Skenario:** Pod A mencoba menghubungi `http://my-service:port` atau `http://my-service.target-ns.svc.cluster.local:port` tetapi gagal (timeout, connection refused).

**Diagnosa:**

1.  **Verifikasi Service:**
    *   Apakah Service ada? `kubectl get service my-service -n <target-ns>`
    *   Apakah Service memiliki ClusterIP? `kubectl describe service my-service -n <target-ns>`
    *   **Apakah Selector Service Benar?** `kubectl describe service my-service -n <target-ns>`. Pastikan `Selector:` cocok dengan label Pods backend yang diinginkan.
    *   **Apakah Endpoints Terisi?** `kubectl get endpoints my-service -n <target-ns>`. **Ini krusial!** Jika kolom `ENDPOINTS` kosong atau `<none>`, berarti Service tidak menemukan Pods backend yang `Ready` (atau selector salah). Jika kosong, periksa:
        *   Apakah ada Pods backend yang berjalan dengan label yang cocok? `kubectl get pods -l <selector-key>=<selector-value> -n <target-ns>`
        *   Apakah Pods backend tersebut `Ready` (lulus `readinessProbe`)? `kubectl get pods -l ...` (lihat kolom `READY`). Jika tidak ready, debug Pod tersebut.
2.  **Verifikasi DNS dari Dalam Pod:**
    ```bash
    kubectl exec -it <pod-a> -n <namespace> -- nslookup my-service # Jika di ns yg sama
    kubectl exec -it <pod-a> -n <namespace> -- nslookup my-service.target-ns # Jika di ns lain
    kubectl exec -it <pod-a> -n <namespace> -- nslookup my-service.target-ns.svc.cluster.local
    ```
    *   Haruskah me-resolve ke ClusterIP Service. Jika gagal, lihat [Masalah 3: DNS Resolution Gagal](#masalah-3-dns-resolution-gagal).
3.  **Test Konektivitas ke ClusterIP dari Pod:**
    ```bash
    # Dapatkan ClusterIP dari 'kubectl get svc my-service -n target-ns'
    kubectl exec -it <pod-a> -n <namespace> -- curl -v http://<cluster-ip-service>:<service-port>
    kubectl exec -it <pod-a> -n <namespace> -- telnet <cluster-ip-service> <service-port>
    ```
    *   Jika DNS resolve tapi koneksi ke ClusterIP gagal, masalah kemungkinan ada di `kube-proxy` atau Network Policy.
4.  **Periksa Network Policies:** Apakah ada NetworkPolicy yang memblokir egress dari Pod A ke ClusterIP Service atau ingress dari Pod A ke Pods backend? Periksa policy di namespace Pod A dan namespace Pod B (`target-ns`).
5.  **Periksa `kube-proxy`:** (Lebih jarang) Pastikan Pod `kube-proxy` berjalan di semua Node (`kubectl get pods -n kube-system -l k8s-app=kube-proxy`). Periksa lognya jika dicurigai ada masalah dalam memprogram aturan `iptables`/`IPVS`.

## Masalah 3: DNS Resolution Gagal di Dalam Pod

**Skenario:** `nslookup my-service` atau `curl http://my-service` gagal dengan error DNS (misalnya, `server can't find my-service`, `Could not resolve host`).

**Diagnosa:**

1.  **Periksa Konfigurasi DNS Pod:**
    ```bash
    kubectl exec -it <pod-a> -n <namespace> -- cat /etc/resolv.conf
    ```
    *   Periksa baris `nameserver`. Ini harus menunjuk ke **ClusterIP dari Service `kube-dns`** (biasanya di namespace `kube-system`).
    *   Periksa baris `search`. Ini harus mencakup domain pencarian seperti `<namespace>.svc.cluster.local`, `svc.cluster.local`, `cluster.local`, dan domain host. Ini memungkinkan Anda menggunakan nama pendek (`my-service`) dalam namespace yang sama.
2.  **Verifikasi Service `kube-dns`:**
    ```bash
    kubectl get service kube-dns -n kube-system
    ```
    Pastikan ia memiliki ClusterIP.
3.  **Verifikasi Pods CoreDNS (atau KubeDNS):**
    ```bash
    kubectl get pods -n kube-system -l k8s-app=kube-dns
    ```
    *   Pastikan Pods CoreDNS `Running` dan `Ready`. Jika tidak, `describe` dan periksa `logs` Pods CoreDNS tersebut. Mungkin ada masalah konfigurasi atau resource.
4.  **Test Langsung ke Server DNS Cluster:**
    ```bash
    # Dapatkan ClusterIP kube-dns
    CLUSTER_DNS_IP=$(kubectl get service kube-dns -n kube-system -o jsonpath='{.spec.clusterIP}')
    kubectl exec -it <pod-a> -n <namespace> -- nslookup my-service.target-ns.svc.cluster.local $CLUSTER_DNS_IP
    ```
    *   Jika ini berhasil tetapi resolusi normal gagal, masalah mungkin ada di konfigurasi `/etc/resolv.conf` Pod atau `search domains`.
5.  **Periksa Network Policies:** Apakah ada NetworkPolicy yang memblokir traffic egress dari Pod Anda ke Pods CoreDNS pada port UDP/TCP 53?
6.  **Periksa Konfigurasi CoreDNS:** (Lebih lanjut) Periksa ConfigMap CoreDNS (`kubectl get configmap coredns -n kube-system -o yaml`) untuk memastikan konfigurasinya benar (misalnya, plugin `kubernetes`, `forward` ke upstream DNS).

## Masalah 4: Tidak Bisa Mengakses Aplikasi dari Luar Cluster via Ingress

**Skenario:** Anda mencoba mengakses `http://my-app.example.com` tetapi mendapatkan error 5xx, 404, atau timeout.

**Diagnosa:**

1.  **Verifikasi DNS Eksternal:** Pastikan nama domain (`my-app.example.com`) me-resolve ke **alamat IP eksternal dari Ingress Controller Anda** (biasanya IP Load Balancer atau IP Node jika menggunakan NodePort). Gunakan `nslookup` atau `dig` dari mesin *di luar* cluster.
2.  **Verifikasi Ingress Controller:**
    *   Apakah Pods Ingress Controller (misalnya, Nginx Ingress, Traefik) berjalan dan `Ready`? `kubectl get pods -n <ingress-namespace>`
    *   Apakah Service Ingress Controller (biasanya tipe `LoadBalancer` atau `NodePort`) memiliki `EXTERNAL-IP` (untuk LoadBalancer) atau port yang benar? `kubectl get service -n <ingress-namespace>`
    *   Periksa **log** Pods Ingress Controller. Ini seringkali berisi detail tentang request yang masuk, backend yang dipilih, dan error yang terjadi.
3.  **Verifikasi Resource Ingress:**
    *   Apakah resource `Ingress` ada dan dikonfigurasi dengan benar? `kubectl get ingress -n <app-namespace>`
    *   `kubectl describe ingress <ingress-name> -n <app-namespace>`: Periksa `Rules` (host, path), `Backend` (service name, service port), `Annotations` (penting untuk konfigurasi spesifik Ingress Controller), dan `Events`. Pastikan `ADDRESS` diisi (menunjukkan Ingress Controller telah mengambilnya).
4.  **Verifikasi Service Backend:** Pastikan Service yang dirujuk dalam aturan Ingress (`spec.rules[].http.paths[].backend.service`) ada, memiliki Endpoints yang terisi, dan dapat diakses dari dalam cluster (ikuti langkah-langkah di [Masalah 2](#masalah-2-pod-tidak-bisa-mencapai-service-clusterip-di-namespace-yang-samalain)).
5.  **Periksa Network Policies:** Apakah ada NetworkPolicy yang memblokir ingress dari Pods Ingress Controller ke Pods aplikasi backend Anda?
6.  **Periksa Konfigurasi Spesifik Ingress Controller:** Baca dokumentasi Ingress Controller yang Anda gunakan. Mungkin ada anotasi spesifik yang diperlukan untuk TLS, rewrite, atau fitur lainnya.

## Masalah 5: NetworkPolicy Memblokir Traffic yang Seharusnya Diizinkan

**Skenario:** Anda yakin Pod A seharusnya bisa mencapai Pod B, tetapi koneksi gagal, dan Anda mencurigai NetworkPolicy.

**Diagnosa:**

1.  **Identifikasi Policy yang Berlaku:** Cari NetworkPolicy di namespace Pod sumber (untuk aturan `egress`) dan di namespace Pod tujuan (untuk aturan `ingress`) yang `podSelector`-nya cocok dengan Pod yang relevan.
    ```bash
    kubectl get networkpolicy -n <source-ns>
    kubectl get networkpolicy -n <target-ns>
    ```
2.  **Analisis Aturan Policy:**
    *   Untuk policy **ingress** pada Pod tujuan: Periksa bagian `ingress.from`. Apakah ada aturan yang mengizinkan traffic dari `podSelector` Pod sumber, `namespaceSelector`, atau `ipBlock` yang cocok? Jika tidak ada bagian `ingress`, secara default semua ingress diizinkan *kecuali* ada policy lain yang menargetkan Pod yang sama. Jika bagian `ingress` ada tapi kosong (`ingress: {}`), semua ingress ditolak.
    *   Untuk policy **egress** pada Pod sumber: Periksa bagian `egress.to`. Apakah ada aturan yang mengizinkan traffic ke `podSelector` Pod tujuan, `namespaceSelector`, atau `ipBlock` yang cocok? Periksa juga `ports` jika port spesifik dibatasi. Jika tidak ada bagian `egress`, semua egress diizinkan. Jika `egress: {}`, semua egress ditolak.
3.  **Gunakan Alat Bantu (Opsional):** Beberapa alat/plugin CNI (seperti Calico dengan `calicoctl`, Cilium dengan `cilium monitor`) menyediakan alat bantu untuk men-debug atau memvisualisasikan aliran traffic dan evaluasi policy.
4.  **Uji dengan Menghapus/Mengubah Policy:** Untuk sementara hapus atau sederhanakan policy yang dicurigai untuk melihat apakah konektivitas pulih. **Lakukan ini dengan hati-hati di lingkungan produksi.**

Troubleshooting jaringan Kubernetes memerlukan pendekatan lapisan demi lapisan: mulai dari DNS, ke Service, ke Endpoints, ke konektivitas Pod-ke-Pod, dan akhirnya memeriksa aturan NetworkPolicy. Menggunakan `kubectl exec` untuk menjalankan alat diagnostik dari perspektif Pod sumber sangatlah berharga.
