# Lab 03: Menggunakan ConfigMaps dan Secrets untuk Konfigurasi Aplikasi

**Tujuan:** Lab ini mendemonstrasikan cara memisahkan konfigurasi aplikasi (data non-sensitif) dan data rahasia (data sensitif) dari image kontainer menggunakan `ConfigMap` dan `Secret`. Kita akan melihat dua cara umum untuk menyuntikkan data ini ke dalam Pod: sebagai environment variables dan sebagai volume file.

**Konsep yang Dipelajari:**

*   Membuat `ConfigMap` dari literal dan data file.
*   Membuat `Secret` menggunakan `stringData` (lebih mudah) atau dari literal/file (base64).
*   Menyuntikkan data ConfigMap/Secret ke Pod sebagai **environment variables** (`env`, `envFrom`, `valueFrom`).
*   Menyuntikkan data ConfigMap/Secret ke Pod sebagai **volume file** (`volumes`, `volumeMounts`).
*   Memverifikasi bahwa data tersedia di dalam Pod.
*   Memahami perbedaan dan kasus penggunaan untuk env vars vs volume mounts.
*   Mengamati pembaruan data saat ConfigMap/Secret diubah (khususnya untuk volume mounts).

**Prasyarat:**

*   Cluster Kubernetes lokal berjalan.
*   `kubectl` terinstal dan terkonfigurasi.
*   Pemahaman dasar tentang Pods, ConfigMaps, Secrets, Volumes.

## Langkah 1: Membuat Namespace

```bash
kubectl create namespace lab03-config
kubectl config set-context --current --namespace=lab03-config
```

## Langkah 2: Membuat ConfigMap

Kita akan membuat ConfigMap yang berisi beberapa konfigurasi aplikasi dan contoh file konfigurasi.

Buat file `configmap.yaml`:

```yaml
# configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
data:
  # Key-value pairs sederhana
  LOG_LEVEL: "info"
  API_ENDPOINT: "https://api.example.com/v1"
  FEATURE_FLAG_BETA: "true"

  # Mensimulasikan seluruh konten file konfigurasi
  app-settings.conf: |
    # Ini adalah contoh file konfigurasi
    # yang disimpan dalam satu key ConfigMap.
    color.theme = dark
    retry.count = 3
    timeout.seconds = 15

  another-file.txt: "Ini konten file teks lain."
```

**Terapkan manifest:**

```bash
kubectl apply -f configmap.yaml
```

**Verifikasi:**
```bash
kubectl get configmap app-config -o yaml
kubectl describe configmap app-config
```

## Langkah 3: Membuat Secret

Kita akan membuat Secret untuk menyimpan kredensial API palsu. Kita gunakan `stringData` agar tidak perlu encode base64 manual.

Buat file `secret.yaml`:

```yaml
# secret.yaml
apiVersion: v1
kind: Secret
metadata:
  name: api-credentials
type: Opaque # Tipe default untuk data arbitrer
stringData: # Gunakan stringData agar K8s otomatis encode ke base64
  API_KEY: "super-secret-key-12345"
  API_SECRET: "very-confidential-password!@#"
  # Anda juga bisa menaruh konten file di sini
  # cert.pem: |
  #   -----BEGIN CERTIFICATE-----
  #   ... (konten sertifikat) ...
  #   -----END CERTIFICATE-----
```
**Peringatan Keamanan:** Jangan pernah menyimpan data sensitif *nyata* dalam bentuk plain text seperti ini di file YAML yang akan dimasukkan ke Git. Gunakan mekanisme seperti SOPS atau External Secrets Operator untuk produksi. Ini hanya untuk tujuan demo.

**Terapkan manifest:**

```bash
kubectl apply -f secret.yaml
```

**Verifikasi (Data akan ter-encode):**
```bash
kubectl get secret api-credentials -o yaml
# Anda akan melihat data di bawah 'data:', bukan 'stringData:', dan nilainya adalah base64.
```

## Langkah 4: Menggunakan ConfigMap/Secret sebagai Environment Variables

Buat Pod yang menyuntikkan data dari ConfigMap dan Secret sebagai variabel lingkungan.

