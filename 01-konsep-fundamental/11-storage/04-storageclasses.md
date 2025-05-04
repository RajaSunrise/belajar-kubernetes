# StorageClasses: Mengaktifkan Penyediaan Volume Dinamis

Dalam pembahasan [PersistentVolume (PV)](./02-persistentvolumes-pv.md), kita melihat ada dua cara PV dapat disediakan: **statis** dan **dinamis**.

*   **Static Provisioning:** Administrator cluster secara manual membuat PV terlebih dahulu. Ini memerlukan pengetahuan tentang infrastruktur penyimpanan yang mendasarinya dan bisa menjadi membosankan jika banyak permintaan penyimpanan.
*   **Dynamic Provisioning:** Ketika pengguna membuat `PersistentVolumeClaim` (PVC) yang meminta jenis penyimpanan tertentu, cluster dapat **secara otomatis membuat (memprovisikan) PV baru** yang cocok dengan permintaan tersebut. Ini menyederhanakan proses bagi pengguna dan administrator.

Mekanisme yang memungkinkan dynamic provisioning di Kubernetes adalah **StorageClass**.

## Apa itu StorageClass?

**StorageClass** adalah objek API Kubernetes (`storage.k8s.io/v1`) yang memungkinkan administrator mendefinisikan **"kelas" atau "jenis" penyimpanan** yang tersedia di cluster. Setiap StorageClass:

*   **Menjelaskan Jenis Penyimpanan:** Mewakili kualitas layanan (misalnya, SSD cepat, HDD lambat), kebijakan backup, atau fitur lain yang ditawarkan oleh backend penyimpanan.
*   **Menentukan Provisioner:** Menunjuk ke plugin volume internal Kubernetes atau driver [Container Storage Interface (CSI)](../../02-topik-lanjutan/02-storage-lanjutan/01-container-storage-interface-csi.md) eksternal yang **tahu cara membuat** volume fisik untuk kelas ini (misalnya, membuat disk EBS di AWS, disk PD di GCE, LUN di SAN).
*   **Menentukan Parameter Provisioning:** Menyertakan parameter spesifik yang akan diteruskan ke provisioner saat membuat volume (misalnya, tipe disk, zona replikasi, opsi enkripsi).

## Mengapa Menggunakan StorageClass?

*   **Otomatisasi (Dynamic Provisioning):** Manfaat utama. Pengguna cukup membuat PVC yang meminta StorageClass tertentu, dan PV akan dibuat secara otomatis sesuai kebutuhan. Mengurangi beban kerja administrator secara signifikan.
*   **Abstraksi Lebih Lanjut:** Pengguna tidak perlu peduli tentang PV; mereka hanya perlu tahu kelas penyimpanan apa (misalnya, "cepat", "standar", "backup") yang mereka butuhkan dan memintanya melalui PVC.
*   **Fleksibilitas:** Administrator dapat mendefinisikan berbagai kelas penyimpanan dengan tingkat kinerja, ketersediaan, dan biaya yang berbeda untuk memenuhi kebutuhan aplikasi yang beragam.
*   **Konsistensi:** Memastikan volume dibuat dengan parameter dan kebijakan yang konsisten sesuai definisi kelasnya.

## Bagaimana Dynamic Provisioning Bekerja dengan StorageClass?

1.  **Administrator Membuat StorageClass:** Admin mendefinisikan satu atau lebih objek StorageClass di cluster, menentukan `provisioner`, `parameters`, `reclaimPolicy`, dll. Satu StorageClass dapat ditandai sebagai **default**.
2.  **Pengguna Membuat PVC:** Pengguna membuat PVC dan menentukan:
    *   `spec.storageClassName`: Nama StorageClass yang diinginkan.
    *   `spec.resources.requests.storage`: Ukuran yang dibutuhkan.
    *   `spec.accessModes`: Mode akses yang dibutuhkan.
3.  **Binding & Provisioning:**
    *   Kubernetes memeriksa apakah ada PV statis yang *tersedia* dan *cocok* dengan `storageClassName` (dan persyaratan lain) dari PVC. Jika ada, PVC akan langsung terikat ke PV statis tersebut.
    *   Jika **tidak ada** PV statis yang cocok *dan* `storageClassName` ditentukan di PVC:
        *   Kubernetes akan memanggil **`provisioner`** yang ditentukan dalam StorageClass tersebut.
        *   Provisioner (berjalan sebagai Pod di cluster atau komponen eksternal) akan menggunakan `parameters` dari StorageClass dan detail dari PVC (ukuran, mode akses) untuk **membuat volume fisik baru** di backend penyimpanan (misalnya, membuat disk EBS baru).
        *   Setelah volume fisik dibuat, provisioner akan membuat **objek PV baru** di Kubernetes yang merepresentasikan volume fisik tersebut, dengan `storageClassName` dan `reclaimPolicy` yang sesuai dari StorageClass.
        *   Objek PV baru ini akan secara otomatis **terikat (Bound)** ke PVC yang memicu pembuatannya.
    *   Jika `storageClassName` **tidak ditentukan** di PVC *dan* ada StorageClass yang ditandai **default** di cluster, StorageClass default tersebut akan digunakan untuk dynamic provisioning.
    *   Jika `storageClassName` tidak ditentukan dan tidak ada StorageClass default, PVC akan tetap `Pending` menunggu PV statis yang cocok (tanpa `storageClassName`) tersedia.
