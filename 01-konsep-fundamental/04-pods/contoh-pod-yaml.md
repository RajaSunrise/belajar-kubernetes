# Contoh YAML Pod Lengkap

Meskipun Anda jarang membuat Pod secara langsung (biasanya melalui Deployment, StatefulSet, dll.), memahami struktur lengkap definisi Pod dalam YAML sangat penting karena `spec.template` pada controller tersebut pada dasarnya adalah definisi Pod.

Berikut adalah contoh YAML yang mendefinisikan sebuah Pod dengan berbagai fitur umum, beserta penjelasan untuk setiap bagian penting:

```yaml
# pod-example.yaml
apiVersion: v1 # Core API group untuk Pod
kind: Pod
metadata:
  name: my-complex-pod
  namespace: web-apps
  labels:
    app: webserver
    environment: production
    tier: frontend
  annotations:
    description: "Contoh Pod dengan berbagai fitur untuk demo"
    contact: "admin@example.com"
    prometheus.io/scrape: "true" # Anotasi untuk Prometheus
    prometheus.io/port: "9113"   # Port metrik (misalnya dari sidecar)
spec:
  # --- Konfigurasi Umum Pod ---
  restartPolicy: Always # Always, OnFailure, Never (Default: Always)
                       # Menentukan apa yg Kubelet lakukan jika kontainer berhenti
  terminationGracePeriodSeconds: 45 # Waktu tunggu (detik) stlh SIGTERM sblm SIGKILL
                                   # Beri waktu aplikasi shutdown dgn baik
  serviceAccountName: web-app-sa # (Opsional) Service Account yg digunakan Pod ini
  automountServiceAccountToken: true # (Default: true) Mount token SA ke /var/run/secrets...?
  # nodeSelector: # (Opsional) Cara sederhana memilih Node berdasarkan label
  #   disktype: ssd
  # affinity: # (Opsional) Aturan affinity/anti-affinity yg lebih kompleks
  #   nodeAffinity: ...
  #   podAffinity: ...
  #   podAntiAffinity: ...
  # tolerations: # (Opsional) Memungkinkan Pod dijadwalkan di Node dgn Taints
  # - key: "special-node"
  #   operator: "Exists"
  #   effect: "NoSchedule"
  securityContext: # (Opsional) Konteks keamanan level Pod
    runAsUser: 1001       # Jalankan semua kontainer sbg User ID 1001
    runAsGroup: 3000      # Jalankan semua kontainer sbg Group ID 3000
    fsGroup: 2000         # ID Grup yg akan memiliki volume & file di dalamnya
    # seLinuxOptions: ... # Opsi SELinux
    # seccompProfile: ... # Profil Seccomp
  imagePullSecrets: # (Opsional) Jika image dari private registry
  - name: my-registry-key

  # --- Init Containers (Berjalan sebelum containers utama) ---
  initContainers:
  - name: init-wait-for-db
    image: busybox:1.28
    command: ['sh', '-c', 'until nc -vz database-service 5432; do echo "Waiting for DB..."; sleep 2; done;']
    resources:
      limits:
        memory: "64Mi"
        cpu: "50m"

  # --- Containers Aplikasi Utama (Berjalan secara paralel) ---
  containers:
    # Kontainer Aplikasi Utama
  - name: main-web-app
    image: my-web-app:v1.2.3 # Gunakan tag spesifik!
    imagePullPolicy: IfNotPresent # Always, Never, IfNotPresent (Default: IfNotPresent jika tag bukan :latest/:kosong, Always jika :latest/:kosong)
    ports:
    - containerPort: 8080 # Port aplikasi listen
      name: http      # Nama untuk port (bisa dirujuk oleh Service/Probe)
      protocol: TCP   # TCP atau UDP (Default: TCP)
    env: # Environment Variables
    - name: APP_ENV
      value: "production"
    - name: DB_HOST
      valueFrom: # Ambil value dari ConfigMap
        configMapKeyRef:
          name: app-config # Nama ConfigMap
          key: database_host # Key di dalam ConfigMap
    - name: API_KEY # Ambil value dari Secret
      valueFrom:
        secretKeyRef:
          name: api-credentials
          key: api-key
    # envFrom: # Alternatif: Muat semua key dari ConfigMap/Secret sbg env vars
    # - configMapRef:
    #     name: app-config-all
    # - secretRef:
    #     name: db-credentials-all
    resources: # Permintaan & Batas Resource
      requests:
        memory: "256Mi"
        cpu: "500m"
      limits:
        memory: "512Mi"
        cpu: "1" # Sama dengan 1000m
    readinessProbe: # Cek kesiapan melayani traffic
      httpGet:
        path: /ready
        port: http # Merujuk nama port di atas
      initialDelaySeconds: 10
      periodSeconds: 5
      failureThreshold: 2
    livenessProbe: # Cek kesehatan aplikasi
      tcpSocket:
        port: 8080 # Cek apakah port masih listen
      initialDelaySeconds: 20
      periodSeconds: 15
    volumeMounts: # Mount volume ke dalam kontainer
    - name: config-volume # Nama volume (harus cocok dgn 'volumes' di bawah)
      mountPath: /etc/app/config # Path tujuan di kontainer
      readOnly: true # Mount sebagai read-only (praktik baik utk config)
    - name: log-storage # Mount volume untuk log
      mountPath: /var/log/app
    - name: static-assets
      mountPath: /usr/share/nginx/html # Contoh jika Nginx sidecar

    # Kontainer Sidecar untuk Logging
  - name: log-forwarder-sidecar
    image: fluent/fluent-bit:latest # Contoh agen logging
    resources:
      requests:
        memory: "64Mi"
        cpu: "50m"
      limits:
        memory: "128Mi"
        cpu: "100m"
    volumeMounts:
    - name: log-storage # Mount volume log yang sama dgn app utama
      mountPath: /logs/app # Path sumber log di sidecar
      readOnly: true # Sidecar hanya membaca
    # (Konfigurasi Fluent Bit biasanya via ConfigMap yg di-mount sbg volume lain)

    # Kontainer Sidecar untuk Monitoring (mis: Nginx exporter)
  - name: nginx-exporter-sidecar
    image: nginx/nginx-prometheus-exporter:0.11
    args: ["-nginx.scrape-uri", "http://localhost:8081/stub_status"] # Asumsi app utama punya endpoint status Nginx
    ports:
    - containerPort: 9113 # Port metrik exporter
      name: metrics
    resources:
      requests: { memory: "32Mi", cpu: "25m" }
      limits: { memory: "64Mi", cpu: "50m" }

  # --- Definisi Volumes yang Digunakan Pod ---
  volumes:
  - name: config-volume # Nama volume (direferensikan oleh volumeMounts)
    configMap: # Tipe volume: dari ConfigMap
      name: app-config # Nama ConfigMap yg akan di-mount
      items: # (Opsional) Pilih key spesifik dan beri nama file berbeda
      - key: app.properties
        path: settings.properties # Key 'app.properties' dari CM akan jadi file 'settings.properties'
      - key: nginx.conf
        path: webserver.conf
  - name: log-storage # Nama volume untuk berbagi log
    emptyDir: {} # Tipe volume: direktori kosong sementara, hidup selama Pod ada
                 # Cocok untuk berbagi file antar kontainer dlm Pod
  - name: static-assets
    persistentVolumeClaim: # Tipe volume: dari PVC (untuk data persisten)
      claimName: my-web-assets-pvc # Nama PVC yang sudah dibuat & Bound

```