Buat file `pod-env.yaml`:

```yaml
# pod-env.yaml
apiVersion: v1
kind: Pod
metadata:
  name: pod-using-env
spec:
  containers:
  - name: main-container
    image: busybox:1.28 # Image sederhana untuk demo
    # Perintah untuk tidur selamanya agar Pod tetap berjalan
    command: [ "/bin/sh", "-c", "while true; do echo 'Running...'; sleep 3600; done" ]
    env: # Mendefinisikan variabel lingkungan satu per satu
      # Mengambil nilai spesifik dari ConfigMap
      - name: APP_LOG_LEVEL # Nama env var di kontainer
        valueFrom:
          configMapKeyRef:
            name: app-config # Nama ConfigMap
            key: LOG_LEVEL   # Key di dalam ConfigMap
      # Mengambil nilai spesifik dari Secret
      - name: SECRET_API_KEY # Nama env var
        valueFrom:
          secretKeyRef:
            name: api-credentials # Nama Secret
            key: API_KEY        # Key di dalam Secret

    envFrom: # Menyuntikkan SEMUA key dari ConfigMap/Secret sebagai env vars
      # Menyuntikkan semua key dari ConfigMap
      - configMapRef:
          name: app-config # Nama ConfigMap
      # Menyuntikkan semua key dari Secret
      - secretRef:
          name: api-credentials # Nama Secret
          # Opsional: Tambahkan prefix ke nama env var yang disuntikkan
          # prefix: "CREDS_"
  restartPolicy: Never
```

**Terapkan manifest:**

```bash
kubectl apply -f pod-env.yaml
```

**Verifikasi Environment Variables:**

```bash
# Tunggu Pod menjadi Running
kubectl get pod pod-using-env

# Masuk ke shell Pod
kubectl exec -it pod-using-env -- /bin/sh

# Di dalam shell Pod, periksa env vars
# printenv | grep APP_LOG_LEVEL
# printenv | grep SECRET_API_KEY
# printenv | grep API_ENDPOINT # Disuntikkan oleh envFrom ConfigMap
# printenv | grep API_SECRET   # Disuntikkan oleh envFrom Secret
# (Nama key dengan '.' atau '-' di CM/Secret akan diubah jadi '_' di env var)
# printenv | grep app_settings_conf

# Keluar dari shell
exit
```
Anda akan melihat variabel lingkungan yang berasal dari ConfigMap dan Secret. **Perhatikan risiko keamanan mengekspos secret sebagai env vars.**

## Langkah 5: Menggunakan ConfigMap/Secret sebagai Volume File

Buat Pod lain yang me-mount data sebagai file di dalam volume. Ini adalah metode yang **lebih disukai** untuk Secrets.

Buat file `pod-volume.yaml`:

```yaml
# pod-volume.yaml
apiVersion: v1
kind: Pod
metadata:
  name: pod-using-volume
spec:
  containers:
  - name: main-container
    image: busybox:1.28
    command: [ "/bin/sh", "-c", "while true; do echo 'Inspecting volumes...'; sleep 60; done" ]
    volumeMounts: # Mendefinisikan di mana volume akan di-mount di kontainer
      # Mount untuk ConfigMap
      - name: config-vol # Nama mount harus cocok dengan nama volume di bawah
        mountPath: "/etc/config" # Direktori mount di kontainer
        # readOnly: true # Opsional
      # Mount untuk Secret
      - name: secret-vol
        mountPath: "/etc/secrets"
        readOnly: true # Praktik terbaik untuk mount secret read-only

  volumes: # Mendefinisikan volume yang akan tersedia untuk Pod
    # Volume dari ConfigMap
    - name: config-vol # Nama volume
      configMap:
        name: app-config # Nama ConfigMap yang akan di-mount
        # Opsional: Pilih key mana yang akan di-mount sebagai file
        # items:
        # - key: API_ENDPOINT
        #   path: api_url.txt # Nama file di dalam mountPath
        # - key: app-settings.conf
        #   path: settings.ini
        # Jika 'items' tidak ditentukan, semua key menjadi nama file.
    # Volume dari Secret
    - name: secret-vol
      secret:
        secretName: api-credentials # Nama Secret yang akan di-mount
        # items: ... # Anda juga bisa memilih key spesifik di sini
        # Opsional: Atur mode izin file (default 0644)
        # defaultMode: 0400 # Contoh: Hanya bisa dibaca oleh pemilik

  restartPolicy: Never
```

