# Komponen Control Plane: Otak Cluster Kubernetes

**Control Plane** (sebelumnya dikenal sebagai Master Node) adalah pusat saraf dan otak dari cluster Kubernetes. Ia bertanggung jawab untuk membuat keputusan global tentang cluster, mendeteksi dan merespons peristiwa, serta mengelola state keseluruhan cluster. Tanpa Control Plane yang berfungsi, cluster tidak dapat dikelola atau dioperasikan.

Control Plane terdiri dari beberapa komponen inti yang bekerja sama. Dalam setup produksi, komponen-komponen ini seringkali dijalankan di beberapa mesin (Nodes) untuk memastikan Ketersediaan Tinggi (High Availability - HA).

Berikut adalah komponen utama Control Plane:

## 1. `kube-apiserver` (API Server)

*   **Peran:** Pintu gerbang utama dan satu-satunya ke cluster Kubernetes. Semua interaksi (dari `kubectl`, UI Dashboard, komponen internal seperti Kubelet dan Controller Manager, serta aplikasi eksternal) harus melalui API Server.
*   **Fungsi:**
    *   **Mengekspos Kubernetes API:** Menyediakan antarmuka RESTful HTTP untuk semua operasi pada objek Kubernetes (Pods, Services, Nodes, dll.).
    *   **Validasi:** Memvalidasi data objek yang dikirimkan (misalnya, memastikan field yang diperlukan ada dan formatnya benar).
    *   **Autentikasi & Otorisasi (AuthN/AuthZ):** Memverifikasi identitas peminta (AuthN) dan memeriksa apakah peminta memiliki izin untuk melakukan tindakan yang diminta pada sumber daya target (AuthZ - biasanya via RBAC).
    *   **Admission Control:** Menerapkan kebijakan tambahan sebelum objek dibuat atau diperbarui (misalnya, menerapkan standar keamanan Pod, menyuntikkan sidecar).
    *   **Berinteraksi dengan `etcd`:** Satu-satunya komponen yang membaca dan menulis state cluster ke/dari `etcd`.
*   **Skalabilitas:** API Server dirancang untuk dapat di-scale secara horizontal (menjalankan beberapa instance di belakang load balancer) untuk menangani beban tinggi.
*   **Penting:** Jika API Server tidak dapat dijangkau, Anda tidak dapat mengelola cluster Anda.

## 2. `etcd`

*   **Peran:** Database key-value terdistribusi yang konsisten dan sangat tersedia (Highly Available - HA). Bertindak sebagai **penyimpanan backing (backing store)** atau "sumber kebenaran" (source of truth) untuk semua data cluster Kubernetes.
*   **Fungsi:**
    *   Menyimpan **state yang diinginkan** (`spec`) dan **state aktual** (`status`) dari semua objek API Kubernetes.
    *   Memastikan konsistensi data di seluruh cluster, bahkan jika beberapa node Control Plane gagal (jika dikonfigurasi dalam mode HA dengan quorum).
    *   Menggunakan protokol Raft untuk konsensus terdistribusi.
*   **Interaksi:** Hanya `kube-apiserver` yang diizinkan berkomunikasi langsung dengan `etcd`. Komponen lain mengakses state melalui API Server.
*   **Penting:** Kehilangan data `etcd` berarti kehilangan state seluruh cluster. **Backup `etcd` secara teratur sangat krusial** dalam cluster self-managed. (Di cluster terkelola/managed K8s, penyedia cloud biasanya menangani backup etcd).

## 3. `kube-scheduler` (Scheduler)

*   **Peran:** Mengawasi Pods yang baru dibuat dan belum memiliki Node yang ditetapkan (`.spec.nodeName` kosong). Tugasnya adalah memilih **Node terbaik** bagi Pod tersebut untuk dijalankan.
*   **Fungsi (Proses Scheduling):**
    1.  **Filtering (Penyaringan/Predicates):** Mengidentifikasi sekumpulan Node yang *memenuhi syarat* untuk menjalankan Pod. Ini memeriksa batasan-batasan seperti:
        *   Apakah Node memiliki resource (CPU, Memori) yang cukup sesuai `requests` Pod?
        *   Apakah Node memenuhi `nodeSelector` atau `nodeAffinity` yang diminta Pod?
        *   Apakah Pod dapat mentolerir `Taints` yang ada pada Node?
        *   Apakah volume yang dibutuhkan Pod tersedia di Node tersebut?
        *   Apakah port host yang diminta Pod tersedia di Node?
    2.  **Scoring (Penilaian/Priorities):** Jika ada lebih dari satu Node yang memenuhi syarat, Scheduler memberikan skor pada setiap Node kandidat berdasarkan serangkaian fungsi prioritas. Tujuannya adalah memilih Node yang "paling pas". Fungsi prioritas dapat mempertimbangkan:
        *   Node yang memiliki resource paling banyak tersedia (least requested priority).
        *   Node yang sudah memiliki image kontainer yang dibutuhkan Pod (menghemat waktu tarik image).
        *   Memenuhi aturan `podAffinity` dan `podAntiAffinity`.
        *   Memenuhi `topologySpreadConstraints`.
    3.  **Binding:** Scheduler memilih Node dengan skor tertinggi dan kemudian memberi tahu API Server untuk **mengikat (bind)** Pod ke Node tersebut dengan memperbarui field `.spec.nodeName` pada objek Pod.
