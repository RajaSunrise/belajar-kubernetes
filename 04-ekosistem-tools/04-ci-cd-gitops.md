# CI/CD dan GitOps untuk Kubernetes

Mengotomatiskan proses pengiriman perangkat lunak (Continuous Integration/Continuous Delivery - CI/CD) sangat penting untuk tim modern. Di dunia Kubernetes, CI/CD seringkali dikombinasikan dengan pendekatan **GitOps**.

## Apa itu CI/CD?

*   **Continuous Integration (CI):** Praktik mengintegrasikan perubahan kode dari banyak kontributor ke dalam repositori bersama secara sering (biasanya beberapa kali sehari). Setiap integrasi diverifikasi oleh **build otomatis** dan **pengujian otomatis**. Tujuannya adalah mendeteksi masalah integrasi sedini mungkin.
    *   **Output Khas CI untuk K8s:** Container Image yang sudah diuji dan diberi tag versi, mungkin juga Helm Chart atau manifest Kustomize yang sudah di-package.
*   **Continuous Delivery (CD):** Memperluas CI dengan mengotomatiskan **rilis** perubahan yang sudah lolos CI ke lingkungan target (misalnya, staging, produksi). CD memastikan bahwa perangkat lunak dapat dirilis kapan saja dengan menekan satu tombol (atau secara otomatis).
*   **Continuous Deployment (CD):** Langkah lebih lanjut dari Continuous Delivery di mana *setiap* perubahan yang lolos semua tahapan pipeline (build, test, staging) secara **otomatis dideploy ke produksi** tanpa intervensi manual.

## CI/CD Tradisional untuk Kubernetes

Pipeline CI/CD "tradisional" untuk Kubernetes biasanya melibatkan langkah-langkah berikut dalam alat CI/CD (seperti Jenkins, GitLab CI, GitHub Actions, CircleCI):

1.  **Trigger:** Perubahan kode di-push ke repositori Git (misalnya, ke branch `main` atau saat membuat tag rilis).
2.  **Build:** Server CI mengambil kode, menjalankan unit/integration test, dan membangun image kontainer (misalnya, menggunakan `docker build`).
3.  **Tag & Push:** Image yang berhasil dibangun diberi tag versi (misalnya, dari Git tag atau commit hash) dan didorong (pushed) ke container registry (Docker Hub, ECR, GCR, ACR).
4.  **Update Manifests:** Pipeline CI/CD memperbarui file manifest Kubernetes (YAML biasa, Kustomize overlays, atau `values.yaml` Helm) untuk menunjuk ke tag image baru. Perubahan manifest ini mungkin juga di-commit kembali ke Git.
5.  **Deploy:** Pipeline CI/CD menjalankan perintah (biasanya `kubectl apply -f ...`, `kustomize build . | kubectl apply -f -`, atau `helm upgrade ...`) untuk menerapkan manifest yang diperbarui ke cluster Kubernetes target (misalnya, staging).
6.  **Testing (Opsional):** Menjalankan pengujian end-to-end atau smoke test terhadap aplikasi yang baru di-deploy di lingkungan staging.
7.  **Promote/Deploy to Production:** Jika pengujian staging berhasil, proses deploy (langkah 5) diulang untuk lingkungan produksi (mungkin memerlukan persetujuan manual).

**Kelemahan Potensial Pendekatan Tradisional:**

*   **Keamanan Kredensial:** Pipeline CI/CD memerlukan kredensial (kubeconfig, token) untuk mengakses cluster Kubernetes target. Menyimpan dan mengelola kredensial ini dengan aman bisa menjadi tantangan.
*   **Cluster Drift:** Jika seseorang melakukan perubahan manual di cluster (`kubectl edit ...`) yang tidak tercermin di Git, state cluster akan menyimpang dari apa yang didefinisikan di Git. Pipeline CI/CD mungkin tidak menyadari atau tidak dapat memperbaiki penyimpangan ini.
*   **Akses Terbatas:** Sulit untuk mengetahui state *sebenarnya* dari cluster hanya dengan melihat pipeline CI/CD.
*   **Rollback:** Rollback mungkin melibatkan pemicuan ulang pipeline dengan versi sebelumnya, yang bisa jadi lambat.

