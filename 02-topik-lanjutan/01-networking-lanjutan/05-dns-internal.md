# DNS Internal Kubernetes (CoreDNS)

Di dalam cluster Kubernetes, bagaimana sebuah Pod menemukan alamat IP dari `Service` lain? Atau bahkan alamat IP Pod lain (dalam kasus tertentu seperti StatefulSets)? Jawabannya adalah melalui sistem **DNS internal cluster**.

Mekanisme DNS ini memungkinkan aplikasi untuk merujuk ke layanan lain menggunakan nama DNS yang stabil dan dapat diprediksi, daripada harus mengelola alamat IP ClusterIP Service yang bisa saja berubah (meskipun jarang) atau alamat IP Pod yang pasti berubah.

## Komponen Utama: CoreDNS

Implementasi DNS internal default dan paling umum digunakan di Kubernetes saat ini adalah **CoreDNS**.

*   **Deployment CoreDNS:** CoreDNS biasanya dijalankan sebagai `Deployment` (dengan beberapa replika untuk ketersediaan tinggi) di namespace `kube-system`.
*   **Service CoreDNS:** Ada juga sebuah `Service` (biasanya bernama `kube-dns`) di namespace `kube-system` yang mengekspos Pods CoreDNS tadi. Service ini memiliki ClusterIP yang stabil.
*   **Konfigurasi Kubelet:** Setiap Kubelet di Worker Node dikonfigurasi (biasanya melalui argumen `--cluster-dns=<IP_Service_kube-dns>`) untuk memberi tahu setiap Pod baru agar menggunakan ClusterIP dari Service `kube-dns` sebagai nameserver mereka. Ini biasanya dilakukan dengan mengkonfigurasi file `/etc/resolv.conf` di dalam setiap kontainer Pod.

**Bagaimana Cara Kerjanya?**

1.  **Pod Membuat Kueri DNS:** Ketika sebuah Pod (misalnya, `frontend-pod`) perlu menghubungi Service bernama `backend-svc` di namespace `myapp-ns`, ia akan membuat kueri DNS untuk nama seperti `backend-svc.myapp-ns.svc.cluster.local`.
2.  **Kueri ke CoreDNS:** Konfigurasi `/etc/resolv.conf` di `frontend-pod` mengarahkan kueri ini ke ClusterIP dari Service `kube-dns`.
3.  **CoreDNS Menjawab:** Pods CoreDNS menerima kueri tersebut. CoreDNS dikonfigurasi (melalui ConfigMap bernama `coredns` di `kube-system`) untuk mengawasi API Server Kubernetes.
    *   Ia akan mencari `Service` bernama `backend-svc` di namespace `myapp-ns`.
    *   Jika ditemukan, CoreDNS akan mengembalikan **ClusterIP** dari Service tersebut sebagai jawaban (record A).
4.  **Pod Menghubungi ClusterIP:** `frontend-pod` sekarang tahu ClusterIP dari `backend-svc` dan dapat mengirim lalu lintas ke alamat IP tersebut. Seperti yang kita tahu, `kube-proxy` kemudian akan mencegat lalu lintas ini dan mengarahkannya ke salah satu Pod backend yang sehat.

## Format Nama DNS Internal

Kubernetes secara otomatis membuat record DNS untuk Services dan Pods (dalam kondisi tertentu) dengan format yang dapat diprediksi:

**1. Untuk Services:**

*   **Format:** `<service-name>.<namespace-name>.svc.<cluster-domain>`
*   **Contoh:** `my-nginx.production.svc.cluster.local`
*   **Resolves to:** ClusterIP dari Service.
*   **Pencarian Singkat:**
    *   Dari Pod di namespace *yang sama* (`production`), Anda bisa menggunakan nama pendek: `my-nginx`.
    *   Dari Pod di namespace *lain*, Anda perlu menggunakan nama yang lebih panjang: `my-nginx.production`.
*   **`cluster.local`**: Ini adalah domain cluster default, tetapi dapat dikonfigurasi.

**2. Untuk Pods (Biasanya dengan Headless Services):**

*   **Format:** `<pod-hostname>.<subdomain>.<namespace-name>.svc.<cluster-domain>`
    *   Ini memerlukan `Service` tipe **Headless** (`clusterIP: None`) dengan nama yang sama dengan `subdomain`.
    *   Pod harus memiliki field `hostname` dan `subdomain` yang diset di `spec`-nya.
