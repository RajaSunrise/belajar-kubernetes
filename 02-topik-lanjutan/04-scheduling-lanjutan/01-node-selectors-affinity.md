# Node Selectors & Node Affinity: Menarik Pod ke Node Tertentu

Secara default, Kubernetes Scheduler mencoba menempatkan Pods ke Node yang valid (memenuhi permintaan resource Pod, tidak memiliki Taint yang tidak ditoleransi Pod) dengan tujuan menyebarkan beban kerja secara merata (bin packing). Namun, seringkali kita memiliki kebutuhan untuk **mempengaruhi** keputusan penjadwalan ini dan **mengarahkan** Pods agar berjalan di **Node spesifik** atau **kelompok Node tertentu**.

Beberapa alasan umum:

*   **Hardware Khusus:** Pod memerlukan akses ke hardware spesifik yang hanya tersedia di beberapa Node (misalnya, GPU, SSD cepat).
*   **Lisensi Perangkat Lunak:** Lisensi software mungkin terikat pada Node tertentu.
*   **Lokasi Data:** Pod perlu berjalan dekat dengan data (misalnya, di zona ketersediaan yang sama dengan volume penyimpanan).
*   **Pemisahan Beban Kerja:** Menjalankan beban kerja development/staging terpisah dari produksi di Node yang berbeda.
*   **Kepatuhan (Compliance):** Persyaratan untuk menjalankan beban kerja tertentu di Node yang memenuhi standar keamanan atau lokasi geografis tertentu.

Kubernetes menyediakan dua mekanisme utama untuk "menarik" Pod ke Node tertentu: **Node Selectors** dan **Node Affinity**.

## 1. Node Selectors (`spec.nodeSelector`)

*   **Konsep:** Cara **paling sederhana** untuk membatasi Pod agar hanya berjalan di Node yang memiliki **label spesifik** yang cocok.
*   **Cara Kerja:**
    1.  **Label Node:** Anda (atau sistem otomatisasi/cloud provider) menambahkan label kustom ke objek Node Kubernetes.
        ```bash
        # Contoh menambahkan label ke node 'worker-01'
        kubectl label node worker-01 disktype=ssd
        kubectl label node worker-02 hardware=gpu vendor=nvidia
        ```
    2.  **Definisi Pod:** Anda menambahkan field `spec.nodeSelector` ke definisi Pod Anda, yang berisi map `key: value` dari label yang *harus* dimiliki oleh Node target.
        ```yaml
        apiVersion: v1
        kind: Pod
        metadata:
          name: my-app-needs-ssd
        spec:
          nodeSelector:
            disktype: ssd # Hanya berjalan di Node dengan label disktype=ssd
            # Anda bisa menambahkan lebih banyak label (implisit AND)
            # topology.kubernetes.io/zone: us-east-1a
          containers:
          - name: main-app
            image: my-app:1.0
            # ...
        ```
    3.  **Penjadwalan:** Scheduler hanya akan mempertimbangkan Node yang memiliki **semua** label yang tercantum dalam `nodeSelector` Pod tersebut. Jika tidak ada Node yang cocok, Pod akan tetap dalam status `Pending`.
*   **Kelebihan:** Sangat sederhana dan mudah dipahami.
*   **Kekurangan:** Kurang ekspresif. Hanya mendukung pencocokan label `key=value` secara eksak (logika AND). Tidak ada cara untuk mengekspresikan preferensi ("lebih suka Node X, tapi Node Y juga boleh") atau kondisi yang lebih kompleks (misalnya, "Node dengan label X atau Y", "Node yang tidak memiliki label Z").

## 2. Node Affinity (`spec.affinity.nodeAffinity`)

