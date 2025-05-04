# Limit Ranges: Menetapkan Batas Sumber Daya Default/Min/Max per Namespace

Kita sudah membahas pentingnya menentukan `requests` dan `limits` sumber daya (CPU, Memori) pada Pods dan Kontainer. Ini krusial untuk:

*   **Penjadwalan (Scheduling):** Scheduler menggunakan `requests` untuk menemukan Node yang cocok.
*   **Quality of Service (QoS):** Kubernetes menggunakan `requests` dan `limits` untuk menentukan kelas QoS Pod (Guaranteed, Burstable, BestEffort), yang mempengaruhi bagaimana Pod ditangani saat terjadi tekanan resource (misalnya, siapa yang di-OOMKill duluan).
*   **Resource Quotas:** Agar ResourceQuota komputasi berfungsi, Pods harus memiliki `requests`/`limits`.

Namun, apa yang terjadi jika pengguna lupa menentukan `requests` atau `limits` saat membuat Pod?

*   Jika tidak ada ResourceQuota, Pod mungkin akan dibuat dengan QoS `BestEffort` (jika requests & limits tidak ada) atau `Burstable` (jika hanya salah satu yang ada), yang perilakunya kurang dapat diprediksi.
*   Jika *ada* ResourceQuota komputasi yang aktif di namespace, pembuatan Pod **akan gagal** karena tidak memiliki `requests`/`limits` yang diperlukan untuk validasi kuota.

Untuk mengatasi ini dan membantu menegakkan praktik baik penggunaan resource, Kubernetes menyediakan objek **LimitRange**.

## Apa itu LimitRange?

LimitRange adalah objek kebijakan (namespaced) yang memungkinkan administrator untuk menetapkan **batasan (constraints)** pada penggunaan sumber daya komputasi (CPU, Memori) **per entitas** (seperti Pod atau Container) di dalam satu Namespace.

LimitRange dapat menentukan:

1.  **Nilai Default Request:** Jika sebuah Kontainer dibuat tanpa `requests.cpu` atau `requests.memory` secara eksplisit, nilai default dari LimitRange ini akan otomatis diterapkan padanya.
2.  **Nilai Default Limit:** Jika sebuah Kontainer dibuat tanpa `limits.cpu` atau `limits.memory` secara eksplisit, nilai default dari LimitRange ini akan otomatis diterapkan.
3.  **Batas Minimum:** Ukuran `requests` atau `limits` minimum yang diizinkan untuk CPU/Memori per Kontainer. Pods yang meminta kurang dari ini akan ditolak.
4.  **Batas Maksimum:** Ukuran `requests` atau `limits` maksimum yang diizinkan untuk CPU/Memori per Kontainer atau per Pod. Pods yang meminta lebih dari ini akan ditolak.
5.  **Rasio Limit/Request Maksimum:** Membatasi rasio antara `limit` dan `request` untuk suatu sumber daya (misalnya, memastikan limit memori tidak lebih dari 2x request memori).

## Manfaat LimitRange

*   **Mencegah Pod Tanpa Batas:** Memastikan semua kontainer memiliki `requests` dan `limits` (dengan menerapkan nilai default), mencegah Pod `BestEffort` yang tidak terduga.
*   **Memfasilitasi ResourceQuota:** Memungkinkan Pod dibuat bahkan jika pengguna lupa menentukan `requests`/`limits`, karena nilai default akan diterapkan, sehingga validasi ResourceQuota dapat berjalan.
*   **Membatasi Konsumsi Ekstrim:** Mencegah pengguna secara tidak sengaja atau sengaja meminta resource yang sangat besar (`max`) atau sangat kecil (`min`).
*   **Menegakkan Rasio:** Membantu menjaga rasio yang wajar antara resource yang diminta dan dibatasi.

## Contoh YAML LimitRange

