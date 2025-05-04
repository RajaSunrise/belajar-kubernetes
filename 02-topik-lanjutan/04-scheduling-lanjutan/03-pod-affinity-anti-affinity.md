# Pod Affinity & Anti-Affinity: Menempatkan Pods Relatif Terhadap Pods Lain

Sementara Node Affinity/Selector mengontrol penempatan Pod berdasarkan properti *Node*, **Pod Affinity** dan **Pod Anti-Affinity** memungkinkan Anda mengontrol penempatan Pod berdasarkan **label dari Pods lain** yang sudah berjalan di cluster.

Ini memungkinkan Anda untuk:

*   **Collocation (Pod Affinity):** Menempatkan Pods tertentu berdekatan satu sama lain (di Node yang sama, zona yang sama, dll.). Berguna jika Pods perlu berkomunikasi secara intensif atau berbagi sumber daya lokal.
*   **Separation (Pod Anti-Affinity):** Menyebarkan Pods dari layanan yang sama ke Node atau zona yang berbeda untuk meningkatkan ketersediaan tinggi (HA). Jika satu Node/zona gagal, tidak semua instance layanan Anda ikut gagal.

## Konsep Utama

*   **Berbasis Label Pod:** Aturan affinity/anti-affinity bekerja dengan mencocokkan `labelSelector` terhadap label Pods lain.
*   **Domain Topologi (`topologyKey`):** Kunci terpenting dalam affinity/anti-affinity. Ini mendefinisikan "domain" atau "area" di mana aturan diterapkan. Scheduler akan melihat nilai label Node yang sesuai dengan `topologyKey` ini untuk menentukan apakah Pods berada di domain yang sama atau berbeda. Contoh `topologyKey` umum:
    *   `kubernetes.io/hostname`: Domainnya adalah Node individual.
    *   `topology.kubernetes.io/zone`: Domainnya adalah Zona Ketersediaan (AZ) cloud provider.
    *   `topology.kubernetes.io/region`: Domainnya adalah Region cloud provider.
    *   Label Node kustom lainnya (misalnya, `rack-id`).
*   **Aturan Wajib vs. Preferensi:** Sama seperti Node Affinity, Pod Affinity/Anti-Affinity memiliki dua jenis aturan:
    *   **`requiredDuringSchedulingIgnoredDuringExecution`**: Aturan **HARUS** dipenuhi agar Pod dapat dijadwalkan. Jika tidak bisa dipenuhi, Pod akan `Pending`.
    *   **`preferredDuringSchedulingIgnoredDuringExecution`**: Scheduler akan **MENCOBA** memenuhi aturan ini (berdasarkan `weight`), tetapi Pod *masih bisa* dijadwalkan meskipun aturan tidak dapat dipenuhi.
*   **`IgnoredDuringExecution`**: Sama seperti Node Affinity, aturan ini hanya dievaluasi saat penjadwalan awal. Perubahan label pada Pods lain atau perpindahan Pods lain *setelah* Pod ini dijadwalkan tidak akan menyebabkan Pod ini digusur. (Ada juga varian `RequiredDuringExecution` yang direncanakan tetapi belum stabil sepenuhnya).

## Pod Affinity (`spec.affinity.podAffinity`)

Menarik Pod agar dijadwalkan ke domain topologi (Node, zona, dll.) di mana sudah ada Pod lain yang cocok dengan `labelSelector`.

**Kasus Penggunaan:**

*   Menempatkan web server Pod di Node yang sama dengan cache Pod (Redis/Memcached) untuk latensi rendah.
*   Menempatkan Pod aplikasi di zona yang sama dengan Pod database utamanya.

**Contoh YAML (Preferensi):**

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: web-server
spec:
  affinity:
    podAffinity:
      preferredDuringSchedulingIgnoredDuringExecution:
      - weight: 100 # Preferensi tertinggi
        podAffinityTerm:
          labelSelector:
            matchExpressions: # Pilih Pods dengan label...
            - key: app
              operator: In
              values:
              - cache # ... 'app=cache'
          # Domain di mana kita mencari Pod 'app=cache'
          topologyKey: kubernetes.io/hostname # Cari di Node yang sama
  containers:
  - name: web-app
    image: my-web-app:1.0
