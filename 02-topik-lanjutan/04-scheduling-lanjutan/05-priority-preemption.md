# Prioritas Pod (Priority) dan Penggusuran (Preemption)

Dalam cluster Kubernetes yang digunakan bersama (multi-tenant) atau yang menjalankan beban kerja dengan tingkat kepentingan yang berbeda, terkadang Pod yang lebih penting (misalnya, komponen sistem inti, aplikasi produksi kritis) perlu "didahulukan" daripada Pod yang kurang penting (misalnya, tugas batch, Pod development).

**Masalah:** Jika cluster kekurangan sumber daya (CPU, Memori), Pod baru yang penting mungkin tidak dapat dijadwalkan (status `Pending`) karena semua sumber daya sudah digunakan oleh Pod yang kurang penting.

**Solusi:** Kubernetes menyediakan mekanisme **Prioritas Pod (Pod Priority)** dan **Penggusuran (Preemption)**.

*   **Prioritas Pod:** Memungkinkan Anda menetapkan tingkat prioritas numerik pada Pods. Pod dengan prioritas lebih tinggi dianggap lebih penting.
*   **Penggusuran (Preemption):** Jika Pod dengan prioritas tinggi tidak dapat dijadwalkan karena kekurangan sumber daya, Scheduler dapat memutuskan untuk **menggusur (evict)** satu atau lebih Pod dengan **prioritas lebih rendah** yang sedang berjalan di suatu Node untuk membuat ruang bagi Pod berprioritas tinggi tersebut.

## Objek `PriorityClass`

Prioritas Pod tidak ditetapkan langsung pada Pod itu sendiri. Sebaliknya, administrator cluster membuat objek **`PriorityClass`** (cluster-scoped).

*   **`kind: PriorityClass`**: Objek API Kubernetes.
*   **`metadata.name`**: Nama PriorityClass yang akan dirujuk oleh Pods.
*   **`value` (Wajib):** Angka integer 32-bit. **Semakin tinggi nilainya, semakin tinggi prioritasnya.** Nilai di atas 1 Miliar (1,000,000,000) dicadangkan untuk Pods sistem kritis.
*   **`globalDefault` (Opsional):** Boolean. Jika `true`, PriorityClass ini akan menjadi prioritas default untuk Pods yang **tidak** menentukan `priorityClassName` secara eksplisit. Hanya **satu** PriorityClass di cluster yang boleh memiliki `globalDefault: true`.
*   **`description` (Opsional):** String deskripsi untuk tujuan PriorityClass.
*   **`preemptionPolicy` (Opsional):** Mengontrol apakah Pod dengan prioritas ini dapat menggusur Pod lain.
    *   `PreemptLowerPriority` (Default): Pod ini dapat menggusur Pod dengan prioritas lebih rendah.
    *   `Never`: Pod ini tidak akan pernah menggusur Pod lain, meskipun prioritasnya tinggi. Ia akan tetap `Pending` jika tidak ada resource yang cukup tanpa penggusuran.

**Contoh YAML PriorityClass:**

```yaml
apiVersion: scheduling.k8s.io/v1
kind: PriorityClass
metadata:
  name: high-priority-apps # Nama kelas prioritas
value: 1000000 # Nilai prioritas (tinggi tapi di bawah sistem)
globalDefault: false
description: "Priority class for critical user-facing applications."
preemptionPolicy: PreemptLowerPriority # Bisa menggusur yg lebih rendah
---
apiVersion: scheduling.k8s.io/v1
kind: PriorityClass
metadata:
  name: default-low-priority
value: 100000 # Nilai prioritas rendah
globalDefault: true # Jadi default jika Pod tidak menentukan priorityClassName
description: "Default low priority for general workloads and batch jobs."
preemptionPolicy: Never # Tidak bisa menggusur Pod lain
```

## Menggunakan Prioritas pada Pod

Untuk menetapkan prioritas pada Pod, Anda menambahkan field `spec.priorityClassName` ke definisi Pod, merujuk pada nama `PriorityClass` yang sudah dibuat:

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: critical-app-pod
spec:
  priorityClassName: high-priority-apps # Menggunakan PriorityClass 'high-priority-apps'
  containers:
  - name: main-app
    image: critical-app:latest
    # ... requests/limits ...
