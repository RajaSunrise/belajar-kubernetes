# CNI (Container Network Interface)

Seperti yang dibahas dalam model jaringan fundamental, Kubernetes sendiri tidak mengimplementasikan jaringan Pod. Sebaliknya, ia mendefinisikan sebuah standar atau spesifikasi bernama **CNI (Container Network Interface)** yang memungkinkan berbagai *plugin jaringan* pihak ketiga untuk menyediakan fungsionalitas jaringan ini.

## Apa itu CNI?

CNI adalah proyek Cloud Native Computing Foundation (CNCF) yang terdiri dari:

1.  **Spesifikasi:** Mendefinisikan format JSON untuk konfigurasi jaringan dan serangkaian operasi (API) yang harus diimplementasikan oleh plugin CNI. Operasi utama adalah:
    *   `ADD`: Menambahkan kontainer (Pod) ke jaringan. Ini melibatkan alokasi IP, penyiapan interface jaringan di dalam namespace Pod, dan menghubungkannya ke jaringan Node/cluster.
    *   `DEL`: Menghapus kontainer (Pod) dari jaringan. Membersihkan interface dan melepaskan alamat IP.
    *   `CHECK`: Memeriksa apakah kontainer masih ada di jaringan yang diharapkan.
    *   `VERSION`: Melaporkan versi spesifikasi CNI yang didukung oleh plugin.
2.  **Libraries:** Pustaka Go resmi untuk membantu pengembang membuat plugin yang sesuai dengan spesifikasi.
3.  **Plugin:** Implementasi konkret dari spesifikasi CNI. Inilah yang benar-benar melakukan pekerjaan penyiapan jaringan. Ada banyak plugin CNI yang tersedia.

## Bagaimana CNI Digunakan oleh Kubernetes?

1.  **Instalasi Plugin CNI:** Administrator cluster memilih dan menginstal plugin CNI (biasanya sebagai DaemonSet yang berjalan di setiap Node). Instalasi ini juga menempatkan *binary* plugin CNI di direktori yang telah ditentukan pada setiap Node (misalnya, `/opt/cni/bin/`).
2.  **Konfigurasi CNI:** Sebuah file konfigurasi CNI (format JSON, biasanya di `/etc/cni/net.d/`) memberitahu Kubelet plugin mana yang harus digunakan dan parameter apa yang harus diberikan padanya (misalnya, CIDR Pod, jenis backend jaringan).
3.  **Siklus Hidup Pod:**
    *   Ketika Kubelet perlu membuat Pod baru, setelah Container Runtime (misalnya, containerd) membuat namespace jaringan untuk Pod, Kubelet akan memanggil *binary* plugin CNI yang dikonfigurasi (dengan operasi `ADD` dan detail Pod).
    *   Plugin CNI kemudian melakukan tugasnya: mengalokasikan IP dari pool yang dikelola (mungkin melalui IPAM - IP Address Management plugin), membuat interface virtual (misalnya, `veth pair`), menempatkan satu ujung di namespace Pod, menghubungkan ujung lainnya ke bridge Linux atau konfigurasi jaringan Node lainnya, mengatur IP address dan route di dalam Pod, dll.
    *   Ketika Pod dihapus, Kubelet memanggil plugin CNI dengan operasi `DEL` untuk membersihkan semua sumber daya jaringan yang terkait dengan Pod tersebut.

## Mengapa CNI Penting?

*   **Fleksibilitas & Pilihan:** Memungkinkan pengguna memilih solusi jaringan yang paling sesuai dengan kebutuhan mereka (performa, fitur keamanan, kemudahan operasi, integrasi cloud).
*   **Inovasi:** Vendor jaringan dapat berinovasi dan mengembangkan solusi jaringan canggih untuk Kubernetes tanpa harus mengubah kode inti Kubernetes.
*   **Standarisasi:** Menyediakan antarmuka standar antara container runtime/orchestrator (seperti Kubelet) dan logika penyiapan jaringan.

## Plugin CNI Populer (Overview Singkat)

Ada banyak plugin CNI, masing-masing dengan fokus dan fitur yang berbeda. Beberapa yang paling populer antara lain:

1.  **Flannel:**
    *   **Fokus:** Kesederhanaan dan kemudahan penggunaan.
    *   **Fitur:** Terutama menyediakan konektivitas jaringan L3 dasar. Pilihan backend umum: VXLAN (overlay, paling kompatibel), host-gw (routing langsung, lebih performan tapi butuh L2 antar node).
    *   **Network Policy:** Tidak mendukung Network Policy Kubernetes secara native (memerlukan kombinasi dengan plugin lain seperti Calico untuk itu, atau menggunakan Canal).
    *   **Cocok untuk:** Cluster sederhana, belajar, lingkungan di mana Network Policy bukan prioritas utama.

2.  **Calico:**
    *   **Fokus:** Jaringan berperforma tinggi dan keamanan jaringan yang kaya fitur (Network Policy).
    *   **Fitur:** Menggunakan routing L3 murni. Backend: BGP (untuk routing optimal di jaringan yang mendukungnya) atau IPIP (overlay). Implementasi Network Policy yang sangat kuat dan fleksibel (melampaui standar K8s).
    *   **Network Policy:** Ya, implementasi yang sangat baik dan ekstensif.
    *   **Cocok untuk:** Cluster produksi skala besar, lingkungan yang membutuhkan performa tinggi dan/atau keamanan jaringan granular. Mungkin sedikit lebih kompleks untuk diatur daripada Flannel.

3.  **Cilium:**
    *   **Fokus:** Jaringan, keamanan, dan observability yang didukung oleh eBPF (extended Berkeley Packet Filter) di kernel Linux.
    *   **Fitur:** Menggunakan eBPF untuk penegakan jaringan dan keamanan yang sangat efisien. Mendukung Network Policy K8s dan fitur kebijakan L7 (HTTP-aware). Identitas berbasis label (bukan hanya IP). Kemampuan load balancing lanjutan (pengganti `kube-proxy`), enkripsi transparan, observability mendalam.
    *   **Network Policy:** Ya, sangat kuat (L3/L4/L7).
    *   **Cocok untuk:** Lingkungan modern yang mencari performa, keamanan tingkat lanjut (termasuk L7), dan observability mendalam. Membutuhkan kernel Linux yang relatif baru dengan dukungan eBPF.

4.  **Weave Net:**
    *   **Fokus:** Kemudahan penggunaan, setup "zero configuration", enkripsi jaringan bawaan.
    *   **Fitur:** Menciptakan mesh network terenkripsi antar node. Menggunakan VXLAN atau "sleeve" mode (UDP encapsulation). Juga menyediakan implementasi Network Policy.
    *   **Network Policy:** Ya.
    *   **Cocok untuk:** Cluster di mana enkripsi traffic antar node penting, kemudahan setup dihargai.

5.  **CNI Cloud Provider (AWS VPC CNI, Azure CNI, GKE VPC-Native):**
    *   **Fokus:** Integrasi erat dengan jaringan cloud provider masing-masing.
    *   **Fitur:** Memberikan IP VPC asli ke Pods, memanfaatkan routing cloud native, integrasi dengan security groups/NSG.
    *   **Network Policy:** Tergantung implementasi (misalnya, AWS VPC CNI bisa dikombinasikan dengan Calico untuk Network Policy).
    *   **Cocok untuk:** Cluster yang berjalan di cloud provider tersebut dan menginginkan integrasi serta performa terbaik di lingkungan itu.

## Pemilihan Plugin CNI

Pemilihan CNI tergantung pada kebutuhan spesifik Anda:
*   Butuh kesederhanaan? Flannel mungkin cukup.
*   Butuh Network Policy yang kuat dan performa? Calico atau Cilium adalah pilihan bagus.
*   Butuh fitur L7, observability mendalam, dan menggunakan kernel modern? Cilium sangat menarik.
*   Butuh enkripsi mudah? Weave Net bisa jadi pilihan.
*   Berjalan di cloud? CNI native provider seringkali merupakan pilihan terbaik.

Penting untuk memahami fitur dan persyaratan dari plugin CNI yang Anda pilih untuk memastikan jaringan cluster Kubernetes Anda berfungsi sesuai harapan.