*   **Konsep:** Mekanisme yang **jauh lebih ekspresif dan fleksibel** daripada `nodeSelector` untuk menentukan batasan penjadwalan berdasarkan label Node.
*   **Fitur Utama:**
    *   **Ekspresi Lebih Kaya:** Mendukung operator seperti `In`, `NotIn`, `Exists`, `DoesNotExist`, `Gt` (Greater Than), `Lt` (Less Than) untuk mencocokkan label Node.
    *   **Aturan Wajib vs. Preferensi:** Memungkinkan Anda menentukan dua jenis aturan:
        *   **`requiredDuringSchedulingIgnoredDuringExecution`**: Aturan **HARUS** dipenuhi agar Pod dapat dijadwalkan ke Node. Jika tidak ada Node yang cocok, Pod tidak akan dijadwalkan (`Pending`). *("IgnoredDuringExecution"* berarti jika label Node berubah *setelah* Pod dijadwalkan, Pod tidak akan digusur).
        *   **`preferredDuringSchedulingIgnoredDuringExecution`**: Scheduler akan **MENCOBA** menemukan Node yang memenuhi aturan ini, tetapi jika tidak ada, Pod *masih bisa* dijadwalkan ke Node lain yang valid (yang memenuhi aturan `required...` jika ada). Aturan ini diberi bobot (`weight` antara 1-100) untuk menunjukkan tingkat preferensi.
    *   **Logika OR dan AND:** Anda dapat menggabungkan beberapa ekspresi dalam satu aturan (logika AND) dan mendefinisikan beberapa aturan preferensi (Scheduler akan mencoba memenuhi sebanyak mungkin berdasarkan bobot).

*   **Struktur YAML:**

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: my-app-with-affinity
spec:
  affinity:
    nodeAffinity:
      # --- Aturan WAJIB ---
      requiredDuringSchedulingIgnoredDuringExecution:
        nodeSelectorTerms: # Daftar term (logika OR antar term)
        - matchExpressions: # Daftar ekspresi dalam satu term (logika AND)
          - key: topology.kubernetes.io/zone
            operator: In # Operator: In, NotIn, Exists, DoesNotExist
            values: # Nilai untuk operator In/NotIn
            - antarctica-east1
            - antarctica-west1
          - key: hardware
            operator: Exists # Node harus punya label 'hardware'
      # --- Aturan PREFERENSI ---
      preferredDuringSchedulingIgnoredDuringExecution:
      - weight: 80 # Bobot preferensi (1-100, lebih tinggi lebih disukai)
        preference:
          matchExpressions:
          - key: disktype
            operator: In
            values:
            - ssd
      - weight: 30
        preference:
          matchExpressions:
          - key: cpu-arch
            operator: NotIn
            values:
            - arm64
  containers:
  - name: main-app
    image: my-app:2.0
    # ...
```

*   **Penjelasan Contoh:**
    *   **Wajib:** Pod ini *harus* dijadwalkan di Node yang berada di zona `antarctica-east1` ATAU `antarctica-west1` **DAN** memiliki label `hardware` (nilai apa saja).
    *   **Preferensi:** Scheduler akan *lebih memilih* (dengan bobot 80) Node yang juga memiliki label `disktype=ssd`. Scheduler juga akan *agak memilih* (dengan bobot 30) Node yang arsitektur CPU-nya *bukan* `arm64`. Jika ada Node SSD di zona Antartika, kemungkinan besar Pod akan ditempatkan di sana. Jika tidak ada, Scheduler mungkin memilih Node non-SSD di Antartika yang bukan ARM64, atau jika itu pun tidak ada, ia akan memilih Node mana saja di Antartika (selama label `hardware` ada).

*   **Kelebihan:** Sangat fleksibel, memungkinkan aturan penjadwalan yang kompleks, mendukung preferensi.
*   **Kekurangan:** Sintaks YAML sedikit lebih rumit daripada `nodeSelector`.

## Kapan Menggunakan Mana?

*   Gunakan **`nodeSelector`** jika kebutuhan Anda sederhana: Pod *harus* berjalan di Node dengan satu atau beberapa label `key=value` yang pasti.
*   Gunakan **`nodeAffinity`** jika Anda membutuhkan:
    *   Logika yang lebih kompleks (OR, NotIn, Exists, Gt, Lt).
    *   Preferensi penjadwalan (ingin Pod berjalan di Node tertentu jika memungkinkan, tapi tidak wajib).
    *   Kombinasi aturan wajib dan preferensi.

**Penting:** `nodeSelector` dan `nodeAffinity` **tidak dapat digunakan bersamaan** dalam satu definisi Pod. Node Affinity adalah pengganti yang lebih kuat untuk Node Selector. Jika Anda mendefinisikan keduanya, `nodeSelector` akan diabaikan.

Node Affinity (dan Node Selector) adalah alat penting untuk memastikan Pod Anda berjalan di lingkungan Node yang tepat sesuai dengan kebutuhan aplikasi, data, atau persyaratan infrastruktur.
