# Resource Requests dan Limits: Mengelola CPU & Memori Pod

Saat Anda menjalankan kontainer di Kubernetes, mereka menggunakan sumber daya komputasi dari Node tempat mereka berjalan, terutama **CPU** dan **Memori**. Sangat penting untuk memberi tahu Kubernetes tentang kebutuhan sumber daya aplikasi Anda dan menetapkan batasan penggunaannya. Ini dilakukan melalui **Requests** dan **Limits**.

Mengkonfigurasi Requests dan Limits dengan benar sangat krusial untuk:

*   **Penjadwalan (Scheduling) yang Efisien:** Scheduler menggunakan `requests` untuk menemukan Node yang memiliki kapasitas cukup untuk menjalankan Pod Anda.
*   **Stabilitas Cluster:** Mencegah satu Pod "rakus" menghabiskan semua resource Node dan menyebabkan Pod lain (atau bahkan komponen Node itu sendiri) terganggu atau gagal (misalnya, karena Out Of Memory - OOM).
*   **Prediktabilitas Kinerja:** Memberikan jaminan sumber daya minimum (`requests`) dan mencegah penggunaan berlebih yang tidak terduga (`limits`).
*   **Kualitas Layanan (Quality of Service - QoS):** Mempengaruhi bagaimana Kubernetes memprioritaskan Pod Anda saat terjadi perebutan resource atau tekanan pada Node.

## Unit Sumber Daya

*   **CPU:**
    *   Diukur dalam unit "CPU Kubernetes". 1 CPU setara dengan 1 core CPU fisik/virtual (tergantung platform cloud/hardware), atau 1 hyperthread.
    *   Dapat dinyatakan sebagai desimal (misalnya, `0.5` untuk setengah CPU) atau menggunakan satuan **milliCPU** atau **millicores** (misalnya, `500m` untuk setengah CPU, `100m` untuk sepersepuluh CPU). `1000m` = `1` CPU.
    *   CPU selalu dianggap sebagai resource yang *compressible* (dapat dimampatkan). Jika aplikasi mencoba menggunakan CPU lebih dari `limits`-nya, ia akan di-**throttled** (diperlambat), tetapi tidak akan dimatikan.
*   **Memori:**
    *   Diukur dalam **bytes**.
    *   Dapat dinyatakan sebagai angka integer (bytes) atau menggunakan akhiran satuan daya dua (binary SI): `Ki` (Kibibyte), `Mi` (Mebibyte), `Gi` (Gibibyte), `Ti`, `Pi`, `Ei`. Atau satuan daya sepuluh (decimal SI): `k` (kilobyte), `M` (Megabyte), `G` (Gigabyte), dll.
    *   **Penting:** Gunakan satuan daya dua (`Ki`, `Mi`, `Gi`) karena ini yang umum digunakan dalam sistem operasi untuk mengukur memori. `100Mi` lebih besar dari `100M`.
    *   Memori dianggap sebagai resource yang *incompressible* (tidak dapat dimampatkan). Jika sebuah kontainer mencoba menggunakan memori lebih dari `limits`-nya, proses di dalam kontainer tersebut kemungkinan besar akan **dimatikan (killed)** oleh kernel sistem operasi karena **Out Of Memory (OOMKilled)**.

## Requests vs. Limits

Untuk setiap kontainer dalam Pod, Anda dapat menentukan `requests` dan `limits` untuk CPU dan Memori di bawah bagian `resources`:

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: resource-demo
spec:
  containers:
  - name: myapp-container
    image: myapp:latest
    resources:
      # Requests: Sumber daya yang DIJAMIN untuk kontainer
      requests:
        memory: "128Mi" # Meminta 128 Mebibytes RAM
        cpu: "250m"     # Meminta 0.25 core CPU (250 millicores)
      # Limits: Batas MAKSIMUM sumber daya yang boleh digunakan
      limits:
        memory: "256Mi" # Dibatasi hingga 256 Mebibytes RAM
        cpu: "500m"     # Dibatasi hingga 0.5 core CPU (500 millicores)
