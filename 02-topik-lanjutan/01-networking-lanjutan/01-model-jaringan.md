# Model Jaringan Fundamental Kubernetes

Memahami model jaringan dasar Kubernetes adalah kunci untuk memahami bagaimana Pods, Services, dan komponen lainnya berkomunikasi. Kubernetes menetapkan serangkaian asumsi dan persyaratan fundamental tentang bagaimana jaringan harus berperilaku di dalam cluster.

## Prinsip Inti Model Jaringan

Model jaringan Kubernetes didasarkan pada prinsip-prinsip berikut:

1.  **Setiap Pod Mendapatkan Alamat IP Uniknya Sendiri:** Setiap Pod di dalam cluster dialokasikan alamat IP uniknya sendiri dari ruang alamat IP internal cluster (CIDR Pod). Tidak ada dua Pod yang memiliki IP yang sama pada waktu yang bersamaan.
2.  **Komunikasi Pod-ke-Pod Tanpa NAT:** Semua Pod di dalam cluster harus dapat berkomunikasi satu sama lain secara langsung menggunakan alamat IP Pod masing-masing, **tanpa** memerlukan Network Address Translation (NAT). Ini berlaku bahkan jika Pods berada di Node yang berbeda.
3.  **Komunikasi Node-ke-Pod (dan sebaliknya) Tanpa NAT:** Agen di Node (seperti Kubelet itu sendiri atau komponen sistem lainnya) harus dapat berkomunikasi dengan semua Pod di Node tersebut (dan sebaliknya) tanpa NAT.
4.  **IP yang Dilihat Pod Sama dengan IP yang Dilihat Pihak Lain:** Alamat IP yang dilihat oleh sebuah Pod (IP internalnya) harus sama dengan alamat IP yang digunakan oleh Pod atau Node lain untuk berkomunikasi dengannya.

## Implikasi Model Ini

*   **Penyederhanaan Konfigurasi Aplikasi:** Aplikasi yang berjalan di dalam Pod tidak perlu khawatir tentang pemetaan port atau mekanisme NAT yang rumit untuk berkomunikasi dengan Pod lain. Mereka dapat langsung menargetkan IP dan port Pod tujuan seolah-olah berada di jaringan datar yang sama.
*   **Portabilitas:** Model ini memastikan bahwa aplikasi yang berjalan di VM atau bare metal dapat dengan mudah dipindahkan ke Kubernetes tanpa perlu mengubah cara mereka melakukan penemuan layanan atau komunikasi jaringan secara drastis (meskipun penggunaan Services K8s lebih disarankan daripada hardcoding IP).
*   **Ketergantungan pada Implementasi Jaringan:** Kubernetes *tidak* mengimplementasikan model jaringan ini secara langsung. Sebaliknya, ia bergantung pada **Plugin Jaringan** (yang sesuai dengan spesifikasi CNI) untuk benar-benar menyiapkan jaringan agar memenuhi persyaratan ini.

## Bagaimana Ini Dicapai? (Peran CNI)

Untuk mencapai model jaringan ini, terutama komunikasi Pod-ke-Pod antar Node tanpa NAT, berbagai teknik digunakan oleh plugin CNI, antara lain:

1.  **Overlay Networks (Contoh: Flannel VXLAN, Calico IPIP):**
    *   Membuat jaringan virtual "di atas" jaringan fisik Node yang ada.
    *   Setiap Node memiliki subnet (bagian dari CIDR Pod cluster) untuk Pods lokalnya.
    *   Ketika Pod di Node A ingin mengirim paket ke Pod di Node B:
        *   Paket dengan IP Pod sumber dan tujuan asli dibungkus (enkapsulasi) di dalam paket lain dengan IP Node A sebagai sumber dan IP Node B sebagai tujuan.
        *   Paket yang dibungkus ini dikirim melalui jaringan fisik Node.
        *   Node B menerima paket, membukanya (dekapsulasi), dan mengirimkan paket asli ke Pod tujuan di Node B.
    *   **Pros:** Relatif mudah diatur di berbagai jaringan fisik yang ada.
    *   **Cons:** Bisa ada sedikit overhead performa karena enkapsulasi/dekapsulasi.

2.  **Routing Langsung (Contoh: Calico BGP, Flannel host-gw):**
    *   Mengkonfigurasi tabel routing di setiap Node (atau router jaringan fisik jika menggunakan BGP) agar mengetahui cara merutekan traffic langsung ke subnet Pod di Node lain.
    *   Tidak ada enkapsulasi yang diperlukan.
    *   **Pros:** Performa biasanya lebih baik (mendekati native).
    *   **Cons:** Mungkin memerlukan konfigurasi jaringan fisik yang lebih spesifik (misalnya, semua Node harus berada di subnet L2 yang sama untuk `host-gw`, atau memerlukan router yang mendukung BGP).

3.  **Integrasi dengan Jaringan Cloud Provider (Contoh: AWS VPC CNI, Azure CNI, GKE VPC-Native):**
    *   Plugin CNI berinteraksi langsung dengan API jaringan cloud provider.
    *   Pods mendapatkan alamat IP langsung dari subnet VPC cloud provider.
    *   Memanfaatkan kemampuan routing asli dari infrastruktur cloud.
    *   **Pros:** Performa sangat baik, integrasi mulus dengan fitur cloud lain (security groups, dll.).
    *   **Cons:** Terikat pada cloud provider tertentu, mungkin memiliki batasan jumlah IP per Node.

Pemilihan dan konfigurasi plugin CNI yang tepat sangat penting untuk memastikan model jaringan Kubernetes berfungsi dengan benar dan efisien di lingkungan spesifik Anda.

## Ringkasan

Model jaringan Kubernetes menyediakan fondasi jaringan yang datar dan sederhana (dari perspektif Pod), memungkinkan komunikasi langsung antar Pod tanpa NAT. Ini dicapai melalui penggunaan plugin jaringan (CNI) yang mengimplementasikan teknik seperti overlay network atau routing langsung. Memahami prinsip dasar ini membantu dalam merancang aplikasi dan memecahkan masalah jaringan di Kubernetes.
