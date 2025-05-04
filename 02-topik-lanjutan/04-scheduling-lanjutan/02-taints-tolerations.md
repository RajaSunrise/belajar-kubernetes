# Taints & Tolerations: Mendorong Pod Menjauh dari Node

Berbeda dengan Node Affinity yang *menarik* Pod ke sekumpulan Node tertentu, **Taints** dan **Tolerations** bekerja dengan cara sebaliknya: mereka memungkinkan sebuah Node untuk **menolak (repel)** sekumpulan Pod agar tidak dijadwalkan padanya.

*   **Taint:** Diterapkan pada **Node**. Taint menandai bahwa Node tersebut "tercemar" dengan properti tertentu, dan Pods yang tidak secara eksplisit *mentolerir* taint tersebut tidak akan dijadwalkan di sana (atau akan digusur jika sudah berjalan, tergantung efeknya).
*   **Toleration:** Diterapkan pada **Pod**. Toleration memungkinkan (tetapi tidak mewajibkan) Pod untuk dijadwalkan ke Node dengan Taint yang cocok.

Ini adalah mekanisme **penolakan** atau **pembatasan** penjadwalan.

## Konsep Taint

Taint terdiri dari tiga bagian:

1.  **`key`**: Nama taint (string). Harus berupa nama domain DNS yang valid.
2.  **`value`**: Nilai taint (string). Bisa kosong.
3.  **`effect`**: Menentukan apa yang terjadi pada Pods yang *tidak* mentolerir taint ini. Ada tiga efek:
    *   **`NoSchedule`**: Pod baru **tidak akan dijadwalkan** ke Node ini kecuali mereka memiliki toleration yang cocok. Pod yang sudah berjalan *sebelum* taint ditambahkan **tidak akan digusur**.
    *   **`PreferNoSchedule`**: Versi "lunak" dari `NoSchedule`. Scheduler akan **mencoba untuk tidak** menjadwalkan Pod yang tidak mentolerir taint ini ke Node, tetapi **tidak ada jaminan**. Jika tidak ada Node lain yang cocok, Pod *masih bisa* dijadwalkan di Node ini.
    *   **`NoExecute`**: Efek paling kuat. Pod baru **tidak akan dijadwalkan**, dan Pod yang **sudah berjalan** di Node tersebut yang *tidak* mentolerir taint ini akan **digusur (evicted)** dari Node. Pod dapat menentukan `tolerationSeconds` untuk menunda penggusuran setelah taint ditambahkan.

**Menambahkan/Menghapus Taint pada Node:**
Anda menggunakan `kubectl taint` untuk mengelola taint pada Node.

```bash
# Tambah Taint 'key1=value1:NoSchedule' ke 'node1'
kubectl taint nodes node1 key1=value1:NoSchedule

# Tambah Taint 'dedicated=gpu:NoExecute' ke 'node2'
kubectl taint nodes node2 dedicated=gpu:NoExecute

# Hapus Taint dengan key 'key1' dan effect 'NoSchedule' dari 'node1'
kubectl taint nodes node1 key1:NoSchedule-

# Hapus semua Taint dengan key 'dedicated' dari 'node2'
kubectl taint nodes node2 dedicated-
```

## Konsep Toleration

Toleration didefinisikan dalam `spec.tolerations` pada objek Pod. Setiap toleration mendefinisikan:

1.  **`key`**: Nama taint yang akan ditoleransi. Jika kosong, cocok dengan semua key (jika `operator: Exists`).
2.  **`operator`**: Bagaimana mencocokkan `key` dan `value`.
    *   `Equal` (Default): `key` dan `value` dari toleration harus sama persis dengan `key` dan `value` dari taint. Jika `value` di toleration dihilangkan, ia hanya cocok dengan taint yang `key`-nya sama dan *tidak memiliki* `value` (atau `value`-nya string kosong).
    *   `Exists`: Hanya `key` yang perlu ada pada taint (nilai `value` taint diabaikan). Jika `key` di toleration dihilangkan bersamaan dengan `operator: Exists`, ini akan mentolerir *semua* taint (semua key, value, dan effect).
3.  **`value`**: Nilai yang akan dicocokkan (jika `operator: Equal`).
4.  **`effect`**: Efek taint yang akan ditoleransi (`NoSchedule`, `PreferNoSchedule`, `NoExecute`). Jika kosong, cocok dengan *semua* efek untuk `key` (dan `value`, jika `operator: Equal`) yang cocok.
5.  **`tolerationSeconds`**: Hanya relevan untuk `effect: NoExecute`. Menentukan berapa lama (dalam detik) Pod akan tetap terikat pada Node setelah taint `NoExecute` yang cocok ditambahkan atau ditemukan. Setelah waktu ini habis, Pod akan digusur. Jika tidak ditentukan, Pod tidak akan digusur karena taint `NoExecute` yang ditoleransi.