```

*   **`resources.requests`:**
    *   **Apa Artinya:** Jumlah sumber daya **minimum** yang Anda harapkan dibutuhkan oleh kontainer Anda untuk berjalan dengan baik. Kubernetes akan **menjamin** alokasi resource ini untuk kontainer Anda.
    *   **Digunakan Untuk:**
        *   **Penjadwalan:** Scheduler **hanya** akan menempatkan Pod di Node yang memiliki kapasitas *tersedia* (kapasitas total node dikurangi total `requests` dari semua Pod yang sudah berjalan di sana) yang **lebih besar atau sama dengan** total `requests` Pod baru tersebut. Jika tidak ada Node yang memenuhi `requests`, Pod akan tetap `Pending`.
        *   Menentukan **Kualitas Layanan (QoS Class)** Pod.
    *   **Jika Tidak Ditentukan:** Defaultnya bisa 0 atau diatur oleh `LimitRange` di namespace tersebut. Tidak menentukan `requests` membuat penjadwalan kurang dapat diprediksi.

*   **`resources.limits`:**
    *   **Apa Artinya:** Jumlah sumber daya **maksimum** yang diizinkan untuk digunakan oleh kontainer.
    *   **Penegakan:**
        *   **Memori:** Jika kontainer mencoba menggunakan memori **melebihi** `limits.memory`, prosesnya akan dihentikan paksa (**OOMKilled**).
        *   **CPU:** Jika kontainer mencoba menggunakan CPU **melebihi** `limits.cpu` secara berkelanjutan, penggunaannya akan dibatasi (**throttled**) oleh kernel Linux (cgroups). Aplikasi akan melambat, tetapi tidak dimatikan.
    *   **Jika Tidak Ditentukan:** Kontainer secara teoritis dapat menggunakan semua resource yang tersedia di Node (berpotensi menyebabkan masalah bagi Pod lain). `LimitRange` dapat menetapkan batas default.

**Penting:** `limits` harus selalu **lebih besar atau sama dengan** `requests` untuk setiap jenis resource (CPU, Memori). Kubernetes akan menolak Pod jika `limits` lebih kecil dari `requests`.

## Kualitas Layanan (Quality of Service - QoS Classes)

Berdasarkan bagaimana `requests` dan `limits` diatur untuk *semua* kontainer dalam sebuah Pod, Kubernetes mengklasifikasikan Pod ke dalam salah satu dari tiga Kelas QoS. Kelas QoS ini memengaruhi bagaimana Scheduler memprioritaskan Pod dan, yang lebih penting, **Pod mana yang akan dimatikan terlebih dahulu** oleh Kubelet atau kernel jika Node kehabisan sumber daya (terutama memori).

1.  **`Guaranteed`:**
    *   **Kondisi:** *Setiap* kontainer dalam Pod harus memiliki `limits` yang ditentukan untuk CPU dan Memori, DAN `limits` tersebut harus **sama persis** dengan `requests` untuk *setiap* kontainer.
    *   **Implikasi:** Pod ini mendapatkan jaminan resource tertinggi. Paling kecil kemungkinannya untuk dimatikan saat Node kehabisan memori. Ideal untuk beban kerja kritis.

2.  **`Burstable`:**
    *   **Kondisi:** Setidaknya satu kontainer dalam Pod memiliki `requests` CPU atau Memori yang ditentukan, TETAPI tidak semua kontainer memenuhi kriteria `Guaranteed` (misalnya, `limits` > `requests`, atau beberapa kontainer tidak memiliki `limits`, atau hanya `requests` yang ditentukan).
    *   **Implikasi:** Pod mendapatkan jaminan resource sesuai `requests`-nya, tetapi dapat "meledak" (burst) menggunakan resource lebih banyak hingga `limits`-nya jika tersedia di Node. Pod ini lebih mungkin dimatikan daripada `Guaranteed` saat terjadi kekurangan memori, tetapi lebih aman daripada `BestEffort`. Kasus paling umum.

3.  **`BestEffort`:**
    *   **Kondisi:** *Tidak ada* kontainer dalam Pod yang memiliki `requests` atau `limits` CPU atau Memori yang ditentukan.
    *   **Implikasi:** Pod ini tidak memiliki jaminan resource sama sekali. Mereka akan dijadwalkan di mana saja ada ruang. Mereka adalah **kandidat pertama** untuk dimatikan jika Node kehabisan resource. Hanya cocok untuk beban kerja yang tidak penting atau toleran terhadap gangguan.

**Bagaimana Memeriksa QoS Class Pod:**
```bash
kubectl get pod <pod-name> -o yaml | grep qosClass
# atau
kubectl describe pod <pod-name> | grep QoS
```

## Praktik Terbaik

*   **Selalu Tentukan `requests`:** Ini sangat penting untuk penjadwalan yang andal dan prediktabilitas. Tentukan `requests` serendah mungkin yang masih memungkinkan aplikasi Anda berjalan normal.
*   **Selalu Tentukan `limits`:** Ini sangat penting untuk stabilitas Node. Mencegah aplikasi "liar" menghabiskan semua resource dan mengganggu tetangganya.
*   **Mulai dari `limits` = 2x `requests` (Aturan Praktis Awal):** Ini sering menjadi titik awal yang baik untuk QoS `Burstable`. Pantau penggunaan aktual dan sesuaikan.
*   **Profil Aplikasi Anda:** Cara terbaik menentukan `requests` dan `limits` yang tepat adalah dengan memprofil penggunaan resource aplikasi Anda di bawah beban kerja yang realistis menggunakan alat monitoring (seperti Prometheus/Grafana).
*   **Hindari `BestEffort` untuk Beban Kerja Penting:** Gunakan setidaknya `Burstable` (dengan `requests` yang ditentukan) untuk aplikasi penting.
*   **Gunakan `Guaranteed` untuk Beban Kerja Paling Kritis:** Jika stabilitas absolut adalah prioritas utama dan Anda tahu persis kebutuhan resource-nya.
*   **Gunakan `LimitRange`:** Administrator dapat menggunakan objek `LimitRange` di Namespace untuk menetapkan nilai `requests` dan `limits` default atau membatasi nilai min/maks yang dapat diminta pengguna, memastikan standar minimum diterapkan.

Mengelola resource dengan `requests` dan `limits` adalah aspek fundamental dari operasi Kubernetes yang stabil dan efisien. Mengabaikannya dapat menyebabkan penjadwalan yang tidak efisien, ketidakstabilan Node, dan kinerja aplikasi yang tidak dapat diprediksi.
