# Secrets: Mengelola Data Sensitif

Sama seperti ConfigMaps yang digunakan untuk memisahkan konfigurasi dari aplikasi, **Secrets** digunakan untuk tujuan yang sama tetapi secara khusus dirancang untuk menyimpan dan mengelola sejumlah kecil data **sensitif**. Contoh data sensitif meliputi:

*   Password database atau pengguna.
*   Token API (OAuth, token akses pribadi).
*   Kunci SSH (privat dan publik).
*   Sertifikat TLS/SSL (kunci privat dan sertifikat).
*   Informasi kredensial lainnya.

**Menyimpan data sensitif ini secara langsung di image kontainer, file YAML konfigurasi (ConfigMap atau manifest Pod), atau dalam kode sumber adalah praktik keamanan yang sangat buruk.** Kubernetes menyediakan objek `Secret` sebagai cara yang lebih aman untuk menanganinya.

## Apa itu Secret?

Secret adalah objek API Kubernetes yang mirip dengan ConfigMap tetapi ditujukan untuk data rahasia. Ia menyimpan data dalam format key-value.

**Perbedaan Utama dari ConfigMap:**

1.  **Encoding (BUKAN Enkripsi!):** Secara default, nilai data dalam Secret disimpan di `etcd` dalam format **Base64 encoded**. Base64 adalah encoding, **bukan enkripsi**. Siapa pun yang memiliki izin untuk membaca objek Secret dapat dengan mudah mendekode nilai Base64 untuk mendapatkan data asli.
2.  **Keamanan Tambahan (Opsional):**
    *   **Enkripsi Saat Istirahat (At-Rest):** Administrator cluster dapat mengkonfigurasi Kubernetes untuk **mengenkripsi** data Secret saat disimpan di `etcd`, memberikan lapisan perlindungan tambahan jika seseorang mendapatkan akses langsung ke backup `etcd`.
    *   **Kontrol Akses (RBAC):** Akses untuk membaca atau menulis objek Secret harus dibatasi secara ketat menggunakan RBAC hanya kepada pengguna atau Service Account yang benar-benar membutuhkannya.
    *   **Volume Mount (tmpfs):** Saat Secret di-mount sebagai volume, secara default Kubernetes menggunakan filesystem berbasis memori (`tmpfs`), sehingga data Secret tidak ditulis ke disk Node secara persisten (meskipun mungkin disimpan sementara oleh Kubelet).
3.  **Perilaku `kubectl`:**
    *   `kubectl get secret <nama> -o yaml` atau `kubectl edit secret <nama>` **tidak** akan menampilkan nilai `data` (yang base64 encoded) secara default untuk mencegah paparan tidak sengaja. Anda perlu menggunakan opsi seperti `-o jsonpath='{.data}'` atau template Go untuk melihatnya.
    *   `kubectl describe secret <nama>` juga tidak menampilkan nilai datanya.

**Intinya:** Secret memberikan *mekanisme* untuk mengelola data sensitif dan *memfasilitasi* praktik keamanan yang lebih baik (seperti enkripsi at-rest dan RBAC ketat), tetapi **bukanlah solusi keamanan ajaib** dengan sendirinya. Keamanan sebenarnya bergantung pada konfigurasi cluster dan kebijakan akses yang diterapkan.

## Struktur Data Secret

Mirip ConfigMap, data disimpan dalam field:

*   **`data`:** Peta (map) key-value di mana **value** harus berupa string **Base64 encoded**.
*   **`stringData`:** Peta (map) key-value di mana **value** dapat berupa **string biasa (plain text)**. Kubernetes akan **secara otomatis meng-encode Base64** nilai dari `stringData` dan menyimpannya di field `data` saat Secret dibuat atau diperbarui. Field `stringData` bersifat *write-only* (tidak akan pernah ditampilkan saat Anda membaca Secret). Ini lebih nyaman untuk mendefinisikan Secret dalam YAML.