**Penjelasan Tambahan:**

*   **`spec.restartPolicy`**: Mengontrol nasib kontainer jika berhenti. `Always` cocok untuk layanan jangka panjang.
*   **`spec.terminationGracePeriodSeconds`**: Waktu yang diberikan pada aplikasi untuk shutdown dengan bersih saat Pod dihapus.
*   **`spec.serviceAccountName`**: Jika aplikasi perlu berinteraksi dengan API Kubernetes, ia akan menggunakan token dari Service Account ini.
*   **`spec.securityContext`**: Mengatur izin dan kapabilitas di level Pod. Menjalankan sebagai non-root (`runAsUser`/`runAsGroup`) adalah praktik keamanan yang baik.
*   **`spec.imagePullSecrets`**: Diperlukan jika image Anda berada di registry privat yang memerlukan autentikasi.
*   **`initContainers`**: Berjalan berurutan sebelum `containers` utama. Berguna untuk tugas setup.
*   **`containers`**: Daftar kontainer aplikasi utama dan sidecar. Berjalan secara paralel.
    *   `imagePullPolicy`: Kapan Kubelet harus mencoba menarik image.
    *   `env`/`envFrom`: Cara menyuntikkan variabel lingkungan (dari nilai literal, ConfigMap, Secret).
    *   `resources`: **Sangat penting** untuk menentukan `requests` dan `limits`.
    *   `readinessProbe`/`livenessProbe`: Untuk pemeriksaan kesehatan dan kesiapan.
    *   `volumeMounts`: Mendefinisikan bagaimana `volumes` dipasang ke dalam filesystem kontainer.
*   **`volumes`**: Mendefinisikan sumber penyimpanan yang dapat digunakan oleh kontainer dalam Pod. Tipe yang umum:
    *   `configMap`: Memuat data dari ConfigMap sebagai file.
    *   `secret`: Memuat data dari Secret sebagai file (lebih aman daripada env vars).
    *   `emptyDir`: Direktori sementara yang kosong, siklus hidupnya sama dengan Pod. Bagus untuk berbagi data antar kontainer.
    *   `persistentVolumeClaim`: Menggunakan penyimpanan persisten yang dikelola oleh PV/PVC.

Contoh ini menunjukkan banyak fitur yang dapat dikonfigurasi dalam sebuah Pod. Saat Anda bekerja dengan controller seperti Deployment, Anda akan mendefinisikan bagian `spec.template` yang sangat mirip dengan `spec` Pod ini (minus beberapa field level Pod seperti `restartPolicy` yang dikelola oleh controller).
