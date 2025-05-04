# Objek Kubernetes: Batu Bata Pembangun Cluster

Di Kubernetes, **Objek** adalah entitas persisten yang merepresentasikan **state (keadaan)** dari cluster Anda. Objek-objek ini menggambarkan:

*   Aplikasi apa yang sedang berjalan dalam kontainer.
*   Di Node mana aplikasi tersebut berjalan.
*   Sumber daya (CPU, memori, storage) apa yang tersedia untuk aplikasi tersebut.
*   Kebijakan apa yang mengatur perilaku aplikasi (misalnya, kebijakan restart, update, penskalaan, jaringan).

Pada dasarnya, ketika Anda berinteraksi dengan Kubernetes (misalnya, menggunakan `kubectl`), Anda membuat, membaca, memperbarui, atau menghapus (operasi CRUD - Create, Read, Update, Delete) objek-objek ini melalui **Kubernetes API**.

## Model Deklaratif & State

Seperti yang dibahas dalam Filosofi Desain, Kubernetes bekerja dengan model **deklaratif**. Anda tidak memberi tahu Kubernetes *bagaimana* melakukan sesuatu, tetapi Anda mendefinisikan *state akhir yang diinginkan* untuk objek tertentu.

Setiap objek Kubernetes memiliki dua bagian utama yang berkaitan dengan state:

1.  **`spec` (Spesifikasi):** Bagian ini Anda **tentukan** saat membuat objek. `spec` mendeskripsikan **state yang Anda inginkan** (desired state) untuk objek tersebut. Misalnya, dalam `spec` sebuah Deployment, Anda menentukan image kontainer yang ingin dijalankan dan jumlah replika yang diinginkan. Strukturnya sangat bervariasi tergantung pada `kind` (jenis) objek.
2.  **`status`:** Bagian ini berisi informasi tentang **state aktual (saat ini)** dari objek, sebagaimana diamati dan diperbarui oleh **sistem Kubernetes** (Control Plane dan komponennya). Anda **tidak** mengedit bagian `status` secara manual. Kubernetes yang mengisinya. Misalnya, `status` sebuah Deployment akan berisi jumlah replika yang saat ini benar-benar berjalan dan siap.

Kubernetes (melalui Controller-nya) terus bekerja untuk **merekonsiliasi** state aktual (`status`) agar sesuai dengan state yang diinginkan (`spec`).

## Struktur Umum Objek Kubernetes (YAML/JSON)

Ketika Anda mendefinisikan objek Kubernetes, Anda biasanya menggunakan format **YAML** (meskipun JSON juga didukung). Setiap definisi objek Kubernetes memerlukan setidaknya field-field berikut di tingkat atas:

```yaml
apiVersion: group/version  # Wajib: Versi API Kubernetes yang digunakan
kind: ObjectKind           # Wajib: Jenis objek yang ingin dibuat
metadata:                  # Wajib: Data untuk mengidentifikasi objek
  name: my-object-name     #   Wajib: Nama unik objek dalam namespace/cluster
  namespace: my-namespace  #   Opsional: Namespace tempat objek berada (jika namespaced)
  labels:                  #   Opsional: Key-value pairs untuk seleksi/pengorganisasian
    key1: value1
  annotations:             #   Opsional: Key-value pairs untuk metadata non-identifikasi
    keyA: valueA
  uid: ...                 #   (Diisi oleh sistem) ID unik cluster-wide
  # ... bidang metadata lainnya ...
spec:                      # Wajib (biasanya): State yang Anda inginkan untuk objek ini
  # ... struktur bidang spec sangat bervariasi tergantung 'kind' ...
  replicas: 3
  template:
    # ... (definisi Pod template untuk Deployment)
status:                    # (Diisi oleh sistem): State aktual objek
  # ... struktur bidang status bervariasi ...
  readyReplicas: 3
  conditions: [...]
```

Mari kita bahas field-field utama:

*   **`apiVersion` (Wajib):** Menentukan versi Kubernetes API yang akan digunakan untuk membuat objek ini. Ini penting karena API Kubernetes berkembang dan dapat berubah antar versi. Formatnya adalah `group/version` (misalnya, `apps/v1`, `batch/v1`, `storage.k8s.io/v1`) atau hanya `version` untuk grup API inti (misalnya, `v1` untuk Pods, Services, Namespaces, ConfigMaps, Secrets, PV, PVC). Anda perlu menggunakan `apiVersion` yang benar sesuai dengan `kind` objek dan versi cluster Anda. Gunakan `kubectl api-versions` untuk melihat versi yang tersedia di cluster Anda.
*   **`kind` (Wajib):** Menentukan jenis objek Kubernetes yang ingin Anda buat. Contoh: `Pod`, `Service`, `Deployment`, `Namespace`, `ConfigMap`, `Secret`, `PersistentVolumeClaim`, `Ingress`, `StatefulSet`, `DaemonSet`, `Job`, `CronJob`, `Role`, `ClusterRole`, `StorageClass`, dll. Case-sensitive. Gunakan `kubectl api-resources` untuk melihat jenis objek yang tersedia.
*   **`metadata` (Wajib):** Berisi data yang membantu mengidentifikasi objek secara unik. Bidang paling penting di dalamnya:
    *   **`name` (Wajib):** Nama unik untuk objek ini *dalam namespace-nya* (atau di seluruh cluster jika objeknya cluster-scoped seperti Node atau Namespace). Harus sesuai dengan konvensi penamaan DNS (RFC 1123).
    *   **`namespace` (Opsional, Penting):** Namespace tempat objek ini berada. Jika dihilangkan untuk objek namespaced, akan menggunakan namespace `default` atau namespace yang diatur dalam konteks `kubectl` saat ini. Objek cluster-scoped (seperti Node, Namespace, PV, ClusterRole) *tidak* memiliki field `namespace`.
    *   **`labels` (Opsional):** Pasangan key-value string yang dilampirkan ke objek untuk tujuan pengorganisasian dan pemilihan (lihat [Labels & Selectors](./06-labels-selectors.md)).
    *   **`annotations` (Opsional):** Pasangan key-value string untuk melampirkan metadata arbitrer non-identifikasi (lihat [Annotations](./07-annotations.md)).
    *   **`uid`:** ID unik yang dihasilkan oleh sistem Kubernetes saat objek dibuat. Bersifat unik di seluruh waktu dan cluster.
*   **`spec` (Wajib, biasanya):** Ini adalah bagian di mana Anda mendefinisikan **karakteristik dan state yang Anda inginkan** untuk objek tersebut. Konten dari `spec` sangat bergantung pada `kind` objek. Anda harus merujuk ke dokumentasi API Kubernetes untuk detail `spec` dari setiap jenis objek.
*   **`status` (Dikelola Sistem):** Bidang ini diisi dan diperbarui oleh Kubernetes untuk merefleksikan **state aktual** dari objek di dalam cluster. Anda tidak mendefinisikan atau mengubah bidang ini secara langsung.

## Interaksi dengan Objek Menggunakan `kubectl`

Anda mengelola siklus hidup objek Kubernetes menggunakan `kubectl`:

*   **Membuat atau Memperbarui (Deklaratif):**
    ```bash
    kubectl apply -f your-object-definition.yaml
    ```
    (`apply` akan membuat objek jika belum ada, atau memperbaruinya jika sudah ada sesuai definisi di file YAML. Ini cara yang direkomendasikan.)
*   **Membuat (Imperatif - Kurang Umum untuk Objek Kompleks):**
    ```bash
    kubectl create -f your-object-definition.yaml # Gagal jika objek sudah ada
    kubectl run my-pod --image=nginx # Contoh membuat Pod secara imperatif
    ```
*   **Melihat Objek:**
    ```bash
    kubectl get <kind> # Lihat semua objek jenis tertentu di namespace saat ini
    kubectl get <kind> <object-name> # Lihat objek spesifik
    kubectl get pods -n kube-system # Lihat Pods di namespace kube-system
    kubectl get all -A # Coba lihat beberapa jenis objek umum di semua namespace
    kubectl get <kind> <object-name> -o yaml # Lihat definisi YAML lengkap objek
    kubectl get <kind> <object-name> -o json # Lihat definisi JSON lengkap objek
    kubectl get pods -l app=my-app # Lihat Pods dengan label tertentu
    ```
*   **Melihat Detail dan Events:**
    ```bash
    kubectl describe <kind> <object-name>
    # Sangat berguna! Menampilkan detail, kondisi, dan event terkait objek.
    ```
*   **Memperbarui (Imperatif - Gunakan `apply` jika memungkinkan):**
    ```bash
    kubectl edit <kind> <object-name> # Buka editor default untuk mengedit objek live
    kubectl scale deployment my-deploy --replicas=5 # Contoh update spesifik
    kubectl label pod my-pod new-label=true # Contoh update metadata
    ```
*   **Menghapus Objek:**
    ```bash
    kubectl delete <kind> <object-name>
    kubectl delete -f your-object-definition.yaml # Hapus objek yg didefinisikan di file
    kubectl delete pods --all # Hapus semua pods di namespace saat ini (hati-hati!)
    ```

Memahami struktur objek dan cara memanipulasinya melalui API (menggunakan `kubectl`) adalah keterampilan fundamental dalam bekerja dengan Kubernetes.