## GitOps: Pendekatan Modern untuk CD di Kubernetes

**GitOps** adalah paradigma operasional yang menggunakan **repositori Git** sebagai **sumber kebenaran tunggal (single source of truth)** untuk mendefinisikan **state yang diinginkan** dari infrastruktur (termasuk aplikasi Kubernetes). Perubahan pada state yang diinginkan dilakukan melalui mekanisme Git standar (commit, pull request, merge), dan agen otomatis memastikan bahwa state aktual cluster sesuai dengan state yang didefinisikan di Git.

**Prinsip Inti GitOps:**

1.  **Sistem Dideskripsikan Secara Deklaratif:** Seluruh state sistem (aplikasi, konfigurasi, infrastruktur) didefinisikan secara deklaratif dalam format yang dapat disimpan di Git (biasanya YAML Kubernetes, Kustomize, atau Helm Charts).
2.  **State yang Diinginkan Disimpan di Git:** Repositori Git adalah satu-satunya tempat di mana state yang diinginkan didefinisikan dan di-versioning.
3.  **Perubahan Disetujui dan Diterapkan via Git:** Perubahan pada state yang diinginkan dilakukan melalui alur kerja Git (commit, Pull/Merge Request, review). Tidak ada perubahan manual (`kubectl apply/edit`) langsung ke cluster.
4.  **Agen Perangkat Lunak Memastikan Kesesuaian:** Agen otomatis (Operator GitOps) berjalan di dalam cluster, terus menerus membandingkan state yang diinginkan di Git dengan state aktual di cluster, dan secara otomatis menerapkan perubahan yang diperlukan untuk menyelaraskannya (rekonsiliasi).

**Alur Kerja GitOps Umum:**

1.  **CI Tetap Berjalan:** Pipeline CI masih bertanggung jawab untuk build, test, dan push image ke registry. Outputnya bisa berupa tag image baru atau pembaruan pada Helm Chart/Kustomize base.
2.  **Pembaruan Repositori Konfigurasi:** Pipeline CI (atau proses terpisah) membuat Pull Request (PR) ke **repositori konfigurasi GitOps** untuk memperbarui manifest agar menggunakan tag image baru atau versi Chart baru.
3.  **Review & Merge:** PR ditinjau oleh tim, dan jika disetujui, di-merge ke branch target (misalnya, `main` untuk produksi, `staging` untuk staging).
4.  **Agen GitOps Mendeteksi Perubahan:** Agen GitOps (seperti Argo CD atau Flux) yang berjalan di cluster mendeteksi perubahan pada branch yang dipantaunya di repositori konfigurasi GitOps.
5.  **Sinkronisasi & Rekonsiliasi:** Agen GitOps mengambil manifest terbaru dari Git dan membandingkannya dengan state di cluster. Ia kemudian menjalankan `kubectl apply`/`helm upgrade`/dll. secara otomatis untuk menerapkan perubahan dan membuat state cluster sesuai dengan Git.
6.  **Observability:** Agen GitOps biasanya menyediakan UI atau metrik untuk memantau status sinkronisasi dan kesehatan aplikasi.

**Agen GitOps Populer (Pull-based):**

Agen ini berjalan di dalam cluster dan secara aktif *menarik (pull)* perubahan dari Git. Ini lebih aman karena tidak memerlukan kredensial cluster di luar cluster.

*   **Argo CD:**
    *   Proyek kelulusan CNCF. Sangat populer dan kaya fitur.
    *   Menyediakan UI Web yang bagus untuk visualisasi aplikasi, status sinkronisasi, perbedaan (diff), dan riwayat.
    *   Mendukung manifest YAML biasa, Kustomize, Helm, Jsonnet, dan plugin kustom.
    *   Menggunakan CRD `Application` untuk mendefinisikan hubungan antara repositori Git, path, cluster target, dan namespace.
    *   Mendukung sinkronisasi otomatis atau manual, rollback, health checks.

