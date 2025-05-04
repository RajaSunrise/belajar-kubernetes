# Topology Spread Constraints: Menyebarkan Pods Secara Merata

Pod Anti-Affinity bagus untuk memastikan Pods *tidak* berada di domain topologi yang sama (misalnya, tidak di Node yang sama). Namun, terkadang kita menginginkan kontrol yang lebih halus: kita ingin **menyebarkan Pods semerata mungkin** di seluruh domain topologi yang tersedia (Nodes, Zones, Regions) untuk meningkatkan ketersediaan dan pemanfaatan sumber daya, sambil tetap mengizinkan beberapa Pod berada di domain yang sama jika perlu.

Di sinilah **Topology Spread Constraints** (`spec.topologySpreadConstraints`) masuk. Fitur ini memberikan kontrol yang lebih baik kepada Scheduler untuk mencapai penyebaran Pod yang merata.

## Mengapa Perlu Selain Anti-Affinity?

Bayangkan Anda memiliki 3 Node dan ingin menjalankan 6 replika Pod.
*   Jika Anda menggunakan `podAntiAffinity` yang `required...` dengan `topologyKey=kubernetes.io/hostname`, hanya 3 Pod pertama yang akan dijadwalkan (satu per Node). 3 Pod berikutnya akan `Pending` karena tidak ada Node baru yang tersedia tanpa melanggar aturan anti-affinity.
*   Jika Anda menggunakan `podAntiAffinity` yang `preferred...`, Scheduler akan mencoba menyebar, tetapi perilakunya mungkin tidak selalu optimal atau dapat diprediksi, terutama jika ada preferensi atau batasan lain.

Topology Spread Constraints memungkinkan Anda mengatakan: "Saya ingin Pods dengan label `app=my-app` tersebar semerata mungkin di seluruh `kubernetes.io/hostname` (atau `topology.kubernetes.io/zone`), dan perbedaan jumlah Pod antar domain tidak boleh melebihi `X`."

## Konsep Utama Topology Spread Constraints

Setiap constraint didefinisikan dalam list `spec.topologySpreadConstraints` dan memiliki field utama:

1.  **`maxSkew` (Wajib):** Angka integer positif. Mendefinisikan **derajat ketidakseimbangan maksimum yang diizinkan** antar domain topologi. Perbedaan antara jumlah Pod yang cocok (sesuai `labelSelector`) di domain topologi mana pun dan jumlah Pod yang cocok secara global (dibagi jumlah domain) tidak boleh melebihi `maxSkew`.
    *   `maxSkew: 1` berarti penyebaran yang paling merata (perbedaan maksimal 1 Pod antar domain).
2.  **`topologyKey` (Wajib):** Sama seperti di affinity, ini adalah kunci label Node yang mendefinisikan domain topologi (misalnya, `kubernetes.io/hostname`, `topology.kubernetes.io/zone`).
3.  **`whenUnsatisfiable` (Wajib):** Menentukan apa yang harus dilakukan Scheduler jika constraint *tidak dapat dipenuhi* saat menjadwalkan Pod baru (misalnya, menambahkan Pod baru akan membuat `skew` melebihi `maxSkew`). Ada dua pilihan:
    *   **`DoNotSchedule` (Lebih Ketat):** Jika constraint tidak dapat dipenuhi, Pod **tidak akan dijadwalkan** dan akan tetap `Pending`. Mirip dengan aturan `required...` pada affinity.
    *   **`ScheduleAnyway` (Lebih Lunak):** Jika constraint tidak dapat dipenuhi, Scheduler **akan tetap menjadwalkan Pod**, tetapi ia akan menempatkannya di domain topologi yang akan **meminimalkan `skew`** (pelanggaran constraint). Mirip dengan aturan `preferred...` pada affinity.
4.  **`labelSelector` (Wajib):** Label selector untuk mengidentifikasi **kelompok Pods** yang ingin Anda sebarkan secara merata. Ini biasanya cocok dengan label Pod dari Deployment atau StatefulSet yang sama.
5.  `minDomains` (Opsional, Beta): Jumlah minimum domain yang memenuhi syarat yang harus ada agar constraint diterapkan.
6.  `nodeAffinityPolicy` / `nodeTaintsPolicy` (Opsional, Beta): Mengontrol apakah Node Affinity/Taints pada Pod ini harus dihormati saat menghitung penyebaran.

## Bagaimana Scheduler Menggunakannya?

Saat menjadwalkan Pod baru yang memiliki `topologySpreadConstraints`:

1.  Scheduler mengidentifikasi semua Node yang valid untuk Pod (memenuhi requests, affinity, tolerations, dll.).
2.  Scheduler mengelompokkan Node valid tersebut ke dalam domain topologi berdasarkan `topologyKey`.
3.  Scheduler menghitung jumlah Pod yang sudah ada (yang cocok dengan `labelSelector`) di setiap domain topologi.
4.  Scheduler menghitung `skew` saat ini dan `skew` yang akan terjadi jika Pod baru ditempatkan di setiap domain yang mungkin.
5.  Scheduler memilih Node di domain yang memenuhi constraint `maxSkew`.
6.  Jika beberapa domain memenuhi constraint, Scheduler akan memilih domain dengan jumlah Pod yang cocok paling sedikit.
7.  Jika tidak ada domain yang memenuhi constraint:
    *   Jika `whenUnsatisfiable: DoNotSchedule`, Pod akan `Pending`.
    *   Jika `whenUnsatisfiable: ScheduleAnyway`, Scheduler memilih domain yang menghasilkan `skew` terkecil.

## Contoh YAML

**Contoh 1: Sebaran Merata Antar Node (Maksimal Beda 1)**

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-uniform-app
spec:
  replicas: 5
  selector:
    matchLabels:
      app: my-uniform-app
  template:
    metadata:
      labels:
        app: my-uniform-app # Label untuk dicocokkan oleh constraint
    spec:
      topologySpreadConstraints:
      - maxSkew: 1 # Perbedaan jumlah Pod maks 1 antar Node
        topologyKey: kubernetes.io/hostname # Domain adalah Node
        whenUnsatisfiable: DoNotSchedule # Jangan jadwalkan jika skew > 1
        labelSelector:
          matchLabels:
            app: my-uniform-app # Sebarkan Pods dengan label ini
      containers:
      - name: app-container
        image: my-app:latest
```
*Jika ada 3 Node, K8s akan mencoba menempatkan Pods seperti ini: Node1=2 Pods, Node2=2 Pods, Node3=1 Pod. Jika replika ditambah jadi 6, akan jadi 2 Pods per Node. Jika Node baru ditambahkan, Scheduler akan mencoba memindahkan Pod (jika menggunakan descheduler) atau menempatkan Pod baru di sana untuk menyeimbangkan kembali.*

**Contoh 2: Sebaran Merata Antar Zona (Preferensi)**

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-zone-spread-app
spec:
  replicas: 6
  selector:
    matchLabels:
      app: my-zone-spread-app
  template:
    metadata:
      labels:
        app: my-zone-spread-app
    spec:
      topologySpreadConstraints:
      - maxSkew: 1
        topologyKey: topology.kubernetes.io/zone # Domain adalah Zona AZ
        whenUnsatisfiable: ScheduleAnyway # Tetap jadwalkan, minimalkan skew
        labelSelector:
          matchLabels:
            app: my-zone-spread-app
      # --- Tambahkan Anti-Affinity per Node untuk HA di dalam Zona ---
      affinity:
        podAntiAffinity:
          requiredDuringSchedulingIgnoredDuringExecution:
          - labelSelector:
              matchLabels:
                app: my-zone-spread-app
            topologyKey: kubernetes.io/hostname
      # -------------------------------------------------------------
      containers:
      - name: app-container
        image: my-app:latest
```
*Contoh ini mencoba menyebarkan 6 Pod semerata mungkin antar Zona (`maxSkew: 1`, `ScheduleAnyway`). Jika ada 3 Zona, idealnya 2 Pod per Zona. Ditambah lagi, aturan `podAntiAffinity` yang `required...` memastikan bahwa *di dalam* setiap Zona, Pods akan ditempatkan di Node yang berbeda.*

## Pertimbangan

*   **Overhead Scheduler:** Seperti affinity, constraints ini menambah pekerjaan bagi Scheduler.
*   **Ketersediaan Domain:** `DoNotSchedule` dapat menyebabkan Pod `Pending` jika tidak cukup domain topologi yang tersedia untuk memenuhi `maxSkew`.
*   **Interaksi dengan Affinity/Taints:** Perilaku bisa menjadi kompleks jika dikombinasikan dengan aturan affinity/toleration lainnya. Gunakan `nodeAffinityPolicy`/`nodeTaintsPolicy` (jika tersedia/diperlukan) untuk mengontrol interaksi ini.
*   **Label Selector:** Pastikan `labelSelector` secara akurat menargetkan kelompok Pods yang ingin Anda sebarkan.

Topology Spread Constraints adalah fitur penjadwalan lanjutan yang memberikan kontrol lebih baik untuk mencapai ketersediaan tinggi dan pemanfaatan sumber daya yang merata dengan menyebarkan Pods secara cerdas di seluruh domain topologi yang relevan.
