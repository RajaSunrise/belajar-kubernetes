# Belajar Kubernetes: Panduan Ultra Komprehensif dari Nol hingga Hero

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Selamat Datang di Perjalanan Mendalam Kubernetes Anda!**

Repositori `belajar-kubernetes` ini dirancang sebagai ensiklopedia dan peta jalan Anda untuk menaklukkan kompleksitas Kubernetes. Dari pemula yang baru mengenal kontainer hingga praktisi berpengalaman yang ingin memperdalam pemahaman, panduan ini bertujuan untuk menjadi sumber daya definitif Anda. Kami akan mengupas tuntas setiap lapisan Kubernetes, mulai dari filosofi desainnya hingga seluk-beluk operasional tingkat lanjut.

Kubernetes (K8s), sang nakhoda (κυβερνήτης - Yunani untuk "pilot" atau "nakhoda") dunia kontainer, adalah platform orkestrasi open-source revolusioner yang telah mentransformasi cara kita membangun, men-deploy, dan mengelola aplikasi modern. Lahir di Google dari pengalaman bertahun-tahun menjalankan beban kerja produksi dalam skala masif (sebagai penerus sistem internal Borg), Kubernetes kini berada di bawah naungan Cloud Native Computing Foundation (CNCF), didukung oleh ekosistem global yang dinamis. Ia mengotomatiskan tugas-tugas operasional yang membosankan namun krusial, memungkinkan developer fokus pada kode dan bisnis fokus pada inovasi.

**Mengapa Investasi Waktu untuk Belajar Kubernetes Begitu Penting?**

Di era cloud-native saat ini, Kubernetes bukan lagi sekadar "nice-to-have", tetapi seringkali menjadi fondasi strategis untuk infrastruktur aplikasi modern. Menguasainya membuka pintu ke berbagai keuntungan:

*   **Abstraksi Infrastruktur & Portabilitas Sejati:** Definisikan aplikasi Anda sekali, jalankan di mana saja—public cloud (AWS, GCP, Azure, dll.), private cloud (OpenStack, VMware), hybrid cloud, bahkan bare metal—dengan konsistensi operasional. Kubernetes menyembunyikan kompleksitas infrastruktur di bawahnya.
*   **Skalabilitas Otomatis & Elastis:** Tanggapi lonjakan traffic atau kebutuhan pemrosesan data secara dinamis. Kubernetes dapat secara otomatis menambah atau mengurangi jumlah instance aplikasi (Pods) berdasarkan metrik seperti penggunaan CPU/Memori (Horizontal Pod Autoscaler - HPA) atau metrik kustom lainnya.
*   **Ketahanan & Penyembuhan Diri (Self-Healing):** Kubernetes secara proaktif memantau kesehatan aplikasi Anda. Jika sebuah kontainer crash, ia akan me-restartnya. Jika sebuah Node (mesin virtual/fisik) gagal, ia akan menjadwal ulang Pods dari Node tersebut ke Node yang sehat, meminimalkan downtime.
*   **Deployment Canggih & Zero Downtime:** Lakukan pembaruan aplikasi (versi baru, perbaikan bug) dengan strategi canggih seperti Rolling Updates (memperbarui instance secara bertahap tanpa downtime), Canary Deployments (merilis ke sebagian kecil pengguna terlebih dahulu), atau Blue/Green Deployments (menjalankan dua versi berdampingan dan memindahkan traffic). Kubernetes menyediakan mekanisme untuk melakukan ini dengan aman dan terkontrol.
*   **Optimalisasi Pemanfaatan Sumber Daya:** Kubernetes bertindak sebagai "Tetris" raksasa untuk kontainer Anda, secara cerdas menempatkan (scheduling) Pods ke Node yang memiliki kapasitas tersedia (bin packing), memaksimalkan penggunaan CPU, memori, dan sumber daya lainnya, yang dapat menghemat biaya infrastruktur secara signifikan.
*   **Ekosistem Cloud-Native yang Kaya:** Kubernetes adalah pusat dari alam semesta Cloud Native Computing Foundation (CNCF). Belajar Kubernetes membuka akses ke ratusan proyek dan alat pelengkap yang terintegrasi—mulai dari service mesh (Istio, Linkerd), monitoring (Prometheus, Grafana), logging (Fluentd, Loki), CI/CD tools (Argo CD, Flux), hingga serverless frameworks (Knative).
*   **Standar Industri & Karir:** Keahlian Kubernetes sangat diminati di seluruh industri teknologi. Menguasainya secara signifikan meningkatkan nilai pasar Anda sebagai developer, DevOps engineer, SRE (Site Reliability Engineer), atau arsitek sistem.

Panduan ini akan membawa Anda melampaui sekadar menjalankan perintah `kubectl`. Kita akan menyelami *mengapa* Kubernetes dirancang seperti itu, *bagaimana* komponen-komponennya berinteraksi, dan *kapan* harus menggunakan fitur-fitur tertentu. Bersiaplah untuk eksplorasi mendalam!

---

## 🎯 Misi & Filosofi Repositori Ini

Repositori ini tidak hanya bertujuan menjadi kumpulan tutorial, tetapi sebuah **kerangka kerja pengetahuan komprehensif** dengan misi:

1.  **Membangun Intuisi Fundamental:** Tidak hanya menghafal perintah, tetapi memahami *prinsip* di balik objek dan mekanisme Kubernetes (deklaratif vs imperatif, level vs edge triggered, loop kontrol).
2.  **Menyajikan Kedalaman Teknis:** Mengupas setiap konsep inti dan lanjutan dengan detail yang memadai, menjelaskan field-field penting dalam YAML, aliran kerja internal, dan implikasi pilihan desain.
3.  **Menawarkan Jalur Belajar Progresif:** Mengorganisir materi secara logis, mulai dari instalasi dasar, konsep fundamental, hingga topik lanjutan seperti keamanan, jaringan, dan observability, memungkinkan pembelajaran bertahap.
4.  **Menyediakan Contoh Praktis & Realistis:** Melengkapi teori dengan contoh kode YAML yang berfungsi, perintah `kubectl`, dan skenario yang mencerminkan tantangan dunia nyata.
5.  **Menjadi Referensi Andal:** Berfungsi sebagai kamus atau ensiklopedia cepat saat Anda membutuhkan penjelasan tentang objek, fitur, atau pola Kubernetes tertentu.
6.  **Mendorong Eksplorasi & Eksperimen:** Memberikan dasar yang kuat dan ide untuk latihan mandiri, memungkinkan Anda membangun cluster percobaan dan mencoba berbagai konfigurasi.
7.  **Menekankan Praktik Terbaik:** Mengintegrasikan rekomendasi dan pola yang terbukti untuk membangun dan mengelola aplikasi Kubernetes yang tangguh, aman, dan efisien.

**Siapa yang Akan Mendapatkan Manfaat Maksimal?**

*   **Pengembang Perangkat Lunak (Software Developers):** Pahami cara mengemas aplikasi Anda dalam kontainer, mendefinisikan deployment, service, dan konfigurasi, serta memanfaatkan fitur K8s untuk CI/CD dan pengembangan yang lebih cepat.
*   **Insinyur DevOps/SRE/System Administrators:** Kuasai cara merancang, membangun, mengelola, mengamankan, memantau, dan memecahkan masalah cluster Kubernetes dan aplikasi yang berjalan di atasnya.
*   **Arsitek Solusi (Solution Architects):** Pelajari bagaimana mengintegrasikan Kubernetes ke dalam arsitektur sistem yang lebih besar, memahami trade-off, dan merancang solusi cloud-native yang scalable dan resilient.
*   **Mahasiswa & Pembelajar Mandiri:** Dapatkan pemahaman mendalam tentang teknologi orkestrasi kontainer terdepan yang membentuk masa depan infrastruktur IT.
*   **Manajer Teknis & Pengambil Keputusan:** Pahami kapabilitas, manfaat, dan tantangan adopsi Kubernetes untuk membuat keputusan strategis yang tepat.

---

##  Prerequisites: Fondasi Sebelum Memulai

Kubernetes dibangun di atas tumpukan teknologi lain. Memiliki pemahaman dasar tentang konsep-konsep berikut akan sangat mempercepat perjalanan belajar Anda dan memungkinkan Anda menghargai *mengapa* Kubernetes melakukan hal-hal dengan cara tertentu:

**Konsep Teknologi Inti:**

1.  **Kontainerisasi & Docker (Sangat Penting):**
    *   **Apa itu Kontainer?** Pahami konsep isolasi proses menggunakan Linux namespaces (pid, net, mnt, uts, ipc, user) dan pembatasan sumber daya menggunakan control groups (cgroups).
    *   **Kontainer vs. VM:** Jelaskan perbedaan fundamental dalam arsitektur, overhead, kecepatan startup, dan densitas.
    *   **Docker:** Anda *harus* nyaman dengan Docker. Ini meliputi:
        *   **Images:** Konsep lapisan (layers), build context, Dockerfile (perintah dasar: `FROM`, `WORKDIR`, `COPY`, `ADD`, `RUN`, `CMD`, `ENTRYPOINT`, `EXPOSE`, `ENV`, `ARG`, `VOLUME`), Best practices Dockerfile (multi-stage builds, meminimalkan layer).
        *   **Containers:** Lifecycle (create, start, stop, rm), menjalankan perintah (`docker run`, `docker exec`), port mapping (`-p`), volume mounting (`-v`).
        *   **Registry:** Docker Hub, registry privat (AWS ECR, GCP GCR, Azure ACR, Harbor). Perintah `docker pull`, `docker push`, `docker login`.
        *   **Networking Dasar Docker:** Konsep bridge network default, user-defined networks.
        *   **Docker Compose (Berguna):** Memahami cara mendefinisikan dan menjalankan aplikasi multi-kontainer secara lokal (sebagai batu loncatan sebelum K8s).

2.  **Dasar-dasar Sistem Operasi Linux:**
    *   **Command Line Interface (CLI):** Navigasi direktori (`cd`, `ls`, `pwd`), manipulasi file/direktori (`cp`, `mv`, `rm`, `mkdir`, `touch`), editor teks CLI (`nano`, `vim`), perizinan file (`chmod`, `chown`), pipes (`|`), redirection (`>`, `>>`, `<`).
    *   **Manajemen Proses:** Melihat proses (`ps`, `top`, `htop`), mengirim sinyal (`kill`), memahami user/group ID.
    *   **Konsep Jaringan Linux:** Interface jaringan (`ip addr`, `ifconfig`), tabel routing (`ip route`), DNS client (`/etc/resolv.conf`), tools diagnosa (`ping`, `traceroute`, `netstat`, `ss`, `curl`, `wget`, `telnet`).
    *   **Filesystem:** Struktur direktori standar (FHS), mounting/unmounting.

