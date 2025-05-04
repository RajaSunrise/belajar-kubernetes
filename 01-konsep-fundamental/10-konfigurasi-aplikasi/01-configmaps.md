# ConfigMaps: Mengelola Konfigurasi Non-Sensitif

Saat membangun aplikasi, kita seringkali perlu memisahkan **konfigurasi** dari **kode aplikasi** itu sendiri. Konfigurasi dapat berupa:

*   Endpoint URL untuk layanan lain (misalnya, URL database, API eksternal).
*   Pengaturan fitur (feature flags).
*   Level logging.
*   Parameter tuning kinerja.
*   Konten file konfigurasi utuh (misalnya, `nginx.conf`, `settings.xml`).

Menyimpan konfigurasi ini langsung di dalam image kontainer adalah praktik yang buruk karena:

*   **Tidak Fleksibel:** Setiap perubahan konfigurasi memerlukan pembangunan ulang (rebuild) image.
*   **Sulit Dikelola:** Konfigurasi yang sama mungkin perlu digunakan oleh banyak aplikasi atau di lingkungan yang berbeda (dev, staging, prod) dengan nilai yang berbeda.
*   **Kurang Portabel:** Image menjadi terikat pada konfigurasi spesifik.

Kubernetes menyediakan solusi untuk ini melalui objek **ConfigMap**.

## Apa itu ConfigMap?

ConfigMap adalah objek API Kubernetes yang digunakan untuk menyimpan data konfigurasi **non-sensitif** dalam bentuk **pasangan key-value**. ConfigMap memungkinkan Anda memisahkan konfigurasi dari Pods dan kontainer Anda, membuat aplikasi lebih portabel dan mudah dikelola.

**Penting:** ConfigMap dirancang untuk data **non-sensitif**. Untuk data sensitif seperti password, token API, atau kunci TLS, gunakan objek [Secret](./02-secrets.md).

## Struktur Data ConfigMap

Data dalam ConfigMap disimpan dalam dua field utama di bawah `data` atau `binaryData`:

*   **`data`:** Menyimpan data konfigurasi sebagai **string UTF-8 biasa**. Ini adalah field yang paling umum digunakan. Setiap entri adalah pasangan key-value. Value bisa berupa string sederhana atau string multi-baris (misalnya, konten file konfigurasi).
*   **`binaryData`:** Menyimpan data konfigurasi sebagai **byte sequence yang di-encode base64**. Digunakan jika Anda perlu menyimpan data biner yang tidak dapat direpresentasikan sebagai string UTF-8. `kubectl` akan menangani encoding/decoding base64 secara otomatis saat Anda menggunakan `kubectl create configmap ... --from-file`.

**Penting:** Total ukuran data dalam ConfigMap dibatasi (biasanya sekitar 1 MiB, tergantung konfigurasi etcd). ConfigMap tidak dirancang untuk menyimpan file besar.

## Membuat ConfigMap

Ada beberapa cara untuk membuat ConfigMap:

**1. Dari Literal (Key-Value Langsung):**
   ```bash
   kubectl create configmap app-settings --from-literal=log_level=INFO --from-literal=api_url=http://my-api-service:8080
   ```

**2. Dari File Tunggal (Key = Nama File, Value = Konten File):**
   ```bash
   # Buat file contoh: echo "Hello World" > my-message.txt
   kubectl create configmap message-config --from-file=my-message.txt
   # ConfigMap akan punya key 'my-message.txt' dengan value 'Hello World\n'
   ```

**3. Dari File Tunggal dengan Key Berbeda:**
   ```bash
   # Buat file contoh: echo "max_connections=100" > db.properties
   kubectl create configmap db-config --from-file=database-settings.props=db.properties
   # ConfigMap akan punya key 'database-settings.props' dengan value 'max_connections=100\n'
   ```

**4. Dari Direktori (Setiap File jadi Key):**
   ```bash
   # Buat direktori dan file di dalamnya:
   # mkdir config-dir
   # echo "user=admin" > config-dir/app.properties
   # echo "server { listen 80; }" > config-dir/nginx.conf
   kubectl create configmap app-config-bundle --from-file=config-dir/
   # ConfigMap akan punya key 'app.properties' dan 'nginx.conf'
   ```

**5. Dari File `env`:**
   ```bash
   # Buat file .env:
   # echo "VAR1=value1" > app.env
   # echo "VAR2=value2" >> app.env
   kubectl create configmap env-config --from-env-file=app.env
   # ConfigMap akan punya key 'VAR1' dan 'VAR2'
   ```