```
*Scheduler akan sangat lebih memilih untuk menempatkan Pod `web-server` ini di Node yang sama (`topologyKey: kubernetes.io/hostname`) di mana sudah ada Pod lain yang berjalan dengan label `app=cache`.*

## Pod Anti-Affinity (`spec.affinity.podAntiAffinity`)

Mendorong Pod agar **tidak** dijadwalkan ke domain topologi (Node, zona, dll.) di mana sudah ada Pod lain yang cocok dengan `labelSelector`.

**Kasus Penggunaan:**

*   **High Availability (HA):** Menyebarkan replika dari Deployment atau StatefulSet yang sama ke Node atau Zona yang berbeda. Jika satu Node/Zona gagal, instance lain masih tersedia. Ini adalah kasus penggunaan paling umum.
*   Mencegah dua aplikasi yang "bermusuhan" (misalnya, menggunakan resource yang sama secara intensif) berjalan di Node yang sama.

**Contoh YAML (Wajib untuk HA):**

Misalkan kita memiliki Deployment dengan label `app=my-critical-service`. Kita ingin memastikan tidak ada dua Pod dari Deployment ini yang berjalan di Node yang sama.

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-critical-service-deployment
spec:
  replicas: 3
  selector:
    matchLabels:
      app: my-critical-service # Selector Deployment
  template:
    metadata:
      labels:
        app: my-critical-service # Label Pod (penting untuk anti-affinity)
    spec:
      affinity:
        podAntiAffinity:
          requiredDuringSchedulingIgnoredDuringExecution: # Wajib
          - labelSelector:
              matchExpressions: # Jangan jadwalkan di Node jika sudah ada Pod...
              - key: app
                operator: In
                values:
                - my-critical-service # ...dengan label 'app=my-critical-service' (yaitu Pod dari deployment ini sendiri)
            topologyKey: kubernetes.io/hostname # Domainnya adalah Node individual
      containers:
      - name: critical-service-container
        image: my-critical-service:ha
```
*Aturan `required...` ini akan mencegah Scheduler menempatkan Pod baru dari Deployment ini ke Node mana pun yang sudah menjalankan Pod lain dengan label `app=my-critical-service`. Hasilnya, 3 replika akan tersebar di 3 Node yang berbeda (jika tersedia Node yang cukup).*

**Contoh YAML (Preferensi untuk Sebaran Zona):**

```yaml
apiVersion: apps/v1
kind: Deployment
# ... metadata, replicas, selector ...
  template:
    metadata:
      labels:
        app: my-scalable-app
    spec:
      affinity:
        podAntiAffinity:
          preferredDuringSchedulingIgnoredDuringExecution: # Preferensi
          - weight: 100
            podAffinityTerm:
              labelSelector:
                matchExpressions:
                - key: app
                  operator: In
                  values:
                  - my-scalable-app
              topologyKey: topology.kubernetes.io/zone # Sebarkan antar Zona
      containers:
      # ... container spec ...
```
*Scheduler akan mencoba sebaik mungkin untuk tidak menempatkan Pod dari Deployment ini di Zona Ketersediaan yang sama dengan Pod lain dari Deployment yang sama.*

## Pertimbangan Penting

*   **Performa:** Aturan Affinity/Anti-Affinity (terutama yang `required...`) dapat menambah overhead pada Scheduler, karena perlu memeriksa label semua Pod lain di domain topologi yang relevan. Di cluster yang sangat besar, ini bisa signifikan.
*   **Ketersediaan Node/Domain:** Aturan `required...` dapat menyebabkan Pod tetap `Pending` jika tidak ada Node/domain topologi yang memenuhi syarat. Pastikan Anda memiliki cukup Node/domain untuk memenuhi aturan wajib Anda, terutama untuk anti-affinity.
*   **Label yang Tepat:** Pastikan `labelSelector` dalam aturan affinity/anti-affinity Anda secara akurat menargetkan Pods yang Anda inginkan (atau tidak inginkan) untuk berada di domain yang sama. Untuk anti-affinity HA dalam satu Deployment/StatefulSet, selector biasanya cocok dengan label Pod dari template itu sendiri.
*   **`topologyKey`:** Pikirkan baik-baik tentang `topologyKey` yang paling sesuai. Apakah Anda ingin pemisahan/kolokasi per Node, per Zona, per Region, atau berdasarkan kriteria lain?
*   **Kombinasi:** Anda dapat mengkombinasikan Pod Affinity, Pod Anti-Affinity, dan Node Affinity dalam satu Pod `spec` untuk aturan penempatan yang sangat spesifik.

Pod Affinity dan Anti-Affinity adalah alat yang sangat berguna untuk mengoptimalkan ketersediaan, performa, dan penempatan relatif beban kerja Anda di dalam cluster Kubernetes. Kasus penggunaan paling umum adalah menyebarkan replika untuk ketersediaan tinggi menggunakan `podAntiAffinity` yang `required...` dengan `topologyKey: kubernetes.io/hostname`.
