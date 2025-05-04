# Komponen Worker Node: Otot Cluster Kubernetes

**Worker Nodes** (sebelumnya dikenal sebagai Minions atau Nodes saja) adalah mesin (virtual atau fisik) di dalam cluster Kubernetes tempat **beban kerja aplikasi Anda benar-benar berjalan** dalam bentuk Pods. Setiap cluster biasanya memiliki beberapa Worker Nodes untuk distribusi beban dan ketersediaan.

Worker Nodes dikelola oleh Control Plane dan menjalankan beberapa komponen penting untuk berintegrasi dengan cluster dan menjalankan kontainer:

## 1. `kubelet`

*   **Peran:** Agen utama yang berjalan di **setiap Node** (termasuk node Control Plane dalam beberapa konfigurasi, meskipun mungkin tidak menjalankan beban kerja pengguna). Ini adalah "mata" dan "tangan" Control Plane di setiap mesin.
*   **Fungsi:**
    *   **Mendaftar Node:** Saat pertama kali dimulai, Kubelet mendaftarkan dirinya ke API Server, membuat objek Node yang merepresentasikan mesin tersebut di cluster.
    *   **Menerima PodSpecs:** Mengawasi API Server untuk Pods yang telah dijadwalkan (oleh Scheduler) untuk berjalan di Node-nya.
    *   **Mengelola Siklus Hidup Kontainer:** Berinteraksi dengan **Container Runtime** (melalui CRI - Container Runtime Interface) untuk:
        *   Menarik (pull) image kontainer yang diperlukan.
        *   Membuat dan memulai kontainer sesuai spesifikasi Pod.
        *   Menghentikan kontainer.
        *   Me-restart kontainer yang gagal (sesuai `restartPolicy` Pod).
    *   **Volume Mounting:** Memasang (mount) volume yang didefinisikan dalam Pod ke dalam kontainer.
    *   **Melakukan Probes:** Menjalankan Liveness, Readiness, dan Startup Probes yang dikonfigurasi pada kontainer untuk memeriksa kesehatannya.
    *   **Melaporkan Status:** Secara berkala melaporkan status Node (kondisi seperti `Ready`, `MemoryPressure`, `DiskPressure`) dan status Pods yang berjalan di Node tersebut kembali ke API Server.
    *   **Manajemen Resource:** Memastikan kontainer tidak menggunakan resource melebihi `limits` yang ditentukan.
*   **Penting:** Jika Kubelet di sebuah Node gagal atau berhenti, Node tersebut akan dilaporkan sebagai `NotReady` oleh Control Plane, dan Control Plane tidak akan bisa lagi mengelola Pods di Node tersebut (misalnya, memulai Pod baru atau mendapatkan status Pod yang ada). Controller Manager kemudian mungkin akan mulai menghentikan (evict) Pods dari Node `NotReady` tersebut dan menjadwalkannya di Node lain (jika dikelola oleh Deployment/StatefulSet/dll.).

## 2. `kube-proxy`

*   **Peran:** Network proxy yang berjalan di **setiap Node**. Komponen ini sangat penting untuk mengimplementasikan abstraksi **Service** Kubernetes.
*   **Fungsi:**
    *   **Mengawasi API Server:** Memantau penambahan, penghapusan, atau modifikasi objek `Service` dan `Endpoints`/`EndpointSlices`.
    *   **Memelihara Aturan Jaringan:** Berdasarkan informasi dari API Server, `kube-proxy` memprogram aturan jaringan di Node (menggunakan salah satu mode: `iptables`, `IPVS`, atau `userspace` (lama), `kernelspace` (Windows)). Aturan ini memastikan bahwa lalu lintas yang ditujukan ke alamat IP virtual (ClusterIP) dan port sebuah Service dapat:
        *   Dicegat (intercepted).
        *   Dilakukan load balancing (memilih salah satu IP Pod backend yang sehat).
        *   Diteruskan (misalnya melalui DNAT) ke Pod backend yang dipilih.
    *   **Memungkinkan Komunikasi Service:** Memastikan bahwa Pod di Node mana pun dapat mencapai Service melalui ClusterIP-nya, dan lalu lintas akan dirutekan dengan benar ke Pod backend yang sesuai, di Node mana pun Pod backend itu berada.
*   **Mode Operasi:**
    *   `iptables`: Default di banyak instalasi. Menggunakan aturan `iptables` kernel Linux. Bisa menjadi lambat jika ada ribuan Service karena sifat sekuensial `iptables`. Andal dan matang.
    *   `IPVS` (IP Virtual Server): Menggunakan tabel hash IPVS di kernel Linux. Dirancang untuk load balancing dan umumnya lebih performan daripada `iptables` pada skala besar (jumlah Service banyak). Membutuhkan modul kernel IPVS.
*   **Penting:** Tanpa `kube-proxy` yang berjalan dan berfungsi dengan benar di setiap Node, objek Service tidak akan berfungsi, dan Pods tidak akan dapat saling menemukan atau diakses secara andal melalui endpoint Service yang stabil.

## 3. Container Runtime

*   **Peran:** Perangkat lunak yang bertanggung jawab untuk **menjalankan kontainer**. Kubernetes bersifat fleksibel dan tidak terikat pada satu runtime spesifik.
*   **Fungsi:** Menangani tugas-tugas level rendah terkait kontainer:
    *   Menarik (pull) image kontainer dari registry.
    *   Membongkar (unpack) image.
    *   Membuat dan memulai kontainer (menggunakan fitur kernel Linux seperti namespaces dan cgroups).
    *   Menghentikan kontainer.
    *   Melaporkan status kontainer.
*   **CRI (Container Runtime Interface):** Kubelet tidak berkomunikasi langsung dengan berbagai container runtime. Sebaliknya, ia berkomunikasi melalui plugin shim yang mengimplementasikan **CRI API**. Ini memungkinkan Kubernetes mendukung berbagai runtime yang sesuai dengan standar CRI.
*   **Runtime Populer:**
    *   **Docker:** Runtime asli yang sangat populer (meskipun K8s sekarang sering menggunakan shim `cri-dockerd` untuk berbicara dengannya via CRI).
    *   **containerd:** Runtime level inti yang diekstrak dari Docker, sekarang menjadi proyek CNCF tersendiri. Sangat populer dan sering menjadi default di banyak distribusi K8s (termasuk Kind, K3s, GKE, AKS).
    *   **CRI-O:** Runtime lain yang dibuat khusus untuk Kubernetes (dikembangkan oleh Red Hat). Fokus pada kesesuaian dengan CRI dan OCI (Open Container Initiative).
*   **Penting:** Container runtime harus terinstal dan berjalan dengan benar di setiap Worker Node agar Kubelet dapat menjalankan kontainer untuk Pods.

Ketiga komponen ini (`kubelet`, `kube-proxy`, dan Container Runtime) adalah fondasi yang memungkinkan Worker Node berpartisipasi dalam cluster Kubernetes, menerima instruksi dari Control Plane, dan menjalankan serta mengelola beban kerja aplikasi Anda dalam kontainer.