Anda bisa menggunakan `data` atau `stringData`, tetapi tidak keduanya untuk kunci yang sama dalam satu manifest. Jika kunci ada di keduanya, `stringData` akan diutamakan.

## Tipe-tipe Secret (`type`)

Anda dapat menentukan `type` Secret untuk membantu sistem Kubernetes atau alat lain memvalidasi atau memproses data Secret. Beberapa tipe umum:

*   **`Opaque` (Default):** Tipe default, digunakan untuk data arbitrer key-value. Tidak ada validasi format khusus yang dilakukan.
*   **`kubernetes.io/service-account-token`:** Digunakan untuk menyimpan token kredensial yang mengidentifikasi sebuah [Service Account](./../03-security/03-service-accounts-detail.md). Dibuat dan dikelola secara otomatis oleh Kubernetes (atau Token Controller).
*   **`kubernetes.io/dockercfg` atau `kubernetes.io/dockerconfigjson`:** Digunakan untuk menyimpan kredensial autentikasi ke **private Docker registry**. Digunakan dalam field `imagePullSecrets` pada Pod spec.
*   **`kubernetes.io/basic-auth`:** Digunakan untuk kredensial autentikasi basic (username/password). Harus berisi kunci `username` dan `password`.
*   **`kubernetes.io/ssh-auth`:** Digunakan untuk kredensial autentikasi SSH. Harus berisi kunci `ssh-privatekey`.
*   **`kubernetes.io/tls`:** Digunakan untuk menyimpan sertifikat server TLS/SSL dan kunci privatnya. Harus berisi kunci `tls.crt` (sertifikat) dan `tls.key` (kunci privat). Sering digunakan oleh Ingress controllers.
*   **`bootstrap.kubernetes.io/token`:** Digunakan selama proses bootstrap node.

Menentukan tipe yang benar membantu memastikan Secret berisi data yang diharapkan oleh komponen yang akan menggunakannya.

## Membuat Secret

**Peringatan:** Hindari menyimpan manifest YAML Secret dengan data sensitif (bahkan `stringData`) langsung di sistem kontrol versi Anda jika repositori tersebut tidak aman. Pertimbangkan untuk menggunakan alat manajemen secret eksternal (seperti Vault, SOPS) atau mekanisme lain untuk menyuntikkan secret saat deployment.

**1. Dari Literal (Kurang Aman untuk Data Sensitif):**
   ```bash
   # Hati-hati, ini bisa muncul di history shell
   kubectl create secret generic db-user-pass --from-literal=username=admin --from-literal=password='S3cr3tP@ssw0rd!'
   ```

**2. Dari File:**
   ```bash
   # Buat file (misal: berisi token API)
   # echo -n "my-super-secret-api-token" > ./api-token.txt
   kubectl create secret generic api-key-secret --from-file=api-token=./api-token.txt
   ```

**3. Membuat Secret TLS (Umum):**
   ```bash
   # Asumsi Anda sudah punya tls.crt dan tls.key
   kubectl create secret tls my-tls-secret --cert=path/to/tls.crt --key=path/to/tls.key
   ```

**4. Membuat Secret `docker-registry`:**
   ```bash
   kubectl create secret docker-registry my-registry-key \
     --docker-server=<your-registry-server> \
     --docker-username=<your-name> \
     --docker-password=<your-pword> \
     --docker-email=<your-email>
   ```