*   **Flux CD:**
    *   Proyek kelulusan CNCF. Pilihan populer lainnya, dikenal lebih modular.
    *   Terdiri dari sekumpulan controller (Toolkit) yang bekerja sama (misalnya, `source-controller`, `kustomize-controller`, `helm-controller`).
    *   Konfigurasi sepenuhnya melalui CRD Kubernetes.
    *   Integrasi erat dengan standar Kubernetes. Tidak memiliki UI bawaan sekomprehensif Argo CD (tetapi UI pihak ketiga tersedia).
    *   Mendukung sumber selain Git (misalnya, Helm Repositories, OCI registries).

**Manfaat GitOps:**

*   **Sumber Kebenaran Tunggal:** Git menjadi deskripsi otoritatif dari state cluster, memudahkan pelacakan dan audit.
*   **Alur Kerja Developer-Centric:** Menggunakan alat yang sudah dikenal (Git, PR) untuk mengelola deployment.
*   **Peningkatan Keamanan:** Kredensial cluster tidak perlu diekspos ke sistem CI eksternal (dengan model pull). Perubahan melalui PR memungkinkan review dan persetujuan.
*   **Konsistensi & Reproducibility:** Mudah untuk mengembalikan ke state sebelumnya (via `git revert`) atau mereplikasi lingkungan yang sama di cluster lain.
*   **Pemulihan Bencana:** Memulihkan cluster menjadi lebih mudah karena state yang diinginkan ada di Git. Cukup arahkan agen GitOps ke repo.
*   **Peningkatan Stabilitas:** Mencegah "cluster drift" karena agen terus menerus menyelaraskan cluster dengan Git.

**GitOps vs CI/CD Tradisional:**

GitOps bukanlah pengganti CI, tetapi lebih merupakan **evolusi dari bagian CD** dalam pipeline. CI masih menangani build dan test image. GitOps mengambil alih proses *deployment* ke cluster dengan fokus pada Git sebagai sumber kebenaran dan rekonsiliasi otomatis oleh agen di dalam cluster.

Mengadopsi GitOps dengan alat seperti Argo CD atau Flux adalah praktik terbaik modern untuk Continuous Delivery di Kubernetes, memberikan peningkatan keamanan, keandalan, dan kemudahan pengelolaan dibandingkan pendekatan push berbasis CI tradisional.
```

---

### FILE: `04-ekosistem-tools/05-policy-management.md`

```markdown
# Manajemen Kebijakan (Policy Management): OPA Gatekeeper & Kyverno

Seiring pertumbuhan cluster Kubernetes dan jumlah pengguna/aplikasi yang berinteraksi dengannya, kebutuhan untuk menerapkan **aturan (policies)** dan **praktik terbaik (best practices)** secara konsisten dan otomatis menjadi sangat penting. Tujuannya adalah untuk:

*   **Keamanan:** Mencegah konfigurasi yang tidak aman (misalnya, menjalankan kontainer sebagai root, mengekspos port berbahaya, tidak adanya network policy).
*   **Kepatuhan (Compliance):** Memastikan konfigurasi memenuhi standar internal atau eksternal (misalnya, CIS Benchmarks, peraturan industri).
*   **Konsistensi Operasional:** Menegakkan konvensi penamaan, penggunaan label wajib, pengaturan resource requests/limits.
*   **Manajemen Biaya:** Mencegah pembuatan sumber daya yang mahal atau tidak perlu.

Meskipun Kubernetes memiliki beberapa mekanisme kebijakan bawaan (seperti RBAC, NetworkPolicy, ResourceQuota, Pod Security Admission), terkadang kita memerlukan **kebijakan kustom** yang lebih fleksibel dan spesifik untuk kebutuhan organisasi. Di sinilah alat **Policy Engine** seperti OPA Gatekeeper dan Kyverno berperan.

## Konsep Dasar: Admission Controllers

Alat manajemen kebijakan ini biasanya bekerja sebagai **Dynamic Admission Controllers** di Kubernetes.