*   **Contoh:** Jika ada Headless Service bernama `db-nodes` di namespace `data`, dan Pod StatefulSet memiliki `hostname: mysql-0` dan `subdomain: db-nodes`, maka nama DNS-nya adalah `mysql-0.db-nodes.data.svc.cluster.local`.
*   **Resolves to:** **Alamat IP Pod** individual.
*   **Penggunaan Utama:** Untuk StatefulSets yang memerlukan penemuan peer langsung berdasarkan nama Pod yang stabil, atau skenario service discovery kustom lainnya.

*   **Format (IP Pod):** `<pod-ip-dashed>.<namespace-name>.pod.<cluster-domain>`
    *   **Contoh:** `10-244-0-5.default.pod.cluster.local` (untuk Pod dengan IP 10.244.0.5 di namespace default).
    *   **Resolves to:** Alamat IP Pod. Jarang digunakan secara langsung oleh aplikasi, lebih untuk debugging.

**3. Record Tambahan:**

*   **SRV Records:** Untuk port bernama pada Service. Format: `_<port-name>._<protocol>.<service-name>.<namespace-name>.svc.<cluster-domain>`. Berguna untuk menemukan port spesifik dari sebuah service.

## Konfigurasi `/etc/resolv.conf` Pod

Kubelet secara otomatis mengkonfigurasi file `/etc/resolv.conf` di dalam setiap kontainer. Contoh isinya:

```
nameserver 10.96.0.10       # ClusterIP dari Service kube-dns
search default.svc.cluster.local svc.cluster.local cluster.local # Domain pencarian
options ndots:5             # Threshold untuk mencoba domain pencarian
```

*   **`nameserver`**: Menunjuk ke IP CoreDNS.
*   **`search`**: Daftar domain yang akan ditambahkan secara otomatis saat Anda menggunakan nama pendek. Inilah mengapa `my-nginx` dari namespace `default` bisa me-resolve ke `my-nginx.default.svc.cluster.local`. Urutan penting.
*   **`options ndots:5`**: Jika nama yang Anda kueri memiliki kurang dari 5 titik, sistem akan mencoba menambahkannya dengan domain dari `search` list sebelum mengkuerinya sebagai nama absolut.

Anda dapat mengkustomisasi perilaku DNS per Pod menggunakan field `dnsPolicy` dan `dnsConfig` di Pod `spec`.

*   **`dnsPolicy`:**
    *   `ClusterFirst` (Default): Kueri DNS yang tidak cocok dengan domain cluster akan diteruskan ke nameserver upstream (yang dikonfigurasi di Node).
    *   `Default`: Pod mewarisi konfigurasi resolv.conf dari Node tempat ia berjalan.
    *   `None`: Mengabaikan konfigurasi DNS Kubernetes. Anda harus menyediakan konfigurasi DNS sendiri melalui `dnsConfig`.
    *   `ClusterFirstWithHostNet`: Untuk Pods yang berjalan dengan `hostNetwork: true`.
*   **`dnsConfig`:** Memungkinkan Anda menentukan `nameservers`, `searches`, dan `options` kustom untuk Pod.

## Troubleshooting DNS

Masalah DNS adalah penyebab umum masalah konektivitas di Kubernetes.

*   **Gunakan `nslookup` atau `dig` dari dalam Pod:** Jalankan Pod sementara (`kubectl run tmp-debug --image=busybox:1.28 --rm -it -- /bin/sh`) dan gunakan `nslookup <service-name>` atau `dig <service-name>.<namespace>.svc.cluster.local`.
*   **Periksa Status Pods CoreDNS:** `kubectl get pods -n kube-system -l k8s-app=kube-dns`. Pastikan mereka `Running` dan `Ready`.
*   **Periksa Log CoreDNS:** `kubectl logs -n kube-system -l k8s-app=kube-dns`. Cari error.
*   **Periksa Konfigurasi CoreDNS:** `kubectl get configmap coredns -n kube-system -o yaml`. Periksa apakah plugin `kubernetes` dikonfigurasi dengan benar.
*   **Periksa `/etc/resolv.conf` di Pod yang Bermasalah:** `kubectl exec <pod-name> -- cat /etc/resolv.conf`. Pastikan nameserver menunjuk ke IP Service `kube-dns` yang benar.
*   **Periksa Konektivitas ke CoreDNS:** Dari Pod yang bermasalah, coba `ping <ClusterIP_kube-dns>` atau `telnet <ClusterIP_kube-dns> 53`.
*   **Periksa Network Policies:** Pastikan tidak ada NetworkPolicy yang memblokir traffic UDP/TCP ke port 53 dari Pod ke Pods CoreDNS.

DNS internal adalah komponen krusial yang memungkinkan service discovery yang dinamis dan andal di dalam cluster Kubernetes.
