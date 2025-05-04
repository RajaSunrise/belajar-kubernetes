# Init Containers: Tugas Persiapan Sebelum Aplikasi Utama

Selain kontainer aplikasi utama (dan sidecars), sebuah Pod dapat memiliki satu atau lebih **Init Containers**. Init Containers adalah kontainer khusus yang:

1.  **Berjalan sebelum** kontainer aplikasi utama (`containers`) dimulai.
2.  **Berjalan secara sekuensial:** Jika ada beberapa Init Containers, mereka akan dijalankan satu per satu, sesuai urutan definisinya dalam manifest Pod. Init Container berikutnya *tidak akan* dimulai sampai Init Container sebelumnya **berhasil diselesaikan** (exit code 0).
3.  **Harus berjalan hingga selesai (run-to-completion):** Mereka harus keluar dengan sukses agar proses startup Pod dapat berlanjut ke kontainer aplikasi utama.

**Tujuan Utama Init Containers:**

Init Containers digunakan untuk melakukan **tugas persiapan atau setup** yang harus selesai *sebelum* kontainer aplikasi utama siap menerima traffic atau mulai bekerja. Mereka memisahkan logika startup satu kali dari logika runtime aplikasi utama.

**Kasus Penggunaan Umum:**

*   **Menunggu Layanan Dependen:** Menunggu layanan eksternal (seperti database, API lain, atau message queue) menjadi tersedia sebelum aplikasi utama dimulai. Init Container dapat melakukan loop `ping` atau `curl` hingga dependensi siap.
*   **Inisialisasi atau Setup:**
    *   Melakukan migrasi database atau setup skema awal.
    *   Mengunduh data konfigurasi atau aset yang diperlukan dari sumber eksternal.
    *   Membuat struktur direktori atau file yang diperlukan di volume bersama.
    *   Mengubah izin file pada volume bersama.
    *   Mendaftarkan Pod ini ke sistem penemuan layanan eksternal.
*   **Kloning Kode atau Data:** Mengkloning repositori Git ke dalam volume bersama agar aplikasi utama dapat menggunakannya.
*   **Setup Jaringan Khusus:** Mengkonfigurasi aturan `iptables` atau pengaturan jaringan lain sebelum aplikasi utama berjalan (meskipun seringkali ada cara yang lebih baik untuk ini).

## Perbedaan Utama dari Kontainer Aplikasi Biasa (`containers`)

| Fitur             | Init Containers (`initContainers`)                 | App Containers (`containers`)                      |
|-------------------|----------------------------------------------------|----------------------------------------------------|
| **Waktu Jalan**   | Sebelum App Containers dimulai                    | Setelah semua Init Containers sukses              |
| **Eksekusi**      | Berurutan (satu per satu)                          | Paralel (semua dimulai bersamaan)                 |
| **Tujuan**        | Harus selesai sukses (exit 0)                     | Diharapkan berjalan terus menerus (biasanya)       |
| **Probes**        | `livenessProbe`, `readinessProbe` **tidak** didukung | Didukung dan penting                             |
| **Lifecycle Hooks**| `postStart`, `preStop` **tidak** didukung          | Didukung                                           |
| **Resource Limits**| Dihitung terpisah dari App Containers*            | Dihitung bersama                                   |
| **Restart Policy**| Jika gagal, Pod akan di-restart berdasarkan `restartPolicy` Pod (`Never`, `OnFailure`) | Di-restart berdasarkan `restartPolicy` Pod        |

*Penjelasan Resource Limits: Resource (`requests` dan `limits`) untuk Init Container dihitung secara berbeda. Batas efektif untuk Pod adalah **nilai tertinggi** antara: (a) jumlah `limits` semua App Containers, atau (b) `limits` dari *setiap* Init Container individual. Permintaan efektif adalah nilai tertinggi antara: (a) jumlah `requests` semua App Containers, atau (b) `requests` dari *setiap* Init Container individual. Ini karena Init Containers berjalan secara sekuensial.

## Contoh YAML dengan Init Container

Contoh ini menunjukkan Pod dengan dua Init Containers: satu menunggu service `mydb` siap, dan satu lagi menunggu service `myservice` siap, sebelum kontainer aplikasi utama `myapp-container` dimulai.

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: myapp-pod
  labels:
    app: myapp
spec:
  # Kontainer aplikasi utama
  containers:
  - name: myapp-container
    image: busybox:1.28
    command: ['sh', '-c', 'echo The app is running! && sleep 3600']
    resources:
      requests:
        memory: "64Mi"
        cpu: "50m"
      limits:
        memory: "128Mi"
        cpu: "100m"

  # Init Containers berjalan sebelum 'myapp-container'
  initContainers:
  - name: init-mydb # Init Container pertama
    image: busybox:1.28
    # Loop hingga bisa resolve DNS dan connect ke port service 'mydb'
    command: ['sh', '-c', "until nslookup mydb.$(cat /var/run/secrets/kubernetes.io/serviceaccount/namespace).svc.cluster.local && nc -vz mydb.$(cat /var/run/secrets/kubernetes.io/serviceaccount/namespace).svc.cluster.local 5432; do echo waiting for mydb; sleep 2; done"]
    resources: # Init containers juga bisa punya resource requests/limits
      requests:
        memory: "32Mi"
        cpu: "25m"
      limits:
        memory: "64Mi"
        cpu: "50m"
  - name: init-myservice # Init Container kedua (berjalan SETELAH init-mydb sukses)
    image: busybox:1.28
    # Loop hingga bisa resolve DNS service 'myservice'
    command: ['sh', '-c', "until nslookup myservice.$(cat /var/run/secrets/kubernetes.io/serviceaccount/namespace).svc.cluster.local; do echo waiting for myservice; sleep 2; done"]
    resources:
      requests:
        memory: "32Mi"
        cpu: "25m"
      limits:
        memory: "64Mi"
        cpu: "50m"

  restartPolicy: OnFailure # Jika Init Container gagal, coba restart Pod
```

## Bagaimana Jika Init Container Gagal?

*   Jika sebuah Init Container gagal (keluar dengan exit code non-zero):
    *   Kubelet akan mencoba me-restart Init Container tersebut berdasarkan `restartPolicy` Pod.
    *   Jika `restartPolicy` adalah `OnFailure` atau `Always`, Kubelet akan mencoba lagi (mungkin dengan backoff delay).
    *   Jika `restartPolicy` adalah `Never`, Pod akan langsung masuk ke fase `Failed` dan tidak akan pernah memulai kontainer aplikasi utama.
*   Pod tidak akan pernah masuk ke status `Ready` sampai *semua* Init Containers berhasil diselesaikan.
*   Anda dapat melihat status Init Containers menggunakan `kubectl describe pod <pod-name>`. Status mereka akan muncul di bagian `initContainerStatuses`. Jika ada yang gagal berulang kali, status Pod mungkin menunjukkan `Init:CrashLoopBackOff` atau `Init:Error`.

Init Containers adalah alat yang berguna untuk memisahkan logika inisialisasi yang kompleks atau bergantung pada kondisi eksternal dari kontainer aplikasi utama Anda, membuat startup Pod lebih andal dan terstruktur.