*   **Admission Controllers:** Komponen API Server yang mencegat permintaan ke API Server *setelah* permintaan diautentikasi dan diotorisasi, tetapi *sebelum* objek disimpan di etcd.
*   **Jenis:**
    *   `ValidatingAdmissionWebhook`: Dapat **menolak** permintaan jika tidak sesuai kebijakan, tetapi tidak dapat mengubah objek.
    *   `MutatingAdmissionWebhook`: Dapat **memodifikasi** objek permintaan sebelum disimpan (misalnya, menambahkan label default, menyuntikkan sidecar, mengatur security context default).
*   **Cara Kerja:** API Server dikonfigurasi untuk mengirim permintaan pembuatan/pembaruan objek tertentu (AdmissionReview request) ke layanan webhook (yang dijalankan oleh policy engine). Webhook mengevaluasi permintaan terhadap kebijakan yang dikonfigurasi dan mengirimkan respons kembali ke API Server (izinkan, tolak, atau izinkan dengan modifikasi).

## 1. OPA (Open Policy Agent) Gatekeeper

*   **Deskripsi:** Implementasi Kubernetes native dari **Open Policy Agent (OPA)**, sebuah policy engine open-source serbaguna (proyek kelulusan CNCF). Gatekeeper memungkinkan Anda menegakkan kebijakan kustom pada objek Kubernetes menggunakan bahasa deklaratif OPA yang disebut **Rego**.
*   **Komponen Utama:**
    *   **Gatekeeper Manager (Controller):** Mengelola CRD dan konfigurasi.
    *   **Audit Controller:** Secara berkala memeriksa kepatuhan objek yang *sudah ada* di cluster terhadap kebijakan.
    *   **Admission Webhook:** Pod yang menerima AdmissionReview requests dari API Server dan mengevaluasinya menggunakan OPA/Rego.
*   **Cara Mendefinisikan Kebijakan:**
    1.  **`ConstraintTemplate` (CRD Cluster-scoped):** Mendefinisikan *skema* sebuah kebijakan dan logika Rego untuk menegakkannya. Ini adalah template yang dapat digunakan kembali. Template menentukan parameter apa yang dapat diterima oleh kebijakan.
        ```rego
        # Contoh sederhana di dalam ConstraintTemplate (logika Rego)
        violation[{"msg": msg}] {
          input.review.object.metadata.labels["owner"] == "" # Tolak jika label 'owner' kosong
          msg := "Label 'owner' is required"
        }
        ```
    2.  **`Constraint` (CRD, bisa Namespaced atau Cluster-scoped):** Membuat *instance* dari `ConstraintTemplate` dan menerapkannya pada scope tertentu (misalnya, semua Pods di namespace 'prod') dengan parameter spesifik.
        ```yaml
        # Contoh Constraint berdasarkan Template di atas
        apiVersion: constraints.gatekeeper.sh/v1beta1
        kind: K8sRequiredLabels # Nama Kind dari ConstraintTemplate
        metadata:
          name: pod-must-have-owner-label
        spec:
          match: # Menentukan objek mana yang ditargetkan kebijakan
            kinds:
              - apiGroups: [""]
                kinds: ["Pod"]
          # Tidak perlu parameter untuk contoh ini
          # parameters:
          #   key: value
        ```