3.  **Konsep Dasar Jaringan Komputer:**
    *   **Model OSI / TCP/IP:** Pahami lapisan-lapisan dasar (fisik, data link, network, transport, application).
    *   **IP Addressing (IPv4):** Alamat IP, Subnet Mask, CIDR notation, Network vs Broadcast address, Private vs Public IP ranges.
    *   **Ports & Sockets:** Peran port dalam membedakan layanan pada satu IP. Konsep socket (IP:Port).
    *   **Protokol Transport:** TCP (koneksi stateful, handal, three-way handshake) vs UDP (koneksi stateless, cepat, tidak handal).
    *   **Protokol Aplikasi:** HTTP/HTTPS (request methods - GET/POST/PUT/DELETE, status codes - 2xx/3xx/4xx/5xx, headers), DNS (resolusi nama domain ke IP, record types - A, CNAME, MX, TXT, SRV).
    *   **Load Balancing:** Konsep dasar penyebaran traffic ke beberapa server backend (round-robin, least connections, dll.).
    *   **Firewalls:** Konsep dasar pemfilteran traffic berdasarkan IP, port, protokol.

4.  **YAML (YAML Ain't Markup Language):**
    *   **Sintaks Dasar:** Kubernetes menggunakan YAML secara ekstensif untuk file manifest (definisi objek). Anda *harus* memahami:
        *   Key-Value pairs (`key: value`).
        *   Indentation (spasi, bukan tab!) untuk menunjukkan struktur/hierarki. Sangat penting!
        *   Lists/Arrays (dimulai dengan tanda hubung `-`).
        *   Dictionaries/Maps (kumpulan key-value).
        *   Tipe data dasar (string, number, boolean).
        *   Komentar (`#`).
        *   Multi-line strings (`|` untuk mempertahankan newline, `>` untuk melipat newline).
    *   **Tips:** Gunakan linter YAML atau validasi di IDE Anda untuk menghindari kesalahan sintaks yang umum.

**Alat & Lingkungan yang Diperlukan:**

1.  **`kubectl` (Kubernetes Command-Line Tool):**
    *   Antarmuka utama Anda untuk berinteraksi dengan API Server Kubernetes. Wajib diinstal di mesin lokal Anda.
    *   [Instalasi kubectl (Dokumentasi Resmi)](https://kubernetes.io/docs/tasks/tools/install-kubectl/)
2.  **Akses ke Cluster Kubernetes:** Anda tidak bisa belajar Kubernetes tanpa cluster untuk berlatih! Pilihan:
    *   **Lingkungan Lokal (Sangat Direkomendasikan untuk Memulai):**
        *   **Minikube:** Pilihan klasik, matang, menjalankan K8s node tunggal di VM (VirtualBox, Hyper-V, KVM) atau kontainer (Docker driver). Mendukung banyak fitur add-on. [Situs Minikube](https://minikube.sigs.k8s.io/)
        *   **Kind (Kubernetes IN Docker):** Pilihan modern, cepat, ringan. Menjalankan node K8s (bisa multi-node) sebagai kontainer Docker. Cocok untuk pengujian CI/CD dan eksperimen cepat. Membutuhkan Docker terinstal. [Situs Kind](https://kind.sigs.k8s.io/)
        *   **K3s:** Distribusi K8s yang ringan dan bersertifikasi CNCF dari Rancher/SUSE. Binary tunggal, mudah diinstal, konsumsi resource rendah. Cocok untuk edge, IoT, CI, dan development. Bisa dijalankan tanpa Docker (menggunakan containerd). [Situs K3s](https://k3s.io/)
        *   **Docker Desktop:** Jika Anda sudah menggunakan Docker Desktop (Windows/Mac), ia memiliki opsi bawaan untuk mengaktifkan cluster K8s node tunggal. Sangat nyaman untuk memulai. [Docker Desktop](https://www.docker.com/products/docker-desktop/)
        *   **MicroK8s:** Distribusi K8s dari Canonical (Ubuntu). Mudah diinstal (via snap), banyak add-on. [Situs MicroK8s](https://microk8s.io/)
    *   **Managed Kubernetes di Cloud (Untuk Pengalaman Lebih Realistis, Mungkin Berbayar):**
        *   **Google Kubernetes Engine (GKE):** Layanan K8s terkelola dari Google Cloud.
        *   **Amazon Elastic Kubernetes Service (EKS):** Layanan K8s terkelola dari AWS.
        *   **Azure Kubernetes Service (AKS):** Layanan K8s terkelola dari Microsoft Azure.
        *   **DigitalOcean Kubernetes (DOKS), Linode Kubernetes Engine (LKE),** dll.
        *   **Keuntungan:** Mengelola Control Plane untuk Anda, integrasi cloud, fitur tambahan.
        *   **Kekurangan:** Bisa menimbulkan biaya, abstraksi mungkin menyembunyikan beberapa detail internal.
    *   **Cluster DIY (Tingkat Lanjut):** Membangun cluster dari awal menggunakan alat seperti `kubeadm`, RKE, atau KubeSpray. Memberikan pemahaman terdalam tetapi paling kompleks.
3.  **Text Editor / IDE:**
    *   Sebuah editor yang baik untuk menulis file YAML sangat membantu.
    *   **Visual Studio Code (VS Code):** Pilihan populer dengan ekstensi luar biasa:
        *   `Kubernetes` (Microsoft): IntelliSense, linting, template, navigasi objek cluster.
        *   `YAML` (Red Hat): Validasi dan auto-completion YAML.
        *   Ekstensi Docker, dll.
4.  **Git & Akun Platform Git (GitHub/GitLab/Bitbucket):**
    *   Meskipun tidak wajib untuk *belajar* konsep K8s, mengelola file manifest YAML Anda menggunakan Git adalah praktik standar industri (GitOps). Sangat direkomendasikan untuk membiasakan diri.
5.  **Akun Docker Hub (atau Registry Kontainer Lain):**
    *   Anda memerlukan tempat untuk menyimpan image kontainer kustom Anda jika Anda membangun aplikasi sendiri untuk di-deploy. Docker Hub menawarkan plan gratis.

Memiliki fondasi ini akan membuat konsep Kubernetes terasa lebih intuitif dan logis.

---

## 🏗️ Struktur Repositori: Peta Penjelajahan Anda

Repositori ini dirancang dengan struktur modular untuk memandu pembelajaran Anda secara progresif. Setiap direktori utama mewakili fase atau area topik yang berbeda:

```
belajar-kubernetes/
│
├── README.md                # File ini: Pintu gerbang utama Anda, baca ini dulu!
│
├── 00-persiapan-lingkungan/ # LANGKAH NOL: Menyiapkan medan perang Anda
│   ├── 01-instalasi-kubectl.md          # Instalasi CLI K8s
│   ├── 02-memilih-lingkungan-lokal.md   # Perbandingan Minikube, Kind, K3s, Docker Desktop
│   ├── 03-instalasi-minikube.md         # Panduan detail Minikube
│   ├── 04-instalasi-kind.md             # Panduan detail Kind
│   ├── 05-instalasi-k3s.md              # Panduan detail K3s
│   ├── 06-menggunakan-docker-desktop.md # Panduan Docker Desktop K8s
│   ├── 07-verifikasi-setup.md           # Memastikan cluster Anda siap (`kubectl cluster-info`, `get nodes`)
│   └── 08-konfigurasi-kubectl.md        # Memahami Kubeconfig, konteks, namespace
│
├── 01-konsep-fundamental/   # INTI KUBERNETES: Membangun pemahaman dasar
│   ├── 01-filosofi-desain.md            # Model deklaratif, API, loop kontrol
│   ├── 02-arsitektur-cluster/           # Komponen Control Plane & Node secara mendalam
│   │   ├── control-plane.md             # API Server, etcd, Scheduler, Controller Mgr, Cloud Controller Mgr
│   │   └── worker-node.md               # Kubelet, Kube-proxy, Container Runtime (CRI)
│   ├── 03-objek-kubernetes.md           # Struktur umum (apiVersion, kind, metadata, spec, status)
│   ├── 04-pods/                         # Unit atomik deployment: Penjelasan ultra-detail
│   │   ├── pengenalan-pods.md
│   │   ├── siklus-hidup-pod.md          # Phases (Pending, Running, Succeeded, Failed, Unknown), Conditions
│   │   ├── multi-container-pods.md      # Sidecars, Adapters, Ambassadors
│   │   ├── init-containers.md           # Kontainer inisialisasi
│   │   ├── pod-probes.md                # Liveness, Readiness, Startup Probes (HTTP, TCP, Exec)
│   │   ├── resource-requests-limits.md  # Pentingnya QoS (Guaranteed, Burstable, BestEffort)
│   │   └── contoh-pod-yaml.md
│   ├── 05-namespaces.md                 # Isolasi logis & manajemen multi-tenant
│   ├── 06-labels-selectors.md           # Perekat antar objek: Pengorganisasian & Filtering
│   ├── 07-annotations.md                # Metadata tambahan untuk alat & manusia
│   ├── 08-services/                     # Penemuan layanan & Load Balancing internal
│   │   ├── pengenalan-services.md
│   │   ├── tipe-services.md             # ClusterIP, NodePort, LoadBalancer, ExternalName
│   │   ├── endpoints-endpointslices.md  # Bagaimana Service menemukan Pods
│   │   ├── headless-services.md         # Service tanpa ClusterIP (untuk StatefulSets, service discovery manual)
│   │   └── contoh-service-yaml.md
│   ├── 09-controllers-workloads/        # Mengelola siklus hidup aplikasi
│   │   ├── 01-deployments.md            # Aplikasi stateless: Rolling updates, rollbacks
│   │   ├── 02-replicasets.md            # Fondasi di balik Deployment
│   │   ├── 03-statefulsets.md           # Aplikasi stateful: Identitas & storage stabil
│   │   ├── 04-daemonsets.md             # Menjalankan Pod di setiap Node (agen, dll.)
│   │   ├── 05-jobs.md                   # Tugas batch sekali jalan
│   │   └── 06-cronjobs.md               # Tugas terjadwal berulang
│   ├── 10-konfigurasi-aplikasi/         # Memisahkan konfigurasi & data sensitif
│   │   ├── 01-configmaps.md             # Menyimpan konfigurasi non-sensitif
│   │   └── 02-secrets.md                # Menyimpan data sensitif (encoding vs enkripsi)
│   ├── 11-storage/                      # Persistensi data
│   │   ├── 01-volumes.md                # Konsep dasar & tipe (emptyDir, hostPath - hati-hati!)
│   │   ├── 02-persistentvolumes-pv.md   # Abstraksi storage cluster
│   │   ├── 03-persistentvolumeclaims-pvc.md # Permintaan storage oleh pengguna/aplikasi
│   │   ├── 04-storageclasses.md         # Provisioning storage dinamis
│   │   └── 05-volume-modes.md           # Filesystem vs Block
│   └── README.md                        # Ringkasan Konsep Fundamental
│
├── 02-topik-lanjutan/       # MENYELAM LEBIH DALAM: Fitur & area kompleks
│   ├── 01-networking-lanjutan/        # Jaringan dalam K8s
│   │   ├── 01-model-jaringan.md         # IP-per-Pod, komunikasi Pod-ke-Pod
│   │   ├── 02-container-network-interface-cni.md # Plugin jaringan (Flannel, Calico, Cilium - overview)
│   │   ├── 03-ingress-controllers.md    # Mengekspos service HTTP/S ke luar (Nginx, Traefik)
│   │   ├── 04-network-policies.md       # Firewall level Pod/Namespace
│   │   ├── 05-dns-internal.md           # CoreDNS & resolusi nama service/pod
│   │   └── 06-service-mesh-intro.md     # Pengenalan Istio & Linkerd (konsep)
│   ├── 02-storage-lanjutan/           # Manajemen storage tingkat lanjut
│   │   ├── 01-container-storage-interface-csi.md # Standar modern plugin storage
│   │   ├── 02-volume-snapshots.md       # Backup & restore data volume
│   │   ├── 03-volume-expansion.md       # Mengubah ukuran PVC secara online
│   │   └── 04-storage-topology.md       # Penjadwalan sadar lokasi storage (`WaitForFirstConsumer`)
│   ├── 03-security/                   # Mengamankan cluster & aplikasi
│   │   ├── 01-authentication.md         # Siapa Anda? (Users, ServiceAccounts, Sertifikat, Token)
│   │   ├── 02-authorization-rbac.md     # Apa yang boleh Anda lakukan? (Roles, ClusterRoles, Bindings)
│   │   ├── 03-service-accounts-detail.md# Identitas untuk proses dalam Pod
│   │   ├── 04-security-contexts.md      # Mengontrol privilege Pod & Kontainer (user/group, capabilities)
│   │   ├── 05-pod-security-admission.md # Standar keamanan Pod (pengganti PSP)
│   │   ├── 06-secrets-management.md     # Praktik terbaik & enkripsi etcd
│   │   └── 07-network-security.md       # Recap Network Policies & mTLS (Service Mesh)
│   ├── 04-scheduling-lanjutan/        # Mengontrol penempatan Pod
│   │   ├── 01-node-selectors-affinity.md# Menarik Pod ke Node tertentu
│   │   ├── 02-taints-tolerations.md     # Mendorong Pod menjauh dari Node tertentu
│   │   ├── 03-pod-affinity-anti-affinity.md # Menempatkan Pod relatif terhadap Pod lain
│   │   ├── 04-topology-spread-constraints.md # Menyebarkan Pod secara merata
│   │   └── 05-priority-preemption.md    # Prioritas Pod & penggusuran
│   ├── 05-observability/              # Monitoring, Logging, Tracing
│   │   ├── 01-metrics-server.md         # Metrik dasar (CPU/Memori) untuk HPA & `kubectl top`
│   │   ├── 02-monitoring-prometheus.md  # Arsitektur Prometheus, Exporters, PromQL intro
│   │   ├── 03-visualisasi-grafana.md    # Membuat dashboard dengan Grafana
│   │   ├── 04-logging-architecture.md   # Pola logging (sidecar, node agent), EFK vs PLG
│   │   └── 05-tracing-intro.md          # Konsep distributed tracing (Jaeger, Zipkin)
│   ├── 06-manajemen-sumber-daya/      # Mengelola utilisasi cluster
│   │   ├── 01-resource-quotas.md        # Membatasi penggunaan resource per Namespace
│   │   └── 02-limit-ranges.md           # Menetapkan batas default/min/max per Pod/Container
│   ├── 07-package-management-helm/    # Mengelola aplikasi K8s dengan Helm
│   │   ├── 01-pengenalan-helm.md        # Konsep Charts, Releases, Repositories
│   │   ├── 02-struktur-helm-chart.md    # `Chart.yaml`, `values.yaml`, `templates/`
│   │   ├── 03-templating-helm.md        # Sintaks Go template, functions, variables
│   │   ├── 04-dependensi-subcharts.md   # Mengelola dependensi Chart
│   │   └── 05-helm-lifecycle-hooks.md   # Menjalankan aksi selama siklus hidup Release
│   ├── 08-mengembangkan-kubernetes/     # Memperluas fungsionalitas K8s
│   │   ├── 01-custom-resource-definitions-crd.md # Menambah tipe objek baru ke API
│   │   └── 02-operators-pattern.md      # Mengotomatisasi manajemen aplikasi stateful/kompleks
│   └── README.md                        # Ringkasan Topik Lanjutan
│
├── 03-praktek-langsung/     # HANDS-ON LABS: Mengotori tangan Anda
│   ├── 01-deploy-stateless-app/       # Deployment, Service, Scaling, Rolling Update
│   │   ├── README.md
│   │   ├── app/                         # Kode aplikasi contoh (mis: Python Flask/Node.js Express)
│   │   ├── Dockerfile
│   │   ├── deployment.yaml
│   │   └── service.yaml
│   ├── 02-deploy-stateful-app/        # StatefulSet, Headless Service, PV, PVC (mis: database sederhana)
│   │   ├── README.md
│   │   ├── statefulset.yaml
│   │   ├── headless-service.yaml
│   │   └── pvc.yaml
│   ├── 03-konfigurasi-secret/         # Menggunakan ConfigMap & Secret (env vars, volume mounts)
│   ├── 04-expose-app-ingress/         # Menggunakan Ingress untuk akses eksternal
│   ├── 05-setup-monitoring-sederhana/ # Deploy Prometheus & Grafana (mis: via Helm/kube-prometheus-stack)
│   └── README.md                        # Daftar Tutorial
│
├── 04-ekosistem-tools/      # PERALATAN PERANG: Alat bantu populer
│   ├── 01-kubectl-power-user.md       # Tips & trik kubectl (plugins, output formatting, alias)
│   ├── 02-gui-dashboards.md           # Lens, k9s, Kubernetes Dashboard
│   ├── 03-dev-workflow-tools.md       # Skaffold, Tilt, Telepresence
│   ├── 04-ci-cd-gitops.md             # Argo CD, Flux CD
│   ├── 05-policy-management.md        # OPA Gatekeeper, Kyverno
│   └── README.md                        # Ringkasan Alat Bantu
│
├── 05-pola-praktik-terbaik/ # KEARIFAN LOKAL: Cara kerja yang benar
│   ├── 01-desain-aplikasi.md          # 12-Factor App di K8s, Health Checks
│   ├── 02-manajemen-konfigurasi.md    # ConfigMap vs Secret, GitOps
│   ├── 03-keamanan.md                 # RBAC, Network Policies, Security Contexts
│   ├── 04-manajemen-resource.md       # Requests/Limits, Quotas
│   ├── 05-observability.md            # Logging, Metrics, Alerts
│   ├── 06-storage.md                  # Memilih tipe Volume, Reclaim Policy
│   ├── 07-penamaan-labeling.md        # Konvensi yang konsisten
│   └── README.md                        # Ringkasan Praktik Terbaik
│
├── 06-troubleshooting-cookbook/ # SAAT SEMUA GAGAL: Panduan detektif
│   ├── 01-metodologi-umum.md          # Pendekatan sistematis
│   ├── 02-masalah-pod.md              # Pending, CrashLoopBackOff, ImagePull, OOMKilled
│   ├── 03-masalah-jaringan.md         # Konektivitas Service, DNS, Ingress, Network Policy
│   ├── 04-masalah-storage.md          # PVC tidak Bound, masalah mounting
│   ├── 05-masalah-control-plane.md    # Diagnosa komponen master (jika self-hosted)
│   ├── 06-masalah-performa.md         # Aplikasi lambat, resource bottleneck
│   └── README.md                        # Daftar Resep Troubleshooting
│
├── 07-studi-kasus-arsitektur/ # DUNIA NYATA: Contoh penerapan
│   ├── 01-web-app-multi-tier.md
│   ├── 02-pipeline-data-processing.md
│   ├── 03-hosting-database.md
│   └── README.md
│
├── GLOSSARY.md              # Kamus istilah Kubernetes
├── FURTHER_READING.md       # Tautan ke sumber belajar eksternal
└── LICENSE                  # Lisensi (Mis: MIT)
```

*(Catatan: Struktur di atas adalah representasi yang sangat diperluas. Membuat dan mengisi *semua* file markdown ini dengan konten yang sangat detail akan menjadi upaya kolosal, jauh melampaui batasan satu respons. Namun, ini memberikan gambaran tentang kedalaman yang dituju.)*

---

## 🚀 Fase Nol: Persiapan Lingkungan & Verifikasi Awal

Sebelum kita menyelami lautan Kubernetes, kita perlu menyiapkan kapal (lingkungan lokal) dan memastikan semua peralatan navigasi (kubectl) berfungsi. Fase ini krusial untuk pengalaman belajar yang lancar.

**1. Instalasi `kubectl` Sang Pengendali**

`kubectl` adalah tongkat komando Anda. Ini adalah bagaimana Anda akan berbicara dengan cluster Kubernetes Anda. Instalasi bervariasi berdasarkan sistem operasi Anda.

*   **Lihat Panduan Detail:** [./00-persiapan-lingkungan/01-instalasi-kubectl.md](./00-persiapan-lingkungan/01-instalasi-kubectl.md)
*   **Verifikasi Instalasi:** Setelah terinstal, buka terminal dan jalankan:
    ```bash
    kubectl version --client --output=yaml # Menampilkan versi client dalam format YAML
    ```
    Anda akan melihat output yang menunjukkan versi client `kubectl` Anda. Pada titik ini, server mungkin belum terhubung.

**2. Memilih Medan Perang Lokal Anda**

Untuk belajar dan bereksperimen, Anda memerlukan cluster Kubernetes yang berjalan di mesin Anda. Ada beberapa pilihan populer, masing-masing dengan pro dan kontra:

*   **Minikube:** Stabil, fitur lengkap, mendukung banyak driver (VirtualBox, Docker, dll.). Pilihan bagus jika Anda menginginkan pengalaman VM tradisional atau membutuhkan add-on spesifik.
*   **Kind (Kubernetes IN Docker):** Cepat, ringan, bagus untuk multi-node lokal dan CI/CD. Memanfaatkan Docker secara ekstensif.
*   **K3s:** Sangat ringan, binary tunggal, cocok untuk resource terbatas. Menggunakan containerd secara default.
*   **Docker Desktop:** Integrasi termudah jika Anda sudah menggunakan Docker Desktop. Cluster node tunggal yang siap pakai.
*   **MicroK8s:** Alternatif ringan lainnya, terutama populer di ekosistem Ubuntu/snap.

*   **Lihat Perbandingan & Rekomendasi:** [./00-persiapan-lingkungan/02-memilih-lingkungan-lokal.md](./00-persiapan-lingkungan/02-memilih-lingkungan-lokal.md)

**3. Instalasi dan Memulai Cluster Lokal Pilihan Anda**

Pilih salah satu lingkungan dari langkah 2 dan ikuti panduan instalasi detailnya:

*   **Panduan Minikube:** [./00-persiapan-lingkungan/03-instalasi-minikube.md](./00-persiapan-lingkungan/03-instalasi-minikube.md)
    ```bash
    # Contoh memulai Minikube dengan driver Docker
    minikube start --driver=docker --cpus=2 --memory=4096mb
    ```
*   **Panduan Kind:** [./00-persiapan-lingkungan/04-instalasi-kind.md](./00-persiapan-lingkungan/04-instalasi-kind.md)
    ```bash
    # Contoh membuat cluster Kind bernama 'belajar-k8s'
    kind create cluster --name belajar-k8s
    ```
*   **Panduan K3s:** [./00-persiapan-lingkungan/05-instalasi-k3s.md](./00-persiapan-lingkungan/05-instalasi-k3s.md)
    ```bash
    # Contoh instalasi K3s via skrip
    curl -sfL https://get.k3s.io | sh -
    # Konfigurasi KUBECONFIG mungkin diperlukan setelahnya
    ```
*   **Panduan Docker Desktop:** [./00-persiapan-lingkungan/06-menggunakan-docker-desktop.md](./00-persiapan-lingkungan/06-menggunakan-docker-desktop.md) (Biasanya hanya mengaktifkan di Settings).

**4. Verifikasi Konektivitas Cluster**

Setelah cluster lokal Anda berjalan, saatnya memastikan `kubectl` dapat berkomunikasi dengannya.

*   **Lihat Panduan Verifikasi:** [./00-persiapan-lingkungan/07-verifikasi-setup.md](./00-persiapan-lingkungan/07-verifikasi-setup.md)
*   **Perintah Kunci:**
    ```bash
    # Periksa konektivitas dan versi client & server
    kubectl version
    # Output harus menunjukkan Client Version dan Server Version

    # Dapatkan informasi dasar tentang cluster dan endpoint API Server
    kubectl cluster-info
    # Output akan menunjukkan URL Master dan DNS Cluster

    # Lihat node(s) dalam cluster Anda (akan ada 1 node untuk setup lokal dasar)
    kubectl get nodes -o wide
    # Output:
    # NAME           STATUS   ROLES           AGE   VERSION   INTERNAL-IP    EXTERNAL-IP   OS-IMAGE             KERNEL-VERSION     CONTAINER-RUNTIME
    # minikube       Ready    control-plane   10m   v1.27.4   192.168.49.2   <none>        Ubuntu 22.04.2 LTS   5.15.49-linuxkit   docker://24.0.2
    # (Detail output akan bervariasi tergantung lingkungan Anda)

    # Lihat Pods yang berjalan di namespace sistem (komponen internal K8s)
    kubectl get pods -n kube-system
    ```
    Jika perintah ini berhasil tanpa error, lingkungan Anda siap!

**5. Memahami Konfigurasi `kubectl` (Kubeconfig)**

Bagaimana `kubectl` tahu cluster mana yang harus diajak bicara? Jawabannya ada di file `kubeconfig`.

*   **Lihat Penjelasan Kubeconfig:** [./00-persiapan-lingkungan/08-konfigurasi-kubectl.md](./00-persiapan-lingkungan/08-konfigurasi-kubectl.md)
*   **Konsep Utama:**
    *   **Clusters:** Mendefinisikan cluster target (URL API Server, data CA).
    *   **Users:** Mendefinisikan kredensial klien (sertifikat, token).
    *   **Contexts:** Menggabungkan Cluster, User, dan Namespace default.
    *   **`current-context`:** Konteks yang aktif digunakan oleh `kubectl`.
*   **Lokasi Default:** `~/.kube/config`
*   **Perintah Berguna:**
    ```bash
    kubectl config view # Tampilkan konfigurasi Kubeconfig saat ini
    kubectl config get-contexts # Lihat semua konteks yang tersedia
    kubectl config current-context # Lihat konteks yang sedang aktif
    kubectl config use-context <nama-konteks> # Ganti konteks aktif
    kubectl config set-context --current --namespace=<nama-namespace> # Ubah namespace default untuk konteks saat ini
    ```

Dengan selesainya fase nol ini, Anda memiliki lingkungan kerja yang solid untuk mulai menjelajahi konsep-konsep inti Kubernetes.

---

## 🌌 Bagian Satu: Konsep Fundamental Kubernetes - Membedah Sang Nakhoda

Di bagian ini, kita akan membongkar mesin Kubernetes, memahami komponen-komponen pembangunnya, filosofi di baliknya, dan objek-objek dasar yang akan Anda gunakan setiap hari. Menguasai fondasi ini sangat penting sebelum melangkah ke topik yang lebih kompleks.

*(Setiap sub-bagian di bawah ini merujuk pada file markdown yang (dalam implementasi penuh) akan berisi penjelasan yang sangat mendalam, contoh YAML, diagram, dan detail teknis.)*

### 1.1 Filosofi Desain Inti Kubernetes
Sebelum masuk ke `kind: Pod`, mari pahami *mengapa* Kubernetes bekerja seperti itu.
*   **Model Deklaratif:** Anda menyatakan *apa* state akhir yang diinginkan, bukan *bagaimana* mencapainya. Kubernetes yang mencari cara.
*   **API-Centric:** Semua interaksi terjadi melalui API Server RESTful. Objek adalah sumber kebenaran.
*   **Loop Kontrol (Rekonsiliasi):** Controller terus menerus membandingkan state *diinginkan* (dari `spec`) dengan state *aktual* (diamati di cluster) dan mengambil tindakan untuk menyelaraskannya.
*   **Immutability (Prinsip):** Kontainer (dan seringkali Pods) idealnya diperlakukan sebagai immutable. Perubahan dilakukan dengan mengganti, bukan memodifikasi di tempat.
*   **Arsitektur Terdistribusi & Terdesentralisasi:** Dirancang untuk ketahanan terhadap kegagalan.
*   **Lihat Detail:** [./01-konsep-fundamental/01-filosofi-desain.md](./01-konsep-fundamental/01-filosofi-desain.md)

### 1.2 Arsitektur Cluster: Control Plane & Worker Nodes
Sebuah cluster K8s terdiri dari otak (Control Plane) dan otot (Worker Nodes).
*   **Control Plane (Otak):**
    *   `kube-apiserver`: Pintu gerbang API, validasi, penyimpanan state (via etcd).
    *   `etcd`: Database key-value terdistribusi, menyimpan state cluster. Krusial!
    *   `kube-scheduler`: Memilih Node terbaik untuk menjalankan Pod baru.
    *   `kube-controller-manager`: Menjalankan berbagai controller (Node, ReplicaSet, Deployment, dll.).
    *   `cloud-controller-manager` (Opsional): Berinteraksi dengan API cloud provider.
*   **Worker Nodes (Otot):**
    *   `kubelet`: Agen di setiap node, mengelola siklus hidup kontainer di Pod, berkomunikasi dengan API Server.
    *   `kube-proxy`: Mengelola aturan jaringan (iptables/IPVS) untuk Services.
    *   `Container Runtime`: Perangkat lunak yang menjalankan kontainer (Docker, containerd, CRI-O) via CRI (Container Runtime Interface).
*   **Lihat Detail Mendalam & Diagram:** [./01-konsep-fundamental/02-arsitektur-cluster/](./01-konsep-fundamental/02-arsitektur-cluster/)

### 1.3 Objek Kubernetes: Batu Bata Pembangun
Entitas persisten yang merepresentasikan state cluster. Memahami struktur dasarnya adalah kunci.
*   `apiVersion`: Versi API (e.g., `v1`, `apps/v1`, `batch/v1`). Menunjukkan kematangan dan grup API.
*   `kind`: Tipe objek (e.g., `Pod`, `Service`, `Deployment`).
*   `metadata`: Data identifikasi (wajib: `name`; opsional tapi penting: `namespace`, `labels`, `annotations`, `uid`).
*   `spec`: Spesifikasi *state yang diinginkan*. Strukturnya sangat bervariasi berdasarkan `kind`. Ini yang Anda *definisikan*.
*   `status`: Status *state aktual* objek. Diisi dan diperbarui oleh Kubernetes. Anda tidak mengedit ini.
*   **Lihat Detail:** [./01-konsep-fundamental/03-objek-kubernetes.md](./01-konsep-fundamental/03-objek-kubernetes.md)

### 1.4 Pods: Unit Atomik Deployment (Penjelasan Ultra-Detail)
Unit terkecil yang dapat di-deploy dan dijadwalkan. Inti dari semua beban kerja.
*   **Konsep:** Satu atau lebih kontainer yang berbagi network namespace, IPC namespace, dan (opsional) storage volumes. Selalu berjalan bersama di Node yang sama.
*   **Siklus Hidup:** `Pending` -> `ContainerCreating` -> `Running` <-> (Restarting) -> `Succeeded` / `Failed`. Pod bersifat fana (ephemeral).
*   **Multi-Container:** Pola Sidecar (logging, monitoring, proxy), Adapter, Ambassador. Kapan menggunakannya?
*   **Init Containers:** Kontainer yang berjalan *sebelum* kontainer utama, untuk setup (mis: menunggu service lain, pre-populate data).
*   **Probes (Penting!):**
    *   `livenessProbe`: Apakah kontainer masih hidup? Jika gagal, Kubelet me-restart kontainer.
    *   `readinessProbe`: Apakah kontainer siap menerima traffic? Jika gagal, Endpoint Controller menghapus IP Pod dari Service Endpoints.
    *   `startupProbe`: Untuk aplikasi yang lambat start-up, menonaktifkan liveness/readiness sementara.
    *   Tipe Probe: `httpGet`, `tcpSocket`, `exec`.
*   **Resource Requests & Limits:** Mengelola CPU & Memori.
    *   `requests`: Jumlah resource yang *dijamin* untuk kontainer. Digunakan oleh Scheduler.
    *   `limits`: Batas *maksimum* resource yang boleh digunakan. Jika terlampaui (Memori: OOMKilled; CPU: Throttled).
    *   **QoS Classes:** `Guaranteed` (requests==limits), `Burstable` (requests<limits), `BestEffort` (tanpa requests/limits).
*   **Lihat Detail Ekstrem:** [./01-konsep-fundamental/04-pods/](./01-konsep-fundamental/04-pods/)

### 1.5 Namespaces: Ruang Kerja Virtual
Membagi cluster secara logis untuk tim, lingkungan, atau aplikasi.
*   **Tujuan:** Scope nama objek, kontrol akses (RBAC), kuota resource.
*   **Default Namespaces:** `default`, `kube-system`, `kube-public`, `kube-node-lease`.
*   **Penting:** *Tidak* memberikan isolasi jaringan atau node secara default.
*   **Lihat Detail:** [./01-konsep-fundamental/05-namespaces.md](./01-konsep-fundamental/05-namespaces.md)

### 1.6 Labels & Selectors: Perekat Ajaib
Mekanisme kunci untuk mengelompokkan dan memilih objek.
*   **Labels:** Key-value pairs (string) di `metadata`. Untuk identifikasi.
*   **Selectors:** Ekspresi untuk memilih objek berdasarkan labelnya. Digunakan oleh Services, Deployments, ReplicaSets, dll.
    *   Equality-based: `environment=production`, `tier!=frontend`.
    *   Set-based: `environment in (production, qa)`, `!database`.
*   **Pentingnya Konvensi:** Desain strategi labeling yang baik.
*   **Lihat Detail:** [./01-konsep-fundamental/06-labels-selectors.md](./01-konsep-fundamental/06-labels-selectors.md)

### 1.7 Annotations: Catatan Tempel Metadata
Key-value pairs lain di `metadata`, tapi untuk data *non-identifikasi*.
*   **Tujuan:** Informasi untuk tools, debugging, deskripsi, change tracking (`kubernetes.io/change-cause`).
*   **Perbedaan dari Labels:** Tidak digunakan oleh selectors, bisa lebih besar/kompleks.
*   **Lihat Detail:** [./01-konsep-fundamental/07-annotations.md](./01-konsep-fundamental/07-annotations.md)

### 1.8 Services: Penemuan & Akses Stabil ke Pods
Menyediakan IP dan DNS stabil untuk sekumpulan Pods yang berubah-ubah.
*   **Masalah:** Pods fana, IP berubah. Bagaimana klien menemukannya?
*   **Solusi:** Service menggunakan `selector` untuk menemukan Pods target (via Endpoints/EndpointSlices).
*   **Tipe-tipe Service:**
    *   `ClusterIP`: IP internal, hanya dapat diakses dari dalam cluster (default).
    *   `NodePort`: Mengekspos service di port statis pada *setiap* Node.
    *   `LoadBalancer`: Membuat load balancer eksternal di cloud provider (membutuhkan dukungan cloud).
    *   `ExternalName`: Memetakan ke nama DNS eksternal (CNAME).
*   **Endpoints/EndpointSlices:** Objek yang secara otomatis dibuat/diperbarui untuk menyimpan daftar IP:Port Pod yang *siap* (`Ready`) di belakang Service. `kube-proxy` menggunakan ini.
*   **Headless Services (`clusterIP: None`):** Tidak membuat ClusterIP, tapi tetap membuat record DNS SRV/A untuk *setiap* Pod di belakangnya. Penting untuk StatefulSets dan service discovery kustom.
*   **Lihat Detail Mendalam:** [./01-konsep-fundamental/08-services/](./01-konsep-fundamental/08-services/)

### 1.9 Controllers & Workloads: Mengelola Siklus Hidup Aplikasi
Objek tingkat tinggi yang mengelola Pods dan memastikan state yang diinginkan tercapai.
*   **Deployments (Stateless Apps):**
    *   Mengelola ReplicaSets -> Pods.
    *   Fitur utama: Scaling, Rolling Updates (strategi `maxSurge`, `maxUnavailable`), Rollbacks (riwayat revisi), Self-healing.
    *   Cara kerja update: Membuat ReplicaSet baru, scale up baru, scale down lama.
*   **ReplicaSets:** Memastikan N replika Pod selalu berjalan. Jarang digunakan langsung, dikelola oleh Deployment.
*   **StatefulSets (Stateful Apps):**
    *   Untuk aplikasi yang butuh identitas stabil (network, storage). Contoh: Database, Kafka.
    *   Fitur: Nama Pod/DNS stabil (`<sts-name>-<ordinal>`), Storage persisten per Pod (via `volumeClaimTemplates`), Deployment/Scaling/Update terurut (0..N).
    *   Membutuhkan Headless Service.
*   **DaemonSets:** Menjalankan satu Pod per Node (atau subset Node). Untuk agen monitoring, logging, storage, CNI.
*   **Jobs:** Menjalankan tugas hingga selesai (batch processing). `completions`, `parallelism`, `backoffLimit`, `restartPolicy: Never/OnFailure`.
*   **CronJobs:** Menjadwalkan pembuatan Job secara berkala (format cron). `schedule`, `jobTemplate`, `concurrencyPolicy`, `historyLimits`.
*   **Lihat Detail Masing-masing Controller:** [./01-konsep-fundamental/09-controllers-workloads/](./01-konsep-fundamental/09-controllers-workloads/)

### 1.10 Konfigurasi Aplikasi: ConfigMaps & Secrets
Memisahkan konfigurasi dan data sensitif dari image kontainer.
*   **ConfigMaps:** Untuk data non-sensitif (URL, flag fitur, konten file config). Data disimpan plain text.
*   **Secrets:** Untuk data sensitif (password, token API, sertifikat TLS). Data disimpan base64 encoded di etcd (bukan enkripsi!), bisa dienkripsi saat istirahat (at-rest) jika etcd dikonfigurasi. Akses harus dibatasi ketat via RBAC.
*   **Cara Menggunakan:**
    *   Sebagai Environment Variables (kurang aman untuk secrets).
    *   Sebagai File dalam Volume (cara paling umum dan fleksibel). Perubahan pada ConfigMap/Secret *bisa* dipropagasi ke volume (dengan delay), tapi aplikasi mungkin perlu restart/reload.
*   **Lihat Detail & Praktik Terbaik:** [./01-konsep-fundamental/10-konfigurasi-aplikasi/](./01-konsep-fundamental/10-konfigurasi-aplikasi/)

### 1.11 Storage: Membuat Data Bertahan
Menyediakan penyimpanan untuk Pods, dari yang sementara hingga persisten.
*   **Volumes:** Direktori yang dapat diakses kontainer dalam Pod. Siklus hidup bisa terikat Pod (`emptyDir`, `configMap`, `secret`) atau independen (`persistentVolumeClaim`).
    *   `emptyDir`: Temporary scratch space, hilang saat Pod dihapus.
    *   `hostPath`: Mount direktori dari Node host (Gunakan dengan SANGAT HATI-HATI! Risiko keamanan & portabilitas).
*   **PersistentVolumes (PV):** Sumber daya storage *cluster* (disk cloud, NFS, Ceph). Disediakan oleh admin (statis) atau dinamis. Tidak ber-namespace.
*   **PersistentVolumeClaims (PVC):** *Permintaan* storage oleh pengguna/Pod dalam Namespace tertentu. Meminta ukuran, mode akses, storage class.
*   **Binding:** Proses K8s mencocokkan PVC dengan PV yang tersedia dan cocok.
*   **StorageClasses:** Mendefinisikan *jenis* storage (`provisioner`, `parameters`). Mengaktifkan **Dynamic Provisioning** (PV dibuat otomatis saat PVC meminta kelas tersebut).
*   **Access Modes:** `ReadWriteOnce` (RWO), `ReadOnlyMany` (ROX), `ReadWriteMany` (RWX), `ReadWriteOncePod` (RWOP). Menentukan bagaimana PV bisa di-mount ke Node(s)/Pod(s).
*   **Reclaim Policy:** `Retain`, `Delete`, `Recycle` (deprecated). Apa yang terjadi pada PV saat PVC dihapus.
*   **Volume Modes:** `Filesystem` (default), `Block` (akses raw block device).
*   **Lihat Detail Mendalam:** [./01-konsep-fundamental/11-storage/](./01-konsep-fundamental/11-storage/)

---

## 🌊 Bagian Dua: Menyelami Topik Lanjutan - Menguasai Lautan Dalam

Setelah memahami dasar-dasar, saatnya menjelajahi fitur-fitur yang lebih canggih dan area spesialisasi dalam Kubernetes. Bagian ini akan membahas networking, storage, security, scheduling, observability, dan perluasan Kubernetes.

*(Setiap sub-bagian di bawah ini akan memerlukan penjelasan yang sangat detail, contoh konfigurasi kompleks, dan pembahasan trade-off dalam implementasi penuh.)*

### 2.1 Networking Lanjutan: Menghubungkan Semuanya
Jaringan adalah tulang punggung komunikasi di Kubernetes.
*   **Model Jaringan Fundamental:** IP-per-Pod, semua Pod bisa mencapai Pod lain tanpa NAT (dalam cluster).
*   **CNI (Container Network Interface):** Spesifikasi standar untuk plugin jaringan. Memungkinkan vendor berbeda (Calico, Flannel, Cilium, Weave Net) menyediakan implementasi jaringan Pod. Perbedaan fitur (Network Policy support, enkripsi, performa).
*   **Ingress Controllers:** Cara standar untuk mengekspos service HTTP/HTTPS ke luar cluster. Bertindak sebagai reverse proxy L7.
    *   Resource `Ingress`: Mendefinisikan aturan routing (host, path) ke Services backend.
    *   Ingress Controller (e.g., Nginx Ingress, Traefik): Implementasi yang membaca resource Ingress dan mengkonfigurasi proxy. Perlu di-deploy terpisah.
    *   TLS Termination, Path/Host based routing.
*   **Network Policies:** Firewall level Pod/Namespace. Mengontrol traffic *ingress* (masuk) dan *egress* (keluar) berdasarkan label Pod, namespace, atau CIDR IP. Penting untuk keamanan (segmentasi jaringan). Sintaks selector yang kuat.
*   **DNS Internal (CoreDNS):** Resolusi nama untuk Services (`<service-name>.<namespace>.svc.cluster.local`) dan Pods (jika `hostname` & `subdomain` diatur dengan Headless Service).
*   **Service Mesh (Pengantar):** Lapisan infrastruktur dedicated untuk menangani komunikasi service-to-service (Istio, Linkerd).
    *   Konsep: Sidecar proxy (Envoy) di setiap Pod, Control Plane terpisah.
    *   Fitur: Observability (metrics, tracing, topology), Security (mTLS otomatis, otorisasi L7), Traffic Management (canary, fault injection, circuit breaking, retries).
*   **Lihat Detail:** [./02-topik-lanjutan/01-networking-lanjutan/](./02-topik-lanjutan/01-networking-lanjutan/)

### 2.2 Storage Lanjutan: Data di Mana Saja, Kapan Saja
Manajemen data persisten yang lebih canggih.
*   **CSI (Container Storage Interface):** Standar industri untuk mengekspos sistem storage (block, file) ke K8s. Memisahkan logika storage dari Kubelet. Terdiri dari Controller Plugin (provision/delete, attach/detach) dan Node Plugin (mount/unmount). Memungkinkan vendor storage membuat driver tanpa mengubah kode K8s inti.
*   **Volume Snapshots:** Membuat salinan point-in-time dari PV (jika didukung driver CSI). API: `VolumeSnapshotClass`, `VolumeSnapshot`, `VolumeSnapshotContent`. Use case: Backup, cloning environment.
*   **Volume Expansion:** Mengizinkan penambahan ukuran PVC setelah dibuat (jika `allowVolumeExpansion: true` di StorageClass dan didukung driver CSI).
*   **Storage Topology Awareness:** Menggunakan `volumeBindingMode: WaitForFirstConsumer` di StorageClass. Provisioning dan binding PV ditunda sampai Pod pertama yang menggunakan PVC dijadwalkan. Memastikan PV dibuat di zona/region yang sama dengan Node tempat Pod akan berjalan (penting untuk storage lokal atau zona-spesifik).
*   **Lihat Detail:** [./02-topik-lanjutan/02-storage-lanjutan/](./02-topik-lanjutan/02-storage-lanjutan/)

### 2.3 Security: Membangun Benteng Pertahanan
Mengamankan cluster dan aplikasi adalah tanggung jawab bersama.
*   **Authentication (AuthN): Siapa Anda?** Verifikasi identitas User Accounts (manusia) dan Service Accounts (proses). Strategi: Sertifikat X.509, Static Token Files, Bootstrap Tokens, OpenID Connect (OIDC) Tokens, Webhook Token Authentication. K8s tidak punya manajemen user internal.
*   **Authorization (AuthZ): Apa yang Boleh Anda Lakukan?** RBAC (Role-Based Access Control) adalah mekanisme utama.
    *   `Role` (Namespace-scoped) & `ClusterRole` (Cluster-scoped): Mendefinisikan izin (verbs: get, list, watch, create, update, patch, delete) pada resources (pods, services, nodes) dan apiGroups.
    *   `RoleBinding` & `ClusterRoleBinding`: Menghubungkan User/Group/ServiceAccount ke Role/ClusterRole.
    *   Prinsip Least Privilege: Berikan izin seminimal mungkin.
    *   Mode lain (kurang umum): ABAC, Node, Webhook.
*   **Service Accounts (Detail):** Identitas untuk Pods. Token Service Account (JWT) otomatis di-mount ke Pods (di `/var/run/secrets/kubernetes.io/serviceaccount/`). Digunakan untuk otentikasi ke API Server dari dalam Pod atau ke sistem eksternal. `automountServiceAccountToken: false` jika Pod tidak perlu akses API. `imagePullSecrets`.
*   **Security Contexts:** Pengaturan keamanan level Pod atau Kontainer.
    *   `runAsUser`, `runAsGroup`, `fsGroup`: Menjalankan proses sebagai user ID non-root.
    *   `allowPrivilegeEscalation: false`: Mencegah proses mendapatkan privilege lebih.
    *   `capabilities`: Kontrol Linux capabilities (drop ALL, add specific).
    *   `readOnlyRootFilesystem: true`.
    *   `seLinuxOptions`, `seccompProfile`, `appArmorProfile`: Integrasi dengan mekanisme keamanan Linux.
*   **Pod Security Admission (PSA):** Mekanisme bawaan (pengganti PodSecurityPolicy) untuk menerapkan standar keamanan baseline pada Pods di level Namespace. Profil: `privileged`, `baseline`, `restricted`. Mode: `enforce`, `audit`, `warn`.
*   **Secrets Management (Lanjutan):** Mengenkripsi Secret di etcd (encryption at rest). Integrasi dengan solusi eksternal seperti HashiCorp Vault atau KMS cloud provider untuk manajemen secret yang lebih aman dan terpusat.
*   **Network Security (Recap):** Network Policies untuk segmentasi. mTLS via Service Mesh.
*   **Lihat Detail Mendalam:** [./02-topik-lanjutan/03-security/](./02-topik-lanjutan/03-security/)

### 2.4 Scheduling Lanjutan: Penempatan Pod Cerdas
Memberi tahu Scheduler di mana (atau tidak di mana) menempatkan Pods.
*   **Node Selectors & Node Affinity:** Memilih Node berdasarkan label Node.
    *   `nodeSelector`: Cara paling sederhana (key=value).
    *   `nodeAffinity`: Lebih ekspresif (required/preferred, operators: In, NotIn, Exists, DoesNotExist, Gt, Lt). `requiredDuringSchedulingIgnoredDuringExecution` vs `preferredDuringSchedulingIgnoredDuringExecution`.
*   **Taints & Tolerations:** Mekanisme penolakan.
    *   `Taint`: Diterapkan pada Node (key=value:Effect). Effect: `NoSchedule` (tidak dijadwalkan), `PreferNoSchedule` (dihindari), `NoExecute` (menggusur Pod yang sudah berjalan jika tidak mentolerir).
    *   `Toleration`: Diterapkan pada Pod, memungkinkan Pod dijadwalkan di Node dengan Taint yang cocok (key, operator, value, effect).
    *   Use case: Node dedicated, Node dengan hardware khusus, Node dalam maintenance.
*   **Pod Affinity & Anti-Affinity:** Menempatkan Pod relatif terhadap Pod lain (di Node yang sama/berbeda, di zona topologi yang sama/berbeda). `required...` vs `preferred...`. `topologyKey` (e.g., `kubernetes.io/hostname`, `topology.kubernetes.io/zone`). Use case: Collocation (cache & app), High Availability (menyebar Pods).
*   **Topology Spread Constraints:** Kontrol yang lebih halus untuk menyebarkan Pods secara merata di seluruh domain topologi (Nodes, Zones, Regions). `maxSkew`, `whenUnsatisfiable` (DoNotSchedule, ScheduleAnyway), `labelSelector`.
*   **Priority & Preemption:** Menetapkan prioritas pada Pods (`PriorityClass`). Pod dengan prioritas lebih tinggi dapat menggusur (preempt) Pod dengan prioritas lebih rendah jika tidak ada resource yang cukup.
*   **Lihat Detail & Contoh Kompleks:** [./02-topik-lanjutan/04-scheduling-lanjutan/](./02-topik-lanjutan/04-scheduling-lanjutan/)

### 2.5 Observability: Melihat ke Dalam Sistem
Memahami apa yang terjadi di dalam cluster dan aplikasi Anda.
*   **Metrics:**
    *   `metrics-server`: Sumber metrik resource dasar (CPU, Memori) untuk Pods & Nodes. Digunakan oleh HPA dan `kubectl top`. Ringan, in-memory.
    *   **Prometheus:** Standar de-facto untuk monitoring & alerting di ekosistem K8s/CNCF. Model pull-based (scrape), penyimpanan time-series (TSDB), bahasa query PromQL yang kuat, Alertmanager untuk notifikasi. Perlu di-deploy terpisah (sering via Helm chart `kube-prometheus-stack`). Exporters (node-exporter, app exporters).
*   **Visualisasi (Grafana):** Membuat dashboard interaktif dari berbagai sumber data (Prometheus, Loki, Elasticsearch, dll.). Sangat fleksibel dan populer.
*   **Logging:**
    *   Arsitektur Umum: Aplikasi menulis log ke stdout/stderr -> Container Runtime menangkapnya -> Agen logging (DaemonSet: Fluentd, Fluent Bit, Promtail) membaca log dari Node -> Mengirim ke backend agregasi log.
    *   Backend: Elasticsearch (pencarian kuat), Loki (indeks label seperti Prometheus, lebih ringan).
    *   Visualisasi: Kibana (untuk Elasticsearch), Grafana (untuk Loki).
*   **Tracing:** Mengikuti alur permintaan saat melewati berbagai service (distributed tracing). Penting untuk microservices. Konsep: Spans, Trace ID. Alat: Jaeger, Zipkin. Membutuhkan instrumentasi kode aplikasi atau integrasi service mesh.
*   **Lihat Arsitektur & Konfigurasi:** [./02-topik-lanjutan/05-observability/](./02-topik-lanjutan/05-observability/)

### 2.6 Manajemen Sumber Daya Lanjutan
Mengontrol dan mengoptimalkan penggunaan resource cluster.
*   **Resource Quotas:** Menetapkan batas total penggunaan resource (CPU, memori, storage, jumlah objek: pods, services, pvcs) per Namespace. Mencegah satu tim/aplikasi menghabiskan semua resource.
*   **Limit Ranges:** Menetapkan batasan default, minimum, atau maksimum untuk `requests` dan `limits` resource per Pod atau Kontainer dalam sebuah Namespace. Memastikan Pods memiliki batas yang wajar.
*   **Implikasi QoS (Recap):** Bagaimana `requests` & `limits` mempengaruhi kelas QoS (Guaranteed, Burstable, BestEffort) dan bagaimana K8s menangani tekanan resource (OOMKiller priority).
*   **Lihat Detail:** [./02-topik-lanjutan/06-manajemen-sumber-daya/](./02-topik-lanjutan/06-manajemen-sumber-daya/)

### 2.7 Package Management: Helm Sang Juru Mudi Aplikasi
Mengelola aplikasi Kubernetes yang kompleks sebagai paket (Charts).
*   **Konsep:**
    *   `Chart`: Paket Helm (kumpulan file YAML template, nilai default, metadata).
    *   `Release`: Instance dari Chart yang di-deploy ke cluster.
    *   `Repository`: Tempat menyimpan dan berbagi Charts (HTTP server).
    *   `Values`: Parameter untuk mengkustomisasi Chart saat instalasi/upgrade (`values.yaml`, `--set`, `--values`).
*   **Struktur Chart:** `Chart.yaml` (metadata), `values.yaml` (default), `templates/` (file YAML dengan Go templating), `charts/` (dependensi/subcharts), `crds/`.
*   **Templating:** Menggunakan sintaks Go template (`{{ .Values.key }}`), functions (`include`, `required`, `tpl`), flow control (`if`, `range`), named templates (`define`). Memungkinkan Chart yang dinamis dan reusable.
*   **Dependensi (Subcharts):** Mengelola Chart lain sebagai dependensi.
*   **Lifecycle Hooks:** Menjalankan Job K8s pada titik-titik tertentu dalam siklus hidup Release (`pre-install`, `post-install`, `pre-delete`, `post-delete`, `pre-upgrade`, `post-upgrade`).
*   **Perintah Helm:** `helm create`, `helm install`, `helm upgrade`, `helm rollback`, `helm list`, `helm status`, `helm template`, `helm package`, `helm repo add/update`.
*   **Lihat Detail & Praktik Terbaik:** [./02-topik-lanjutan/07-package-management-helm/](./02-topik-lanjutan/07-package-management-helm/)

### 2.8 Mengembangkan Kubernetes: CRDs & Operators
Memperluas API Kubernetes untuk kebutuhan spesifik Anda.
*   **Custom Resource Definitions (CRD):** Cara untuk menambahkan tipe objek *baru* ke API Kubernetes Anda sendiri, tanpa perlu memodifikasi kode K8s inti. Anda mendefinisikan skema (menggunakan OpenAPI v3) untuk resource baru Anda.
*   **Operators:** Pola desain untuk mengemas, men-deploy, dan mengelola aplikasi Kubernetes (terutama yang stateful atau kompleks) menggunakan CRD dan *custom controller*.
    *   **Tujuan:** Meng-encode pengetahuan operasional domain-spesifik (mis: bagaimana melakukan backup database, upgrade cluster Kafka, failover Redis) ke dalam perangkat lunak.
    *   **Cara Kerja:** Operator adalah Pod yang berjalan di cluster, mengawasi Custom Resource (CR) yang terkait dengannya. Ketika CR dibuat/diperbarui/dihapus, controller Operator melakukan tindakan yang sesuai (membuat/mengelola Pods, Services, ConfigMaps, PVCs, bahkan berinteraksi dengan API eksternal).
    *   **Tools:** Operator Framework (Operator SDK, Kubebuilder, Metacontroller) membantu membangun Operator.
    *   **Contoh:** Prometheus Operator, etcd Operator, database operators (Postgres, MySQL), Kafka Operator (Strimzi).
*   **Lihat Detail Pola & Pengembangan:** [./02-topik-lanjutan/08-mengembangkan-kubernetes/](./02-topik-lanjutan/08-mengembangkan-kubernetes/)

---

*(Bagian Praktik Langsung, Alat Bantu, Praktik Terbaik, Troubleshooting, Studi Kasus, Sumber Lanjut, Kontribusi, dan Lisensi akan menyusul, masing-masing diperluas dengan detail serupa untuk mencapai kedalaman yang diinginkan.)*

---

## 🛠️ Bagian Tiga: Praktik Langsung - Mengotori Tangan Anda

Teori itu penting, tetapi pemahaman sejati datang dari praktik. Bagian ini berisi panduan langkah demi langkah untuk men-deploy dan mengelola aplikasi nyata di cluster Kubernetes Anda. Setiap tutorial dirancang untuk mengilustrasikan konsep-konsep yang telah dibahas.

*(Setiap direktori di bawah ini akan berisi README.md detail, kode aplikasi contoh jika perlu, Dockerfile, dan file manifest YAML yang relevan, dengan penjelasan untuk setiap langkah dan perintah.)*

*   **[Lab 01: Deploy, Expose, Scale Aplikasi Web Stateless](./03-praktek-langsung/01-deploy-stateless-app/)**
    *   Membangun image Docker sederhana (mis: Python Flask/Node Express).
    *   Menulis `Deployment` YAML untuk menjalankan beberapa replika.
    *   Menulis `Service` YAML (ClusterIP) untuk akses internal.
    *   Menggunakan `kubectl scale` dan `kubectl rollout` (update image).
    *   (Opsional) Menambahkan `HorizontalPodAutoscaler` (HPA).
*   **[Lab 02: Deploy Aplikasi Stateful dengan Penyimpanan Persisten](./03-praktek-langsung/02-deploy-stateful-app/)**
    *   Menulis `StorageClass` (jika menggunakan dynamic provisioning).
    *   Menulis `Headless Service`.
    *   Menulis `StatefulSet` YAML dengan `volumeClaimTemplates` untuk PVC dinamis.
    *   Men-deploy database sederhana (mis: PostgreSQL atau MySQL) atau aplikasi stateful contoh.
    *   Menguji persistensi data (hapus Pod, lihat apakah data tetap ada).
    *   Mengamati pembuatan Pod dan PVC yang terurut.
*   **[Lab 03: Mengelola Konfigurasi dan Secrets](./03-praktek-langsung/03-konfigurasi-secret/)**
    *   Membuat `ConfigMap` dari file atau literal.
    *   Membuat `Secret` dari literal (`stringData`) atau file (mis: sertifikat TLS).
    *   Me-mount ConfigMap/Secret sebagai environment variables ke dalam Pod.
    *   Me-mount ConfigMap/Secret sebagai volume file ke dalam Pod.
    *   Mengamati bagaimana perubahan pada ConfigMap/Secret dipropagasi (atau tidak).
*   **[Lab 04: Mengekspos Aplikasi ke Dunia Luar dengan Ingress](./03-praktek-langsung/04-expose-app-ingress/)**
    *   Men-deploy Ingress Controller (mis: Nginx Ingress via Helm).
    *   Membuat resource `Ingress` untuk merutekan traffic berdasarkan host atau path ke Service(s) yang berbeda.
    *   Mengkonfigurasi TLS termination pada Ingress (menggunakan Secret TLS).
    *   Mengakses aplikasi dari luar cluster melalui Ingress Controller.
*   **[Lab 05: Setup Monitoring Dasar dengan Prometheus & Grafana](./03-praktek-langsung/05-setup-monitoring-sederhana/)**
    *   Men-deploy stack `kube-prometheus-stack` menggunakan Helm.
    *   Mengakses UI Prometheus dan Grafana.
    *   Menjelajahi metrik cluster dan node yang dikumpulkan.
    *   Membuat dashboard sederhana di Grafana.

---

## 🧰 Bagian Empat: Ekosistem Tools - Memperluas Arsenal Anda

Kubernetes memiliki ekosistem alat bantu yang sangat kaya yang dapat secara dramatis meningkatkan produktivitas dan efisiensi Anda.

*(Setiap file di bawah ini akan membahas alat-alat spesifik, kasus penggunaannya, dan contoh perintah/konfigurasi.)*

*   **[kubectl Power User](./04-ekosistem-tools/01-kubectl-power-user.md):** Melampaui dasar `get`, `describe`, `apply`, `delete`. Kustomisasi output (`-o jsonpath`, `-o custom-columns`), plugin (`krew`), alias shell, `kubectl explain`, debugging (`debug`, `port-forward`, `exec`, `logs --previous`).
*   **[GUI Dashboards & Terminal UIs](./04-ekosistem-tools/02-gui-dashboards.md):** Alternatif visual untuk `kubectl`.
    *   **Lens:** IDE Kubernetes open-source yang kuat. Visualisasi resource, metrik real-time, manajemen multi-cluster.
    *   **k9s:** UI berbasis terminal yang sangat cepat dan efisien untuk navigasi & manajemen cluster. Favorit banyak engineer.
    *   **Kubernetes Dashboard:** Dashboard web resmi (perlu di-deploy dan diamankan).
*   **[Alat Workflow Pengembangan](./04-ekosistem-tools/03-dev-workflow-tools.md):** Mempercepat loop pengembangan inner-loop (code -> build -> deploy -> test).
    *   **Skaffold:** Mengotomatiskan build image, push ke registry, dan deploy ke K8s setiap kali kode berubah. Mendukung berbagai builder & deployer.
    *   **Tilt:** Fokus pada pengalaman pengembangan multi-service lokal di K8s. Update live, UI terintegrasi.
    *   **Telepresence:** Memungkinkan Anda menjalankan service lokal seolah-olah berada di dalam cluster K8s (proxying network).
*   **[CI/CD & GitOps Tools](./04-ekosistem-tools/04-ci-cd-gitops.md):** Mengotomatiskan deployment dan menjaga sinkronisasi cluster dengan repositori Git.
    *   **Argo CD:** Alat GitOps deklaratif populer (pull-based). Memantau repositori Git dan secara otomatis menerapkan perubahan manifest ke cluster. UI bagus.
    *   **Flux CD:** Alternatif GitOps lain (pull-based), bagian dari CNCF. Integrasi erat dengan Helm & Kustomize.
    *   (Alat CI tradisional seperti Jenkins, GitLab CI, GitHub Actions juga dapat digunakan untuk *memicu* deployment ke K8s).
*   **[Policy Management & Governance](./04-ekosistem-tools/05-policy-management.md):** Menerapkan aturan dan best practices secara otomatis.
    *   **OPA (Open Policy Agent) Gatekeeper:** Menggunakan OPA untuk menerapkan kebijakan kustom pada objek K8s saat admission (create/update). Menggunakan CRD `ConstraintTemplate` dan `Constraint`.
    *   **Kyverno:** Alternatif policy engine native Kubernetes. Kebijakan ditulis langsung sebagai resource K8s. Bisa memvalidasi, memutasi, dan menghasilkan resource.

---

## ✅ Bagian Lima: Pola & Praktik Terbaik - Jalan Kearifan Kubernetes

Menjalankan Kubernetes itu mudah, menjalankannya *dengan baik* membutuhkan disiplin dan mengikuti praktik yang terbukti. Bagian ini menyaring kearifan komunitas.

*(Setiap file akan membahas area spesifik dengan rekomendasi konkret dan alasan di baliknya.)*

*   **[Desain Aplikasi Cloud-Native](./05-pola-praktik-terbaik/01-desain-aplikasi.md):** Mengadaptasi prinsip 12-Factor App untuk K8s. Pentingnya health checks (`livenessProbe`, `readinessProbe`, `startupProbe`) yang akurat. Graceful shutdown (menangani SIGTERM). Statelessness vs Statefulness.
*   **[Manajemen Konfigurasi & Secrets](./05-pola-praktik-terbaik/02-manajemen-konfigurasi.md):** Gunakan ConfigMap/Secret daripada hardcoding. Hindari menyimpan secret di Git. Pertimbangkan GitOps untuk manajemen deklaratif. Enkripsi Secret at-rest. Gunakan solusi manajemen secret eksternal (Vault) untuk kasus lanjut. Mount sebagai volume > env vars untuk secrets.
*   **[Keamanan Berlapis](./05-pola-praktik-terbaik/03-keamanan.md):** Terapkan RBAC dengan least privilege. Gunakan Network Policies untuk segmentasi. Jalankan kontainer sebagai non-root (`securityContext`). Batasi privilege (`allowPrivilegeEscalation: false`, drop capabilities). Gunakan Pod Security Admission. Jaga image tetap terupdate (scan vulnerability). Audit logs.
*   **[Manajemen Resource yang Bijak](./05-pola-praktik-terbaik/04-manajemen-resource.md):** *Selalu* set `requests` dan `limits` untuk CPU & Memori. Pahami QoS Classes. Gunakan `ResourceQuota` dan `LimitRange` untuk mengontrol penggunaan namespace. Monitor utilisasi resource.
*   **[Observability Terpadu](./05-pola-praktik-terbaik/05-observability.md):** Implementasikan logging terpusat. Gunakan Prometheus/Grafana (atau alternatif) untuk metrics dan alerting. Pertimbangkan distributed tracing untuk microservices. Pastikan Anda dapat menjawab: Apa yang sedang terjadi? Mengapa ini terjadi?
*   **[Strategi Storage](./05-pola-praktik-terbaik/06-storage.md):** Pilih tipe Volume yang tepat untuk kasus penggunaan. Gunakan PV/PVC untuk data persisten. Pilih `reclaimPolicy` yang sesuai (Retain untuk data penting). Gunakan Dynamic Provisioning dengan StorageClasses. Pertimbangkan backup/restore (Volume Snapshots).
*   **[Penamaan & Labeling Konsisten](./05-pola-praktik-terbaik/07-penamaan-labeling.md):** Terapkan konvensi penamaan yang jelas untuk semua objek. Gunakan label secara strategis untuk mengorganisir resource berdasarkan aplikasi, lingkungan, tim, dll. Ini sangat membantu filtering, policy, dan pemahaman. Gunakan Annotations untuk metadata tambahan.

---

## 🚑 Bagian Enam: Troubleshooting Cookbook - Saat Badai Datang

Masalah pasti akan muncul. Memiliki pendekatan sistematis dan mengetahui di mana mencari petunjuk adalah kunci untuk menyelesaikan masalah dengan cepat.

*(Setiap file akan fokus pada jenis masalah tertentu dengan langkah-langkah diagnosis dan perintah `kubectl` yang relevan.)*

*   **[Metodologi Umum](./06-troubleshooting-cookbook/01-metodologi-umum.md):** Pendekatan top-down vs bottom-up. Periksa event (`kubectl get events --sort-by='.lastTimestamp'`). Gunakan `kubectl describe` secara ekstensif. Isolasi masalah (apakah hanya satu Pod, satu Node, satu Namespace?). Periksa log Control Plane (jika self-hosted).
*   **[Masalah Umum Pod](./06-troubleshooting-cookbook/02-masalah-pod.md):**
    *   `Pending`: `describe pod` (Scheduler events, resource不足, taint/toleration, PVC unbound).
    *   `ImagePullBackOff`/`ErrImagePull`: `describe pod` (nama image salah, tag tidak ada, registry down, `imagePullSecrets` salah/hilang).
    *   `CrashLoopBackOff`: `logs --previous` (lihat error aplikasi), `describe pod` (exit code), periksa command/args, `livenessProbe`.
    *   `ContainerCreating`: `describe pod` (masalah mounting volume, CNI, container runtime).
    *   `Terminating` (Stuck): `describe pod`, periksa `terminationGracePeriodSeconds`, apakah aplikasi menangani SIGTERM? `kubectl delete pod --grace-period=0 --force` (hati-hati!).
    *   `OOMKilled`: `describe pod` (Reason: OOMKilled), periksa `limits.memory`, profil penggunaan memori aplikasi.
*   **[Masalah Jaringan](./06-troubleshooting-cookbook/03-masalah-jaringan.md):**
    *   Pod-ke-Pod: `kubectl exec` untuk `ping`/`curl` IP Pod tujuan. Periksa CNI. Periksa Network Policies.
    *   DNS Resolution: `kubectl exec` untuk `nslookup <service-name>`. Periksa log CoreDNS (`kubectl logs -n kube-system -l k8s-app=kube-dns`). Periksa konfigurasi DNS Node.
    *   Service Connectivity: `kubectl get endpoints <service-name>` (apakah ada IP Pod di sana?). `describe service`. Periksa selector Service vs label Pod. `kubectl port-forward svc/<service-name> <local-port>:<service-port>`. Periksa log `kube-proxy` (level verbose tinggi).
    *   Ingress: `describe ingress`. Periksa log Ingress Controller. Periksa apakah Service backend berfungsi. Periksa konfigurasi DNS eksternal.
*   **[Masalah Storage](./06-troubleshooting-cookbook/04-masalah-storage.md):**
    *   PVC `Pending`: `describe pvc`. Tidak ada PV yang cocok (ukuran, access mode, storage class)? StorageClass salah? Provisioner dinamis error? `kubectl get pv`.
    *   Pod `ContainerCreating` (Mount Error): `describe pod` (event MountVolume). Masalah CSI driver? Masalah izin? Volume sudah di-mount oleh Node lain (untuk RWO)?
*   **[Masalah Control Plane (Self-hosted)](./06-troubleshooting-cookbook/05-masalah-control-plane.md):** Periksa log `kube-apiserver`, `kube-scheduler`, `kube-controller-manager`, `etcd`. Periksa status service/pods mereka. Masalah sertifikat? Masalah konektivitas etcd?
*   **[Masalah Performa](./06-troubleshooting-cookbook/06-masalah-performa.md):** `kubectl top pod/node`. Profiling aplikasi. Resource `requests`/`limits` terlalu rendah/tinggi? Node bottleneck? Masalah jaringan latensi tinggi?

---

## 🏛️ Bagian Tujuh: Studi Kasus & Arsitektur Referensi

Melihat bagaimana konsep-konsep ini diterapkan dalam skenario nyata dapat memperkuat pemahaman.

*(Bagian ini akan berisi deskripsi arsitektur contoh, diagram, dan manifest YAML kunci untuk kasus penggunaan umum.)*

*   **[Aplikasi Web Multi-Tier (Frontend, Backend API, Database)](./07-studi-kasus-arsitektur/01-web-app-multi-tier.md):** Menggunakan Deployments, Services, ConfigMaps, Secrets, Ingress, dan StatefulSet (untuk database).
*   **[Pipeline Pemrosesan Data Asinkron](./07-studi-kasus-arsitektur/02-pipeline-data-processing.md):** Menggunakan Jobs/CronJobs, message queue (mis: RabbitMQ/Kafka di K8s), workers (Deployments).
*   **[Hosting Database dengan Ketersediaan Tinggi](./07-studi-kasus-arsitektur/03-hosting-database.md):** Menggunakan StatefulSet, Pod Anti-Affinity, PV/PVC, Headless Service, mungkin Operator database.

---

## 📖 Glosarium & Bacaan Lanjutan

*   **[GLOSSARY.md](./GLOSSARY.md):** Definisi cepat untuk istilah-istilah kunci Kubernetes.
*   **[FURTHER_READING.md](./FURTHER_READING.md):** Kumpulan tautan ke dokumentasi resmi, blog, buku, kursus, dan sumber daya komunitas lainnya untuk pendalaman tanpa akhir.

---

## 🙌 Kontribusi: Mari Bangun Bersama!

Repositori ini adalah upaya hidup yang dapat terus ditingkatkan oleh komunitas. Kontribusi Anda sangat berharga!

1.  **Laporkan Kesalahan/Saran:** Temukan typo, informasi usang, atau punya ide brilian? Buat [Issue](https://github.com/USERNAME/belajar-kubernetes/issues) baru (Ganti USERNAME/belajar-kubernetes dengan URL repo Anda).
2.  **Sumbangkan Konten/Perbaikan (Pull Requests):**
    *   Fork repositori ini.
    *   Buat branch fitur/perbaikan (`git checkout -b feat/tambah-detail-csi`).
    *   Lakukan perubahan Anda. Ikuti gaya dan struktur yang ada.
    *   Commit perubahan Anda dengan pesan yang jelas (`git commit -m "docs: Menambahkan penjelasan detail CSI Node Plugin"`).
    *   Push ke fork Anda (`git push origin feat/tambah-detail-csi`).
    *   Buat Pull Request ke branch `main` repositori ini. Jelaskan PR Anda.

Setiap kontribusi, sekecil apapun, sangat dihargai!

---

## 📜 Lisensi

Repositori dan konten di dalamnya dilisensikan di bawah [MIT License](./LICENSE).