**6. Menggunakan Manifest YAML (Cara Paling Umum & Deklaratif):**
   Buat file `my-configmap.yaml`:
   ```yaml
   apiVersion: v1
   kind: ConfigMap
   metadata:
     name: my-app-config
     namespace: default
   data:
     # Key-value sederhana
     PLAYER_INITIAL_LIVES: "3"
     UI_COLOR_SCHEME: "dark"

     # Konten file sebagai value (gunakan | untuk mempertahankan newline)
     game.properties: |
       enemy.type=troll
       difficulty=hard
       lives="3" # Nilai tetap string di ConfigMap

     nginx-config.conf: |
       server {
         listen       80;
         server_name  localhost;

         location / {
           root   /usr/share/nginx/html;
           index  index.html index.htm;
         }
         error_page   500 502 503 504  /50x.html;
         location = /50x.html {
           root   /usr/share/nginx/html;
         }
       }
   # binaryData: # Untuk data biner (value harus base64 encoded)
   #   logo.png: R0lGODlhAQABAIAAAAUEBAAAACwAAAAAAQABAAACAkQBADs=
   ```
   Terapkan dengan: `kubectl apply -f my-configmap.yaml`

## Menggunakan ConfigMap di Pods

Ada dua cara utama untuk mengkonsumsi data dari ConfigMap di dalam Pod Anda:

**1. Sebagai Environment Variables:**
   *   Setiap key dari ConfigMap dapat disuntikkan sebagai variabel lingkungan ke dalam satu atau lebih kontainer.
   *   Cocok untuk nilai konfigurasi sederhana.

   ```yaml
   # ... bagian Pod spec ...
   containers:
   - name: my-container
     image: my-app
     env:
       # Menyuntikkan satu key dari ConfigMap
       - name: PLAYER_LIVES # Nama env var di kontainer
         valueFrom:
           configMapKeyRef:
             name: my-app-config # Nama ConfigMap
             key: PLAYER_INITIAL_LIVES # Key di ConfigMap
       # Menyuntikkan semua key dari ConfigMap sebagai env vars
     envFrom:
       - configMapRef:
           name: my-app-config # Nama ConfigMap
   ```

**2. Sebagai File dalam Volume (Cara Paling Umum & Fleksibel):**
   *   Anda dapat me-mount ConfigMap sebagai volume di dalam Pod. Setiap key dalam `data` ConfigMap akan menjadi sebuah file di dalam direktori mount volume tersebut, dengan nama file sama dengan key dan isi file sama dengan value.
   *   Ini adalah cara yang disarankan untuk file konfigurasi utuh atau ketika aplikasi Anda mengharapkan konfigurasi dibaca dari file.

   ```yaml
   # ... bagian Pod spec ...
   containers:
   - name: my-container
     image: my-app
     volumeMounts:
     - name: config-vol # Nama mount (harus cocok dgn volume di bawah)
       mountPath: /etc/config # Direktori tujuan di kontainer
       # readOnly: true # Opsional: Mount sebagai read-only
   # ... kontainer lain ...
   volumes:
   - name: config-vol # Nama volume
     configMap:
       # Berikan nama ConfigMap yang akan di-mount
       name: my-app-config
       # items: # Opsional: Pilih key spesifik & proyeksikan ke path berbeda
       # - key: game.properties
       #   path: game_settings.ini # Key 'game.properties' akan jadi file 'game_settings.ini'
       # - key: nginx-config.conf
       #   path: httpd.conf
       # defaultMode: 0444 # Opsional: Atur izin file (default 0644)
   ```
   Dalam contoh volume ini, di dalam kontainer di path `/etc/config`, akan ada file:
   *   `/etc/config/PLAYER_INITIAL_LIVES` (berisi "3")
   *   `/etc/config/UI_COLOR_SCHEME` (berisi "dark")
   *   `/etc/config/game.properties` (berisi konten multi-barisnya)
   *   `/etc/config/nginx-config.conf` (berisi konten multi-barisnya)

## Pembaruan ConfigMap dan Propagasi

*   ConfigMap dapat diperbarui setelah dibuat (misalnya, menggunakan `kubectl edit configmap` atau `kubectl apply` lagi dengan file yang diperbarui).
*   **Penting:** Bagaimana pembaruan ini dipropagasi ke Pods yang menggunakannya **tergantung pada bagaimana ConfigMap dikonsumsi**:
    *   **Environment Variables:** Nilai environment variable **TIDAK diperbarui secara otomatis** saat ConfigMap berubah. Pod perlu **di-restart** (misalnya, dengan melakukan rollout pada Deployment) untuk mengambil nilai env var yang baru.
    *   **Volume Mounts:** File yang di-mount dari ConfigMap sebagai volume **AKAN diperbarui secara otomatis** oleh Kubelet (biasanya dalam waktu sekitar satu menit, tergantung konfigurasi Kubelet `syncFrequency`). **NAMUN**, aplikasi yang berjalan di dalam kontainer mungkin **perlu diberi tahu atau di-restart** untuk membaca ulang file konfigurasi yang telah diperbarui tersebut. Beberapa aplikasi mendukung pemuatan ulang konfigurasi (misalnya, dengan sinyal SIGHUP), sementara yang lain mungkin memerlukan restart kontainer.

ConfigMap adalah alat esensial untuk mengelola konfigurasi aplikasi di Kubernetes secara fleksibel dan terpisah dari image kontainer, tetapi ingatlah batasannya untuk data non-sensitif dan pertimbangkan bagaimana pembaruan akan ditangani oleh aplikasi Anda.