*   **Kelebihan:** Sangat kuat dan fleksibel karena menggunakan Rego, bagian dari ekosistem OPA yang lebih luas (bisa digunakan di luar K8s), didukung oleh komunitas besar.
*   **Kekurangan:** Bahasa Rego memiliki kurva belajar, debugging kebijakan bisa jadi menantang.
*   **Situs Web:** [open-policy-agent.github.io/gatekeeper/](https://open-policy-agent.github.io/gatekeeper/)

## 2. Kyverno

*   **Deskripsi:** Policy engine open-source yang dirancang **khusus untuk Kubernetes** (proyek kelulusan CNCF). Kebijakan Kyverno ditulis **langsung sebagai resource Kubernetes (CRD)**, membuatnya terasa lebih native dan seringkali lebih mudah dipelajari bagi pengguna Kubernetes.
*   **Komponen Utama:** Berjalan sebagai Deployment di dalam cluster yang mengimplementasikan admission webhook dan controller untuk mengelola kebijakannya.
*   **Cara Mendefinisikan Kebijakan:**
    *   Kebijakan didefinisikan menggunakan CRD `Policy` atau `ClusterPolicy`.
    *   Setiap kebijakan berisi satu atau lebih `rules`.
    *   Setiap `rule` memiliki:
        *   `match`: Memilih sumber daya target (berdasarkan kind, name, namespace, labels, annotations).
        *   `exclude` (Opsional): Mengecualikan sumber daya tertentu dari target.
        *   Satu atau lebih *jenis tindakan* kebijakan:
            *   **`validate`:** Menolak permintaan jika tidak memenuhi kondisi yang ditentukan (misalnya, memeriksa keberadaan label, format nama, pengaturan security context). Bisa menggunakan *overlay patterns* atau kondisi `anyPattern`/`allPattern`.
            *   **`mutate`:** Memodifikasi objek yang masuk sebelum disimpan (misalnya, menambahkan label, anotasi, atau mengatur nilai default). Menggunakan *overlay patterns* atau *patchesStrategicMerge/patchesJson6902*.
            *   **`generate`:** Membuat sumber daya Kubernetes lain secara otomatis ketika sumber daya target dibuat (misalnya, membuat NetworkPolicy default saat Namespace baru dibuat).
            *   **`verifyImages`:** Memverifikasi tanda tangan (signature) image kontainer menggunakan Cosign.
*   **Kelebihan:** Kebijakan ditulis sebagai YAML Kubernetes (lebih mudah dipelajari daripada Rego), mendukung validasi, mutasi, dan generasi resource dalam satu alat, fitur verifikasi image.
*   **Kekurangan:** Lebih baru dibandingkan OPA/Gatekeeper (meskipun sudah matang), ekosistem mungkin belum sebesar OPA.
*   **Situs Web:** [kyverno.io](https://kyverno.io/)

**Contoh Kebijakan Kyverno (Validasi Label):**

```yaml
apiVersion: kyverno.io/v1
kind: ClusterPolicy # Berlaku cluster-wide
metadata:
  name: require-labels
spec:
  validationFailureAction: Enforce # Tolak jika validasi gagal ('Audit' juga tersedia)
  background: true # Periksa resource yang sudah ada juga
  rules:
    - name: check-for-team-label
      match: # Targetkan resource ini
        any:
        - resources:
            kinds:
              - Pod
              - Deployment
              - StatefulSet
              - Service
      validate: # Aksi validasi
        message: "Label 'team' is required." # Pesan error
        pattern: # Objek HARUS cocok dengan pola ini
          metadata:
            labels:
              team: "?*" # Label 'team' harus ada dengan nilai apa saja (?*)
```

## Gatekeeper vs Kyverno: Mana yang Dipilih?

*   **Pilih Gatekeeper jika:**
    *   Anda sudah familiar atau ingin berinvestasi belajar Rego.
    *   Anda membutuhkan fleksibilitas dan kekuatan penuh dari OPA.
    *   Anda menggunakan OPA untuk manajemen kebijakan di luar Kubernetes juga.
*   **Pilih Kyverno jika:**
    *   Anda lebih memilih menulis kebijakan menggunakan YAML gaya Kubernetes.
    *   Anda ingin alat tunggal untuk validasi, mutasi, dan generasi resource.
    *   Anda mencari kurva belajar yang mungkin lebih landai untuk pengguna Kubernetes.
    *   Anda tertarik dengan fitur verifikasi image bawaan.

Kedua alat ini sangat kuat dan merupakan tambahan berharga untuk toolkit keamanan dan tata kelola (governance) Kubernetes Anda. Mereka membantu mengotomatiskan penegakan standar dan praktik terbaik, mengurangi risiko konfigurasi yang salah, dan meningkatkan konsistensi di seluruh cluster Anda. Menggunakan salah satu dari ini (atau keduanya untuk kasus penggunaan berbeda) sangat direkomendasikan untuk lingkungan produksi.