4.  **Penggunaan oleh Pod:** Setelah PVC berstatus `Bound`, Pod dapat menggunakannya seperti biasa.

## Atribut Penting StorageClass (`storage.k8s.io/v1`)

```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: fast-ssd-gcp # Nama StorageClass (yg akan dirujuk oleh PVC)
  # annotations: # Tandai sebagai default (hanya boleh ada satu default per cluster)
  #   storageclass.kubernetes.io/is-default-class: "true"
provisioner: kubernetes.io/gce-pd # WAJIB: Siapa yg akan membuat volume?
                                  # (Contoh: kubernetes.io/aws-ebs, kubernetes.io/azure-disk,
                                  #          csi-driver-name.example.com)
parameters: # Opsional: Parameter spesifik untuk provisioner
  type: pd-ssd # Contoh untuk GCE: minta disk SSD
  # Contoh AWS: type: gp3, iops: "3000", throughput: "125"
  # Contoh Azure: storageaccounttype: Premium_LRS, kind: Managed
  # fsType: ext4 # Opsional: Filesystem yg akan digunakan saat provisioning
reclaimPolicy: Delete # (Default jika tdk diatur: Delete) Kebijakan untuk PV yg dibuat SC ini
                      # Pilihan: Delete, Retain. (Biasanya Delete utk dinamis)
allowVolumeExpansion: true # (Opsional) Izinkan perluasan volume setelah dibuat? (Default: false)
mountOptions: # (Opsional) Opsi mount yg akan diterapkan pada PV
  - discard
volumeBindingMode: Immediate # (Default) Kapan provisioning & binding terjadi?
                             # Immediate: Segera setelah PVC dibuat.
                             # WaitForFirstConsumer: Tunda sampai Pod pertama yg menggunakan PVC dijadwalkan.
                             # (Penting utk storage topology awareness)
# allowedTopologies: # (Opsional) Membatasi provisioning ke zona/region tertentu
# - matchLabelExpressions:
#   - key: topology.kubernetes.io/zone
#     values:
#     - us-central1-a
#     - us-central1-b
```

*   **`provisioner` (Wajib):** Menentukan plugin volume mana yang akan digunakan. Harus sesuai dengan provisioner yang tersedia di cluster Anda (baik internal maupun driver CSI).
*   **`parameters`:** Parameter buram (opaque) yang hanya dipahami oleh `provisioner` yang ditentukan. Lihat dokumentasi provisioner spesifik Anda untuk opsi yang tersedia.
*   **`reclaimPolicy`:** Mengontrol `persistentVolumeReclaimPolicy` pada PV yang dibuat secara dinamis oleh kelas ini. `Delete` adalah default dan paling umum untuk provisioning dinamis.
*   **`allowVolumeExpansion`:** Jika `true`, memungkinkan pengguna memperbesar ukuran PVC mereka nanti (jika provisioner mendukungnya).
*   **`mountOptions`:** Daftar opsi mount string yang akan ditambahkan ke PV.
*   **`volumeBindingMode`:**
    *   `Immediate`: PV dibuat dan diikat segera setelah PVC dibuat. Ini default.
    *   `WaitForFirstConsumer`: Provisioning dan binding ditunda sampai ada Pod yang benar-benar dijadwalkan yang menggunakan PVC tersebut. Ini memungkinkan Scheduler mempertimbangkan batasan topologi (seperti zona ketersediaan Node) sebelum volume dibuat, memastikan volume dibuat di tempat yang tepat untuk Pod. Sangat penting untuk volume lokal atau volume cloud zona-spesifik.

## Mengelola StorageClass dengan `kubectl`

*   **Melihat StorageClass yang tersedia:**
    ```bash
    kubectl get storageclass
    # atau
    kubectl get sc
    # Perhatikan kolom 'PROVISIONER', 'RECLAIMPOLICY', 'VOLUMEBINDINGMODE', 'ALLOWVOLUMEEXPANSION', dan apakah ada yg 'DEFAULT'.
    ```
*   **Membuat StorageClass:**
    ```bash
    kubectl apply -f my-storageclass.yaml
    ```
*   **Menandai StorageClass sebagai Default:** (Hanya boleh ada satu default)
    ```bash
    # Hapus anotasi default dari SC lama (jika ada)
    kubectl patch storageclass <nama-sc-lama> -p '{"metadata": {"annotations":{"storageclass.kubernetes.io/is-default-class":"false"}}}'

    # Tambahkan anotasi default ke SC baru
    kubectl patch storageclass <nama-sc-baru> -p '{"metadata": {"annotations":{"storageclass.kubernetes.io/is-default-class":"true"}}}'
    ```
*   **Menghapus StorageClass:**
    ```bash
    kubectl delete storageclass <nama-sc>
    # Menghapus SC TIDAK akan menghapus PV yang sudah dibuat olehnya.
    ```

StorageClass adalah komponen kunci untuk mengotomatisasi dan menyederhanakan manajemen penyimpanan persisten di Kubernetes, memungkinkan pengguna meminta penyimpanan sesuai kebutuhan tanpa intervensi manual administrator untuk setiap permintaan.