```yaml
apiVersion: v1
kind: LimitRange
metadata:
  name: cpu-mem-defaults
  namespace: development # Berlaku untuk namespace 'development'
spec:
  limits:
  # --- Batasan per Kontainer ---
  - type: Container
    # Nilai Default (jika tidak ditentukan oleh kontainer)
    default:
      cpu: "200m"    # Default limit CPU 0.2 core
      memory: "512Mi" # Default limit Memori 512 MiB
    defaultRequest:
      cpu: "100m"    # Default request CPU 0.1 core
      memory: "256Mi" # Default request Memori 256 MiB
    # Batas Maksimum per Kontainer
    max:
      cpu: "1"       # Maks limit CPU 1 core per kontainer
      memory: "1Gi"  # Maks limit Memori 1 GiB per kontainer
    # Batas Minimum per Kontainer
    min:
      cpu: "50m"     # Min request/limit CPU 0.05 core per kontainer
      memory: "64Mi" # Min request/limit Memori 64 MiB per kontainer
    # Rasio Maksimum Limit terhadap Request
    maxLimitRequestRatio:
      cpu: 4         # Limit CPU maks 4x request CPU
      memory: 3      # Limit Memori maks 3x request Memori

  # --- Batasan per Pod (Opsional) ---
  # - type: Pod
  #   # Batas Maksimum TOTAL untuk SEMUA kontainer dalam satu Pod
  #   max:
  #     cpu: "2"
  #     memory: "2Gi"

  # --- Batasan per PVC (Opsional) ---
  # - type: PersistentVolumeClaim
  #   # Batas ukuran Maksimum/Minimum untuk storage yang diminta PVC
  #   max:
  #     storage: 50Gi
  #   min:
  #     storage: 1Gi
```

**Penjelasan:**

*   `type: Container`: Batasan ini berlaku untuk setiap kontainer individual dalam Pod.
*   `default`: Jika kontainer tidak menentukan `limits`, nilai ini akan diterapkan sebagai `limits`-nya.
*   `defaultRequest`: Jika kontainer tidak menentukan `requests`, nilai ini akan diterapkan sebagai `requests`-nya.
*   `max`: Nilai `requests` atau `limits` tidak boleh melebihi batas ini per kontainer.
*   `min`: Nilai `requests` atau `limits` tidak boleh kurang dari batas ini per kontainer.
*   `maxLimitRequestRatio`: Mengontrol seberapa besar `limit` bisa melebihi `request`. Misalnya, jika `request.memory: 100Mi` dan `maxLimitRequestRatio.memory: 3`, maka `limit.memory` tidak boleh lebih dari `300Mi`.

**Menerapkan LimitRange:**

```bash
kubectl apply -f my-limitrange.yaml -n development
```

**Melihat LimitRange:**

```bash
kubectl describe limitrange cpu-mem-defaults -n development
```

## Bagaimana LimitRange Diterapkan?

LimitRange diterapkan oleh **Admission Controller** saat Pod dibuat atau diperbarui:

1.  Jika sebuah kontainer dalam Pod tidak memiliki `requests` atau `limits` yang ditentukan, Admission Controller akan melihat LimitRange di namespace tersebut.
2.  Jika ada nilai `defaultRequest` atau `default` yang relevan di LimitRange, nilai tersebut akan **disuntikkan** ke dalam spesifikasi kontainer.
3.  Setelah nilai default disuntikkan (jika perlu), Admission Controller akan **memvalidasi** `requests` dan `limits` akhir dari setiap kontainer (dan Pod secara keseluruhan, jika ada batasan Pod) terhadap batasan `min`, `max`, dan `maxLimitRequestRatio` yang didefinisikan dalam LimitRange.
4.  Jika ada pelanggaran (misalnya, meminta lebih dari `max`, kurang dari `min`, atau rasio terlampaui), pembuatan/pembaruan Pod akan **ditolak**.

## Interaksi dengan ResourceQuota

LimitRange dan ResourceQuota bekerja sama dengan baik:

*   **LimitRange** memastikan bahwa setiap kontainer *memiliki* nilai `requests` dan `limits` (baik secara eksplisit maupun melalui default).
*   **ResourceQuota** kemudian dapat memvalidasi *total* `requests` dan `limits` dari *semua* Pods di namespace terhadap batas keseluruhan yang ditetapkan.

Menggunakan keduanya secara bersamaan memberikan kontrol yang komprehensif atas penggunaan sumber daya dalam sebuah namespace, baik pada level per-Pod/Container maupun pada level agregat namespace.

LimitRange adalah alat kebijakan yang berguna untuk menetapkan standar penggunaan resource, mencegah konfigurasi ekstrem, dan memastikan kompatibilitas dengan ResourceQuotas, sehingga meningkatkan prediktabilitas dan stabilitas cluster.
