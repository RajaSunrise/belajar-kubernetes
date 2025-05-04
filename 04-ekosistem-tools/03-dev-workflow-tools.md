# Alat Workflow Pengembangan Kubernetes: Skaffold, Tilt, Telepresence

Mengembangkan aplikasi yang ditargetkan untuk berjalan di Kubernetes dapat menghadirkan tantangan unik pada *inner development loop* (siklus edit-kode -> bangun -> deploy -> uji). Proses manual membangun image Docker, mendorongnya ke registry, memperbarui manifest Kubernetes (misalnya, tag image), dan menerapkan perubahan bisa memakan waktu dan membosankan.

Beberapa alat open source populer bertujuan untuk menyederhanakan dan mempercepat alur kerja pengembangan ini:

## 1. Skaffold

*   **Deskripsi:** Proyek open source dari Google yang mengotomatiskan alur kerja build, push, dan deploy berulang untuk aplikasi Kubernetes. Anda mendefinisikan alur kerja Anda dalam satu file `skaffold.yaml`, dan Skaffold menangani sisanya.
*   **Fitur Utama:**
    *   **Deteksi Perubahan File:** Memantau perubahan pada kode sumber aplikasi Anda.
    *   **Build Otomatis:** Secara otomatis membangun image kontainer saat kode berubah. Mendukung berbagai builder (Docker, Buildpacks, Jib, Bazel, custom scripts).
    *   **Tagging Image Otomatis:** Memberi tag unik pada image yang dibangun (misalnya, berdasarkan Git commit atau checksum konten).
    *   **Push Otomatis (Opsional):** Mendorong image ke registry kontainer. Skaffold cerdas, seringkali dapat melewatkan push jika image tidak berubah atau jika cluster lokal dapat mengakses daemon Docker (misalnya, dengan Minikube/Kind).
    *   **Deploy Otomatis:** Menerapkan manifest Kubernetes (YAML biasa, Helm, Kustomize) ke cluster Anda, secara otomatis memperbarui tag image dalam manifest. Mendukung berbagai deployer.
    *   **Streaming Log:** Menggabungkan dan menampilkan log dari Pods yang di-deploy.
    *   **Port Forwarding Otomatis:** Dapat secara otomatis mengatur port forwarding ke layanan yang di-deploy.
    *   **File Sync (Untuk Pengembangan Cepat):** Untuk bahasa interpreted atau aset statis, Skaffold dapat menyinkronkan file yang diubah langsung ke dalam kontainer yang berjalan tanpa perlu membangun ulang image, mempercepat siklus iterasi secara drastis.
    *   **Profil:** Mendefinisikan konfigurasi berbeda untuk lingkungan yang berbeda (misalnya, dev lokal vs staging).
    *   **Debugging:** Integrasi dengan alat debugging untuk bahasa populer.
*   **Mode Operasi:**
    *   `skaffold dev`: Mode pengembangan interaktif. Memantau perubahan, membangun ulang, men-deploy ulang, stream log secara terus menerus.
    *   `skaffold run`: Menjalankan alur kerja build, push, deploy sekali, lalu keluar. Berguna untuk CI/CD.
    *   `skaffold build`: Hanya membangun dan memberi tag image.
    *   `skaffold deploy`: Hanya men-deploy manifest.
