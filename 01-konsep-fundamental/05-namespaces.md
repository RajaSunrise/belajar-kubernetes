# Namespaces: Mempartisi Cluster Secara Logis

Seiring bertambahnya ukuran dan kompleksitas cluster Kubernetes Anda, atau ketika digunakan oleh banyak tim atau untuk menjalankan banyak aplikasi berbeda, Anda memerlukan cara untuk **mengorganisir sumber daya** dan **mengontrol akses**. Di sinilah **Namespaces** berperan.

## Apa itu Namespace?

Namespace menyediakan mekanisme untuk **mempartisi (membagi)** sumber daya dalam satu cluster Kubernetes fisik menjadi beberapa **ruang kerja virtual**. Anggap saja seperti folder di sistem file Anda; file dalam satu folder terpisah dari file di folder lain, meskipun berada di disk fisik yang sama.

**Penting:** Namespace **tidak** menyediakan isolasi sumber daya fisik (CPU, Memori, Jaringan) secara default. Mereka utamanya untuk **isolasi logis**.

## Tujuan Utama Namespaces

1.  **Scope untuk Nama Objek:**
    *   Nama sebagian besar sumber daya Kubernetes (seperti Pods, Services, Deployments, ConfigMaps, Secrets, PVCs) harus unik **di dalam satu Namespace**.
    *   Anda dapat memiliki objek dengan nama yang sama di Namespace yang berbeda. Misalnya, `Service` bernama `database` di namespace `development` berbeda dan terpisah dari `Service` bernama `database` di namespace `production`.
    *   Ini mencegah konflik penamaan antar tim atau aplikasi yang berbeda.

2.  **Kontrol Akses (RBAC):**
    *   Kebijakan otorisasi **RBAC (Role-Based Access Control)** dapat diterapkan pada level Namespace. Anda dapat membuat `Roles` dan `RoleBindings` yang memberikan izin spesifik kepada pengguna atau grup hanya di dalam Namespace tertentu.
    *   Misalnya, tim A hanya diberi izin untuk membuat dan mengelola sumber daya di namespace `team-a`, sementara tim B hanya bisa di namespace `team-b`. Administrator cluster memiliki akses ke semua namespace.

3.  **Manajemen Kuota Sumber Daya (`ResourceQuota`):**
    *   Administrator dapat menetapkan **kuota** untuk total penggunaan sumber daya (CPU, Memori, Storage) atau jumlah objek (Pods, Services, PVCs) yang dapat dibuat **per Namespace**.
    *   Ini mencegah satu tim/aplikasi/lingkungan menghabiskan semua sumber daya cluster.

4.  **Manajemen Kebijakan Jaringan (`NetworkPolicy`):**
    *   Objek `NetworkPolicy` beroperasi pada level Namespace, memungkinkan Anda mendefinisikan aturan firewall untuk mengontrol lalu lintas masuk (ingress) dan keluar (egress) antara Pods di dalam dan antar Namespace.

## Objek Namespaced vs. Cluster-Scoped

Tidak semua objek Kubernetes berada di dalam Namespace. Ada dua kategori:

1.  **Objek Namespaced:** Sebagian besar objek yang Anda buat terkait aplikasi berada di dalam Namespace. Contoh:
    *   Pods
    *   Services
    *   Deployments, StatefulSets, DaemonSets, ReplicaSets, Jobs, CronJobs
    *   ConfigMaps, Secrets
    *   PersistentVolumeClaims (PVCs)
    *   Ingresses
    *   Roles, RoleBindings
    *   NetworkPolicies
    *   ServiceAccounts
2.  **Objek Cluster-Scoped:** Objek ini ada di level cluster dan tidak terikat pada Namespace tertentu. Contoh:
    *   Nodes
    *   Namespaces itu sendiri
    *   PersistentVolumes (PVs)
    *   StorageClasses
    *   ClusterRoles, ClusterRoleBindings
    *   CustomResourceDefinitions (CRDs)

Anda tidak dapat membuat objek namespaced tanpa menentukan namespace (akan masuk ke `default` atau konteks saat ini) dan Anda tidak dapat menentukan namespace saat membuat objek cluster-scoped.

## Namespace Default yang Ada

Saat Anda pertama kali menyiapkan cluster Kubernetes, beberapa Namespace sudah dibuat secara otomatis:

*   **`default`:** Namespace default yang digunakan jika Anda tidak menentukan namespace lain saat membuat objek namespaced. Sebaiknya **hindari** menggunakan namespace `default` untuk aplikasi produksi atau proyek yang signifikan; lebih baik buat namespace spesifik untuk tujuan Anda.
*   **`kube-system`:** Namespace ini digunakan oleh **komponen sistem Kubernetes** itu sendiri (misalnya, Pods untuk API Server, Controller Manager, Scheduler, CoreDNS, kube-proxy, CNI plugin). **Jangan** membuat objek aplikasi Anda di namespace ini kecuali Anda tahu persis apa yang Anda lakukan.
*   **`kube-public`:** Namespace ini dapat dibaca oleh semua pengguna (bahkan yang tidak terautentikasi) secara default. Biasanya digunakan untuk mengekspos informasi cluster tertentu yang perlu dapat diakses publik. Jarang digunakan secara umum.
*   **`kube-node-lease`:** Berisi objek `Lease` untuk setiap Node, yang digunakan oleh Kubelet untuk mengirim heartbeat dan menentukan ketersediaan Node. Ini adalah mekanisme internal.

## Bekerja dengan Namespaces menggunakan `kubectl`

*   **Melihat semua Namespaces:**
    ```bash
    kubectl get namespaces
    # atau
    kubectl get ns
    ```
*   **Membuat Namespace baru:**
    ```bash
    kubectl create namespace my-namespace
    # atau via YAML:
    # apiVersion: v1
    # kind: Namespace
    # metadata:
    #   name: my-namespace
    ```
*   **Melihat objek dalam Namespace spesifik:**
    ```bash
    kubectl get pods --namespace=my-namespace
    # atau
    kubectl get pods -n my-namespace
    ```
*   **Mengatur Namespace default untuk konteks `kubectl` saat ini:**
    ```bash
    kubectl config set-context --current --namespace=my-namespace
    # Setelah ini, perintah 'kubectl get pods' akan otomatis melihat di 'my-namespace'
    ```
*   **Menghapus Namespace:**
    ```bash
    kubectl delete namespace my-namespace
    # PERHATIAN: Menghapus namespace akan menghapus SEMUA objek di dalamnya!
    # Proses penghapusan bisa memakan waktu jika banyak objek. Statusnya akan 'Terminating'.
    ```

## Kapan Menggunakan Namespace?

Gunakan Namespace untuk memisahkan:

*   **Lingkungan:** `development`, `staging`, `production`.
*   **Tim:** `team-alpha`, `team-beta`, `infra`.
*   **Aplikasi/Proyek:** `project-x-frontend`, `project-x-backend`, `logging-stack`.
*   **Tingkat Keamanan/Kekritisan:** `critical-apps`, `batch-jobs`.

Menggunakan Namespace secara efektif adalah praktik fundamental untuk menjaga cluster Kubernetes Anda tetap terorganisir, aman, dan mudah dikelola seiring pertumbuhannya.