*   **Penting:** Scheduler hanya membuat *keputusan* penempatan awal. Ia tidak bertanggung jawab untuk benar-benar *menjalankan* Pod di Node (itu tugas Kubelet).

## 4. `kube-controller-manager` (Controller Manager)

*   **Peran:** Menjalankan proses **controller** inti Kubernetes. Controller adalah loop kontrol yang mengawasi state cluster melalui API Server dan melakukan perubahan untuk mencoba memindahkan state saat ini menuju state yang diinginkan.
*   **Fungsi:** `kube-controller-manager` adalah satu binary yang menjalankan banyak controller logis untuk efisiensi. Beberapa controller penting yang dijalankannya:
    *   **Node Controller:** Bertanggung jawab untuk memperhatikan Node dan merespons ketika Node menjadi tidak tersedia (NotReady) atau dihapus.
    *   **Replication Controller / ReplicaSet Controller:** Memastikan jumlah Pod yang benar (sesuai `spec.replicas`) selalu berjalan untuk setiap ReplicaSet.
    *   **Deployment Controller:** Mengelola peluncuran (rollout), update, dan rollback Deployments (dengan mengelola ReplicaSets).
    *   **StatefulSet Controller:** Mengelola Pods dalam StatefulSet (identitas stabil, urutan).
    *   **DaemonSet Controller:** Memastikan Pods berjalan di Node yang sesuai untuk DaemonSets.
    *   **Job Controller:** Mengawasi Pods Job dan menandai Job sebagai selesai/gagal.
    *   **CronJob Controller:** Membuat Job berdasarkan jadwal CronJob.
    *   **Endpoint/EndpointSlice Controller:** Mengisi objek Endpoints/EndpointSlices berdasarkan Pods yang cocok dengan selector Service dan dalam keadaan `Ready`.
    *   **Service Account & Token Controllers:** Membuat Service Account default dan token API untuk Namespace baru.
    *   **Namespace Controller:** Mengelola siklus hidup Namespace.
    *   **PersistentVolume Controller:** Mengelola siklus hidup PV dan PVC, termasuk binding.
*   **Cara Kerja:** Setiap controller mengkhususkan diri pada satu atau beberapa jenis objek, mengamati perubahannya via API Server, dan melakukan tindakan rekonsiliasi yang diperlukan.

## 5. `cloud-controller-manager` (Opsional)

*   **Peran:** Menjalankan controller yang berinteraksi secara spesifik dengan API **penyedia cloud** (AWS, GCP, Azure, dll.) tempat cluster berjalan.
*   **Fungsi:** Memisahkan logika interaksi cloud dari `kube-controller-manager` inti. Ini memungkinkan penyedia cloud merilis fitur atau perbaikan bug tanpa harus terikat pada siklus rilis Kubernetes inti. Controller yang dijalankannya meliputi:
    *   **Node Controller (Cloud):** Memeriksa penyedia cloud untuk melihat apakah Node (VM) telah dihapus di cloud jika Node berhenti merespons. Mengupdate objek Node K8s dengan informasi spesifik cloud (zona, tipe instance).
    *   **Route Controller:** Menyiapkan rute jaringan di infrastruktur cloud (misalnya, di VPC) agar kontainer di Node yang berbeda dapat berkomunikasi.
    *   **Service Controller:** Membuat, memperbarui, dan menghapus load balancer penyedia cloud ketika Service dengan `type: LoadBalancer` dibuat/diubah/dihapus di Kubernetes.
*   **Penting:** Komponen ini hanya berjalan jika cluster Anda dikonfigurasi untuk berintegrasi dengan penyedia cloud tertentu. Di lingkungan on-premise atau lokal, komponen ini tidak ada.

Komponen-komponen Control Plane ini bekerja sama secara harmonis, berkomunikasi melalui API Server dan menggunakan `etcd` sebagai state store, untuk menjaga agar cluster Kubernetes berjalan sesuai dengan state yang diinginkan pengguna. Ketersediaan dan kesehatan Control Plane sangat vital untuk operasi cluster.