*   **Kelebihan:** Sangat fleksibel (banyak builder/deployer), otomatisasi penuh siklus build-push-deploy, fitur file sync bagus, didukung Google.
*   **Kekurangan:** Konfigurasi `skaffold.yaml` bisa menjadi kompleks untuk proyek besar, mungkin terasa sedikit "berat" untuk proyek sangat sederhana.
*   **Situs Web:** [skaffold.dev](https://skaffold.dev/)

**Contoh `skaffold.yaml` Sederhana:**

```yaml
apiVersion: skaffold/v4beta7 # Gunakan versi terbaru
kind: Config
metadata:
  name: my-k8s-app
build:
  # Mendefinisikan bagaimana image dibangun
  artifacts:
    - image: my-local/hello-k8s-app # Nama image yang akan dibangun
      context: . # Konteks build (direktori Dockerfile)
      docker:
        dockerfile: Dockerfile # Path ke Dockerfile
      # Opsi sinkronisasi file (jika didukung bahasa/setup Anda)
      sync:
        manual:
          - src: 'app/**/*.py' # File Python
            dest: .           # Salin ke root WORKDIR di kontainer
manifests:
  # Mendefinisikan bagaimana aplikasi di-deploy
  rawYaml:
    - deployment.yaml # Daftar file manifest YAML biasa
    - service.yaml
deploy:
  # Menggunakan kubectl untuk deploy
  kubectl: {}
portForward: # Otomatis port-forward
  - resourceType: service
    resourceName: hello-k8s-service
    namespace: lab01-stateless # Sesuaikan namespace
    port: 80       # Port pada service
    localPort: 8080 # Port lokal
```

## 2. Tilt

*   **Deskripsi:** Alat open source yang fokus pada pengalaman pengembangan **multi-service** lokal di Kubernetes. Tilt menyediakan UI web interaktif untuk memantau status build, deploy, dan log dari semua layanan Anda secara bersamaan.
*   **Fitur Utama:**
    *   **Tiltfile:** Konfigurasi didefinisikan dalam file `Tiltfile` menggunakan dialek Python yang disebut Starlark.
    *   **UI Web Interaktif:** Menampilkan status real-time semua resource (layanan), log, build, error, dll., dalam satu dashboard web.
    *   **Update Cerdas:** Seperti Skaffold, mendeteksi perubahan file. Dapat melakukan build ulang image penuh atau **live update** (menyuntikkan file yang diubah langsung ke kontainer yang berjalan tanpa restart, jika dikonfigurasi). Sangat cepat untuk bahasa interpreted.
    *   **Manajemen Multi-Service:** Dirancang khusus untuk menangani banyak layanan microservice yang saling terkait.
    *   **Resource Kustom:** Memungkinkan definisi "resource" kustom di Tiltfile untuk menjalankan tugas lokal atau mengelola proses lain.
    *   **Snapshots & Time Travel Debugging (Eksperimental):** Fitur untuk menyimpan dan memulihkan state aplikasi.
*   **Kelebihan:** UI Web sangat bagus untuk memantau banyak layanan, live update sangat cepat, konfigurasi Starlark fleksibel. Fokus kuat pada pengalaman developer (DX).
*   **Kekurangan:** Menggunakan Starlark (bukan YAML standar), mungkin sedikit lebih beropini daripada Skaffold. Fokus utama pada `dev` loop, kurang pada `run` sekali jalan untuk CI.
*   **Situs Web:** [tilt.dev](https://tilt.dev/)

**Contoh `Tiltfile` Sederhana:**

```python
# Tiltfile (Starlark/Python-like)

# Deploy manifest Kubernetes biasa
k8s_yaml(['deployment.yaml', 'service.yaml'])

# Definisikan layanan 'my-app' yang terkait dengan deployment dan image Docker
# Tilt akan memantau file, build, deploy, dan stream log untuk ini.
docker_build('my-local/hello-k8s-app', # Nama image
             '.',                      # Konteks build
             live_update=[              # Konfigurasi live update
                 # Sinkronkan file .py ke direktori /app di kontainer
                 sync('app/', '/app/'),
                 # Jalankan perintah ini di kontainer setelah sinkronisasi (jika perlu)
                 # run('pip install -r requirements.txt', trigger='requirements.txt'),
                 # Restart proses python jika file .py berubah
                 restart_container()
             ]
            )

k8s_resource('deployment/hello-k8s-deployment', # Nama deployment K8s
             port_forwards='8080:80')           # Atur port forward
```

## 3. Telepresence

*   **Deskripsi:** Alat open source dari Ambassador Labs (CNCF sandbox project) yang memungkinkan Anda **menjalankan service lokal** di mesin Anda (misalnya, dari IDE Anda) seolah-olah service tersebut **berjalan di dalam cluster Kubernetes**.
*   **Cara Kerja:** Telepresence men-deploy "Traffic Manager" di cluster dan menjalankan "Daemon" di mesin lokal Anda. Ia secara cerdas **mem-proxy koneksi jaringan** antara mesin lokal Anda dan cluster. Anda dapat:
    *   **Intercept:** Mengalihkan traffic yang seharusnya menuju ke Service/Pod di cluster ke proses yang berjalan di mesin lokal Anda. Ini memungkinkan Anda menguji perubahan kode secara instan tanpa perlu build/deploy.
    *   **Connect:** Memberikan akses dari proses lokal Anda ke sumber daya lain di cluster (Services, DNS internal K8s) seolah-olah proses lokal Anda berada di dalam cluster.
*   **Fitur Utama:**
    *   **Intercept Global/Personal:** Mengalihkan semua traffic atau hanya traffic Anda (menggunakan header HTTP khusus).
    *   Akses ke nama DNS Service K8s dari lokal.
    *   Akses ke ClusterIPs dari lokal.
    *   Mount volume remote (eksperimental).
*   **Kelebihan:** Siklus iterasi pengembangan *tercepat* karena Anda menjalankan kode langsung dari mesin lokal Anda. Bagus untuk debugging. Tidak perlu build/deploy untuk setiap perubahan kode.
*   **Kekurangan:** Memerlukan pemahaman yang baik tentang cara kerjanya. Bisa sedikit "ajaib". Mungkin tidak sepenuhnya mereplikasi lingkungan K8s (misalnya, variabel lingkungan, secret mounts). Lebih fokus pada *satu service* pada satu waktu daripada seluruh aplikasi multi-service seperti Tilt/Skaffold.
*   **Situs Web:** [telepresence.io](https://www.telepresence.io/)

**Contoh Penggunaan (Konseptual):**

```bash
# Hubungkan ke cluster
telepresence connect

# Intercept traffic ke deployment 'my-frontend' port 3000
# dan arahkan ke proses lokal yang berjalan di port 3000
telepresence intercept my-frontend --port 3000

# Sekarang jalankan service frontend Anda secara lokal di port 3000
# (mis: npm start)
# Semua request ke service 'my-frontend' di cluster akan diarahkan ke proses lokal Anda.

# Untuk berhenti intercept:
telepresence leave my-frontend

# Putuskan koneksi
telepresence quit
```

## Mana yang Dipilih?

*   **Skaffold:** Pilihan serba bisa yang bagus untuk otomatisasi build-push-deploy standar, fleksibel, dan mendukung banyak konfigurasi. Baik untuk `dev` dan `run` (CI).
*   **Tilt:** Pilihan bagus jika fokus utama Anda adalah pengalaman pengembangan *multi-service* lokal yang cepat dengan UI terintegrasi dan live updates.
*   **Telepresence:** Pilihan bagus jika Anda ingin siklus iterasi *tercepat* untuk *satu service* pada satu waktu dengan menjalankan kode langsung dari mesin lokal Anda, terutama untuk debugging.

Ketiga alat ini tidak saling eksklusif. Beberapa tim mungkin menggunakan Skaffold untuk CI/CD dan Tilt atau Telepresence untuk pengembangan lokal, tergantung pada kebutuhan spesifik mereka. Mencoba ketiganya pada proyek sederhana dapat membantu Anda merasakan perbedaannya.