**Terapkan manifest:**

```bash
kubectl apply -f pod-volume.yaml
```

**Verifikasi File Volume:**

```bash
# Tunggu Pod menjadi Running
kubectl get pod pod-using-volume

# Masuk ke shell Pod
kubectl exec -it pod-using-volume -- /bin/sh

# Di dalam shell Pod, periksa file yang di-mount
# ls -l /etc/config
# cat /etc/config/LOG_LEVEL
# cat /etc/config/API_ENDPOINT
# cat /etc/config/app-settings.conf

# ls -l /etc/secrets
# cat /etc/secrets/API_KEY
# cat /etc/secrets/API_SECRET

# Keluar dari shell
exit
```
Anda akan melihat file-file yang namanya sesuai dengan key di ConfigMap/Secret, dan isinya adalah nilai dari key tersebut.

## Langkah 6: Mengamati Pembaruan (Volume Mounts)

Salah satu keuntungan me-mount ConfigMap/Secret sebagai volume adalah data yang di-mount **dapat diperbarui secara otomatis** jika ConfigMap/Secret diubah (dengan sedikit penundaan). Mari kita coba:

1.  **Ubah ConfigMap:**
    ```bash
    kubectl edit configmap app-config
    # Ubah nilai LOG_LEVEL dari "info" menjadi "debug", simpan & keluar.
    ```
2.  **Ubah Secret:**
    ```bash
    kubectl edit secret api-credentials
    # API Server akan menampilkan data base64. Anda perlu:
    # a. Salin nilai base64 untuk API_KEY.
    # b. Decode base64 tersebut (misal: echo 'base64-string' | base64 -d).
    # c. Ubah nilainya (misal, tambahkan "-updated").
    # d. Encode kembali nilai baru ke base64 (misal: echo -n 'new-value' | base64).
    # e. Ganti nilai base64 di editor dengan nilai base64 baru. Simpan & keluar.
    # (Ini menunjukkan mengapa mengedit Secret secara manual itu merepotkan!)
    ```
3.  **Periksa Ulang File di Pod `pod-using-volume`:**
    ```bash
    # Tunggu sekitar 1-2 menit agar Kubelet memperbarui mount
    kubectl exec -it pod-using-volume -- /bin/sh

    # Di dalam shell:
    cat /etc/config/LOG_LEVEL # Harusnya sekarang menampilkan 'debug'
    cat /etc/secrets/API_KEY # Harusnya menampilkan nilai baru yang Anda set

    exit
    ```
    Anda akan melihat bahwa file di dalam volume telah diperbarui.

**Catatan Penting:**
*   Pembaruan volume **tidak** memicu restart kontainer. Aplikasi Anda perlu dirancang untuk dapat membaca ulang file konfigurasi/secret secara berkala atau diberi sinyal untuk melakukannya agar dapat mengambil perubahan.
*   Pembaruan **tidak** berlaku untuk data yang disuntikkan sebagai **environment variables**. Env vars hanya dibaca saat kontainer dimulai. Untuk memperbarui env vars, Pod perlu dibuat ulang.

## Langkah 7: Pembersihan

```bash
kubectl delete pod pod-using-env
kubectl delete pod pod-using-volume
kubectl delete configmap app-config
kubectl delete secret api-credentials

# Kembali ke namespace default
# kubectl config set-context --current --namespace=default

# Hapus namespace lab
kubectl delete namespace lab03-config
```

**Selamat!** Anda telah belajar cara menggunakan ConfigMap dan Secret untuk mengelola konfigurasi dan data sensitif, serta dua metode utama untuk menyediakannya ke aplikasi Anda di Kubernetes. Ingatlah untuk memilih metode (env vars vs volume) yang sesuai dengan kebutuhan dan pertimbangan keamanan Anda.