```

Pods yang tidak menentukan `priorityClassName` akan menggunakan `PriorityClass` yang ditandai `globalDefault: true` (jika ada), atau akan memiliki prioritas 0 jika tidak ada default global.

## Proses Penjadwalan dengan Prioritas & Penggusuran

1.  **Antrian Penjadwalan:** Pods yang menunggu untuk dijadwalkan (`Pending`) ditempatkan dalam antrian penjadwalan internal, diurutkan berdasarkan nilai prioritasnya (tertinggi didahulukan).
2.  **Percobaan Penjadwalan:** Scheduler mengambil Pod dengan prioritas tertinggi dari antrian dan mencoba menemukan Node yang cocok (memenuhi requests, affinity, tolerations, dll.).
3.  **Penjadwalan Berhasil:** Jika Node yang cocok ditemukan dengan sumber daya yang cukup, Pod dijadwalkan ke Node tersebut.
4.  **Penjadwalan Gagal (Sumber Daya Tidak Cukup):** Jika tidak ada Node yang cocok dengan sumber daya yang cukup, Scheduler memeriksa `preemptionPolicy` dari Pod berprioritas tinggi tersebut.
5.  **Logika Penggusuran (jika `preemptionPolicy: PreemptLowerPriority`):**
    *   Scheduler mencari Node di mana penggusuran satu atau lebih Pod dengan **prioritas lebih rendah** akan membebaskan cukup sumber daya untuk Pod berprioritas tinggi.
    *   Scheduler mempertimbangkan berbagai faktor, termasuk jumlah Pod yang perlu digusur dan potensi gangguan (misalnya, Pod Disruption Budgets - PDB).
    *   Jika Node yang cocok untuk penggusuran ditemukan:
        *   Pods korban (yang prioritasnya lebih rendah) akan menerima sinyal terminasi (proses graceful shutdown dimulai).
        *   Setelah Pods korban benar-benar berhenti dan sumber daya dibebaskan, Pod berprioritas tinggi akan dijadwalkan ke Node tersebut.
    *   Jika tidak ada skenario penggusuran yang valid ditemukan (misalnya, semua Pod yang berjalan memiliki prioritas sama atau lebih tinggi, atau PDB mencegah penggusuran), Pod berprioritas tinggi akan tetap `Pending` dan menunggu sumber daya tersedia secara alami.

## Pertimbangan Penting

*   **Prioritas vs. QoS:** Prioritas Pod berbeda dengan Quality of Service (QoS) Class (Guaranteed, Burstable, BestEffort) yang ditentukan oleh `requests` dan `limits`. QoS mempengaruhi *bagaimana* Pod ditangani saat Node mengalami tekanan resource (siapa yang di-OOMKill duluan), sedangkan Prioritas mempengaruhi *urutan penjadwalan* dan *kemampuan menggusur*.
*   **Risiko Penggusuran Berantai:** Penggusuran dapat memicu penggusuran lain jika Pod yang digusur juga memiliki prioritas tinggi dan perlu dijadwalkan ulang.
*   **Pod Disruption Budgets (PDB):** PDB dapat membatasi jumlah Pod dari suatu aplikasi yang boleh tidak tersedia pada satu waktu. Scheduler akan menghormati PDB saat mempertimbangkan penggusuran. Jika penggusuran akan melanggar PDB dari Pod korban, penggusuran tersebut tidak akan terjadi.
*   **Gunakan dengan Hati-hati:** Penggusuran adalah tindakan disruptif. Gunakan prioritas tinggi dan penggusuran hanya untuk beban kerja yang benar-benar kritis. Konfigurasi `globalDefault` dan `preemptionPolicy` dengan cermat.
*   **Pods Sistem:** Pods sistem kritis (di `kube-system`) biasanya secara otomatis diberi `PriorityClass` dengan nilai sangat tinggi (di atas 1 Miliar) untuk memastikan mereka selalu dapat berjalan dan dapat menggusur beban kerja pengguna jika perlu.

Prioritas dan Penggusuran adalah mekanisme penting untuk memastikan ketersediaan beban kerja kritis dalam cluster yang padat atau memiliki sumber daya terbatas, tetapi perlu dikonfigurasi dan dipahami dengan baik untuk menghindari perilaku yang tidak diinginkan.