**5. Menggunakan Manifest YAML (Paling Umum & Deklaratif):**
   Gunakan `stringData` untuk kemudahan, atau `data` jika Anda sudah memiliki nilai base64.

   ```yaml
   # secret-example.yaml
   apiVersion: v1
   kind: Secret
   metadata:
     name: my-app-secrets
     namespace: default
   type: Opaque # Tipe default
   stringData: # Lebih mudah dibaca/ditulis daripada data base64
     database.password: "DifficultPassword123!"
     external.api.key: "abcdef1234567890"
   # --- Atau menggunakan 'data' (value HARUS base64 encoded) ---
   # data:
   #   database.password: RGlmZmljdWx0UGFzc3dvcmQxMjMh # base64 "DifficultPassword123!"
   #   external.api.key: YWJjZGVmMTIzNDU2Nzg5MA==    # base64 "abcdef1234567890"

   ---
   # Contoh Secret TLS
   apiVersion: v1
   kind: Secret
   metadata:
     name: my-ingress-tls
     namespace: ingress-nginx
   type: kubernetes.io/tls # Tipe TLS
   data:
     tls.crt: LS0tLS1CRUdJTiBDRVJUSUZJQ0FURS0tLS0tCk1JSURFVENDQWZrQ0FnMzZNQTBHQ1NxR1NJYjNEUUVCQlFVQU1JR2JNUXN3Q1FZRFZRUUdFd0pLVURFT01Bd0c...<data base64 cert>...=
     tls.key: LS0tLS1CRUdJTiBSU0EgUFJJVkFURSBLRVktLS0tLQpNSUlFcEFJQkFBS0NBUUVBM3lYdzNrMGt2TUZXWGZ3UFlGcHJkaENEZ2RvM1VRaWxOalJhMkJnWGdlRmg4ZTc...<data base64 key>...=
   ```
   Terapkan dengan `kubectl apply -f secret-example.yaml`.

## Menggunakan Secret di Pods

Sama seperti ConfigMap, ada dua cara utama, tetapi **volume mount lebih disarankan untuk data sensitif.**

**1. Sebagai Environment Variables (Kurang Aman):**
   *   Nilai Secret dapat bocor melalui log aplikasi, pesan error, atau inspeksi (`kubectl describe pod`, UI Dashboard). Hindari ini untuk data yang sangat rahasia seperti password.
   ```yaml
   # ... Pod spec ...
   containers:
   - name: my-container
     image: my-app
     env:
       - name: DATABASE_PASSWORD
         valueFrom:
           secretKeyRef:
             name: my-app-secrets # Nama Secret
             key: database.password # Key di Secret
     # envFrom: # Muat semua key dari Secret (lebih berisiko)
     # - secretRef:
     #     name: my-app-secrets
   ```

**2. Sebagai File dalam Volume (Lebih Aman):**
   *   Secret di-mount sebagai file di dalam direktori volume.
   *   Secara default menggunakan `tmpfs` (filesystem berbasis memori), mengurangi risiko data tertulis ke disk.
   *   Aplikasi membaca kredensial dari file tersebut.
   *   Praktik terbaik adalah me-mount sebagai `readOnly`.

   ```yaml
   # ... Pod spec ...
   containers:
   - name: my-container
     image: my-app
     volumeMounts:
     - name: secret-vol # Nama mount volume
       mountPath: "/etc/secrets" # Direktori tujuan di kontainer
       readOnly: true # Sangat disarankan untuk secrets
   # ... kontainer lain ...
   volumes:
   - name: secret-vol # Nama volume
     secret:
       # Berikan nama Secret yang akan di-mount
       secretName: my-app-secrets
       # items: # Opsional: Pilih key spesifik & proyeksikan
       # - key: api.key
       #   path: external-api-token.txt
       # defaultMode: 0400 # Opsional: Atur izin file (lebih ketat)
   ```
   Di dalam kontainer, akan ada file `/etc/secrets/database.password` dan `/etc/secrets/external.api.key`.

**Pembaruan Secret:** Sama seperti ConfigMap, Secret yang di-mount sebagai volume akan diperbarui secara otomatis oleh Kubelet, tetapi aplikasi mungkin perlu diberi tahu atau di-restart untuk menggunakan nilai baru.

Secret adalah cara standar Kubernetes untuk mengelola informasi sensitif, memisahkannya dari konfigurasi aplikasi dan image, serta memungkinkan penerapan kontrol akses dan enkripsi yang lebih baik. Gunakan dengan bijak dan selalu prioritaskan keamanan.
