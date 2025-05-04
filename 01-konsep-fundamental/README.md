# Bagian 1: Konsep Fundamental Kubernetes

Selamat datang di inti Kubernetes! Bagian ini bertujuan untuk membangun pemahaman yang kuat tentang konsep-konsep dasar dan blok bangunan fundamental yang membentuk platform orkestrasi ini. Menguasai dasar-dasar ini sangat penting sebelum melangkah ke topik yang lebih canggih.

Di bagian ini, kita akan menjelajahi:

1.  **[Filosofi Desain](./01-filosofi-desain.md):** Memahami *mengapa* Kubernetes bekerja seperti itu – model deklaratif, arsitektur berbasis API, dan loop kontrol rekonsiliasi.
2.  **[Arsitektur Cluster](./02-arsitektur-cluster/):** Membedah komponen utama yang membentuk cluster Kubernetes:
    *   **[Control Plane](./02-arsitektur-cluster/control-plane.md):** Otak cluster (API Server, etcd, Scheduler, Controller Manager).
    *   **[Worker Node](./02-arsitektur-cluster/worker-node.md):** Otot cluster tempat aplikasi berjalan (Kubelet, Kube-proxy, Container Runtime).
3.  **[Objek Kubernetes](./03-objek-kubernetes.md):** Struktur dasar (apiVersion, kind, metadata, spec, status) dari semua sumber daya yang Anda kelola.
4.  **[Pods](./04-pods/):** Unit terkecil yang dapat di-deploy.
    *   **[Pengenalan](./04-pods/pengenalan-pods.md):** Apa itu Pod dan mengapa kita menggunakannya.
    *   **[Siklus Hidup](./04-pods/siklus-hidup-pod.md):** Fase (Pending, Running, Succeeded, Failed) dan Kondisi.
    *   **[Multi-Container](./04-pods/multi-container-pods.md):** Pola Sidecar, Adapter, Ambassador.
    *   **[Init Containers](./04-pods/init-containers.md):** Menjalankan tugas persiapan sebelum aplikasi utama.
    *   **[Probes](./04-pods/pod-probes.md):** Pemeriksaan kesehatan (Liveness, Readiness, Startup).
    *   **[Resource Requests & Limits](./04-pods/resource-requests-limits.md):** Mengelola CPU dan Memori.
    *   **[Contoh YAML](./04-pods/contoh-pod-yaml.md):** Melihat definisi Pod yang lengkap.
5.  **[Namespaces](./05-namespaces.md):** Mempartisi cluster secara logis untuk organisasi dan kontrol akses.
6.  **[Labels & Selectors](./06-labels-selectors.md):** Perekat ajaib untuk mengelompokkan dan menghubungkan objek.
7.  **[Annotations](./07-annotations.md):** Melampirkan metadata non-identifikasi untuk alat dan deskripsi.
8.  **[Services](./08-services/):** Menyediakan akses jaringan yang stabil dan load balancing ke Pods.
    *   **[Pengenalan](./08-services/pengenalan-services.md):** Masalah yang dipecahkan dan cara kerja dasar.
    *   **[Tipe Services](./08-services/tipe-services.md):** ClusterIP, NodePort, LoadBalancer, ExternalName.
    *   **[Endpoints & EndpointSlices](./08-services/endpoints-endpointslices.md):** Bagaimana Service melacak backend Pod.
    *   **[Headless Services](./08-services/headless-services.md):** Service tanpa ClusterIP untuk penemuan langsung.
    *   **[Contoh YAML](./08-services/contoh-service-yaml.md):** Ilustrasi definisi berbagai tipe Service.
9.  **[Controllers & Workloads](./09-controllers-workloads/):** Objek tingkat tinggi untuk mengelola siklus hidup aplikasi.
    *   **[Deployments](./09-controllers-workloads/01-deployments.md):** Mengelola aplikasi stateless (scaling, updates, rollbacks).
    *   **[ReplicaSets](./09-controllers-workloads/02-replicasets.md):** Memastikan jumlah replika Pod (biasanya dikelola oleh Deployment).
    *   **[StatefulSets](./09-controllers-workloads/03-statefulsets.md):** Mengelola aplikasi stateful (identitas & storage stabil, urutan).
    *   **[DaemonSets](./09-controllers-workloads/04-daemonsets.md):** Menjalankan satu Pod per Node.
    *   **[Jobs](./09-controllers-workloads/05-jobs.md):** Menjalankan tugas batch hingga selesai.
    *   **[CronJobs](./09-controllers-workloads/06-cronjobs.md):** Menjalankan Jobs secara terjadwal.
10. **[Konfigurasi Aplikasi](./10-konfigurasi-aplikasi/):** Memisahkan konfigurasi dan data sensitif dari image.
    *   **[ConfigMaps](./10-konfigurasi-aplikasi/01-configmaps.md):** Untuk konfigurasi non-sensitif.
    *   **[Secrets](./10-konfigurasi-aplikasi/02-secrets.md):** Untuk data sensitif (password, token, kunci).
11. **[Storage](./11-storage/):** Menyediakan penyimpanan untuk Pods.
    *   **[Volumes](./11-storage/01-volumes.md):** Konsep dasar (emptyDir, hostPath) & cara mount ke Pod.
    *   **[PersistentVolumes (PV)](./11-storage/02-persistentvolumes-pv.md):** Abstraksi sumber daya penyimpanan cluster.
    *   **[PersistentVolumeClaims (PVC)](./11-storage/03-persistentvolumeclaims-pvc.md):** Permintaan penyimpanan oleh pengguna/Pod.
    *   **[StorageClasses](./11-storage/04-storageclasses.md):** Mengaktifkan provisioning volume dinamis.
    *   **[Volume Modes](./11-storage/05-volume-modes.md):** Filesystem vs. Block.

Setiap file markdown di direktori ini akan membahas topik-topik tersebut secara lebih mendalam. Setelah menyelesaikan bagian ini, Anda akan memiliki fondasi yang kokoh untuk memahami cara kerja Kubernetes dan mulai membangun serta men-deploy aplikasi Anda sendiri.