**Penting:** Toleration **memungkinkan** Pod dijadwalkan ke Node yang "tercemar", tetapi **tidak menjamin** bahwa Pod *akan* dijadwalkan ke sana. Affinity (atau tidak adanya Node lain yang cocok) masih diperlukan untuk benar-benar menarik Pod ke Node tersebut. Toleration hanya "membuka kunci" agar Node tersebut bisa dipertimbangkan oleh Scheduler.

## Contoh YAML Pod dengan Tolerations

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: my-app-tolerates
spec:
  tolerations: # Daftar toleration
  - key: "key1" # Mentolerir taint dengan key 'key1'...
    operator: "Equal" # ...jika value-nya sama persis...
    value: "value1" # ...dengan 'value1'...
    effect: "NoSchedule" # ...dan effect-nya 'NoSchedule'.
  - key: "dedicated" # Mentolerir taint dengan key 'dedicated'...
    operator: "Exists" # ...apa pun value-nya (Exists)...
    effect: "NoExecute" # ...jika effect-nya 'NoExecute'.
    tolerationSeconds: 3600 # Tetap di Node selama 1 jam setelah taint ditambahkan.
  # - key: ""            # Contoh toleransi SEMUA taint (gunakan hati-hati)
  #   operator: "Exists"
  containers:
  - name: main-app
    image: my-app:3.0
    # ...
```

## Kasus Penggunaan Umum Taints & Tolerations

1.  **Node Dedicated:**
    *   Terapkan Taint (misalnya, `dedicated=my-special-app:NoSchedule`) ke sekumpulan Node.
    *   Tambahkan Toleration yang cocok ke Pods yang *hanya* boleh berjalan di Node dedicated tersebut.
    *   (Opsional) Tambahkan Node Affinity ke Pods tersebut untuk *memastikan* mereka hanya dijadwalkan ke Node dedicated itu, bukan Node lain yang mungkin tidak memiliki Taint.

2.  **Node dengan Hardware Khusus:**
    *   Terapkan Taint (misalnya, `hardware=gpu:NoSchedule`) ke Node dengan GPU.
    *   Pods yang memerlukan GPU harus memiliki Toleration yang cocok (dan biasanya juga Node Affinity/Selector untuk GPU). Pods lain tidak akan dijadwalkan ke Node mahal ini.

3.  **Penggusuran Berbasis Taint (Eviction):**
    *   Kubernetes secara otomatis menambahkan Taint `NoExecute` untuk kondisi Node tertentu, seperti:
        *   `node.kubernetes.io/not-ready`: Node tidak siap.
        *   `node.kubernetes.io/unreachable`: Node tidak dapat dihubungi dari control plane.
        *   `node.kubernetes.io/memory-pressure`: Node kehabisan memori.
        *   `node.kubernetes.io/disk-pressure`: Node kehabisan disk.
        *   `node.kubernetes.io/pid-pressure`: Node kehabisan PID.
        *   `node.kubernetes.io/network-unavailable`: Jaringan Node tidak tersedia.
    *   Secara default, Pods memiliki toleration bawaan untuk `not-ready` dan `unreachable` dengan `tolerationSeconds=300` (5 menit). Ini berarti Pod akan tetap berjalan selama 5 menit di Node yang menjadi `NotReady` atau `Unreachable` sebelum digusur. Anda dapat menimpa ini di Pod spec.
    *   Anda dapat menambahkan Taint `NoExecute` kustom (misalnya, saat melakukan maintenance Node) untuk mengusir Pods secara terkontrol. Pods penting (misalnya, DaemonSet agen monitoring) mungkin perlu memiliki `tolerationSeconds` yang lebih lama atau tidak sama sekali untuk efek `NoExecute` tertentu.

## Hubungan dengan Affinity

*   Taints & Tolerations adalah mekanisme **penolakan**.
*   Node Affinity adalah mekanisme **penarikan**.

Keduanya sering digunakan **bersama-sama** untuk mencapai kontrol penempatan yang presisi. Misalnya, untuk memastikan Pod *hanya* berjalan di Node dedicated `X`:
1.  Terapkan Taint `dedicated=X:NoSchedule` ke Node `X`.
2.  Terapkan Taint `some-other-taint:NoSchedule` ke *semua Node lain*.
3.  Tambahkan Toleration untuk `dedicated=X:NoSchedule` ke Pod.
4.  Tambahkan Node Affinity `required...` yang menargetkan label unik di Node `X`.

Taints dan Tolerations memberikan cara yang kuat untuk mengontrol penjadwalan dengan mengizinkan Node menolak Pod tertentu, memastikan bahwa hanya Pod yang secara eksplisit dirancang untuk berjalan di sana (dengan memiliki toleration) yang akan ditempatkan.
