# Topologi Penyimpanan (Storage Topology) & Penjadwalan Sadar Topologi

Dalam cluster Kubernetes yang tersebar di beberapa *domain kegagalan* (failure domains) seperti rak server, zona ketersediaan (availability zones - AZ) di cloud, atau region geografis, lokasi fisik dari penyimpanan (PersistentVolume - PV) relatif terhadap Node tempat Pod berjalan menjadi sangat penting.

**Masalah:**

*   **Storage Lokal (Local Persistent Volumes):** Beberapa PV mungkin merepresentasikan disk yang terpasang langsung ke satu Node spesifik. Pod yang menggunakan PV ini *harus* dijadwalkan ke Node tersebut.
*   **Storage Zona-Spesifik (Contoh: AWS EBS, GCE PD):** Volume penyimpanan di cloud provider seringkali terikat pada satu Availability Zone (AZ) tertentu. Sebuah Node hanya dapat me-mount volume dari AZ yang sama. Pod yang menggunakan PV dari `zone-a` harus dijadwalkan ke Node di `zone-a`.
*   **Performa:** Bahkan untuk storage jaringan (NFS, Ceph), mengakses volume dari Node yang berada di zona atau region yang sama biasanya lebih cepat daripada mengaksesnya lintas zona/region.

Jika penjadwalan Pod dan penyediaan/pemilihan PV tidak memperhitungkan topologi ini, bisa terjadi situasi di mana:

*   Pod dijadwalkan ke Node yang tidak dapat mengakses PV yang dibutuhkannya (misalnya, Pod di `zone-b` mencoba menggunakan PV EBS di `zone-a`). Akibatnya, Pod gagal memulai karena volume tidak bisa di-mount.
*   PV disediakan di zona yang salah relatif terhadap tempat Pod akhirnya dijadwalkan.

## Solusi: Penjadwalan Sadar Topologi (Topology-Aware Scheduling)

Kubernetes menyediakan mekanisme agar Scheduler dan proses penyediaan volume dapat bekerja sama untuk memastikan Pod dijadwalkan ke Node yang memiliki akses ke volume yang dibutuhkan. Kunci utama untuk ini adalah:

1.  **Informasi Topologi pada PV:** Driver CSI (atau admin untuk PV statis) dapat menambahkan **label topologi** ke objek PV. Label ini menunjukkan batasan lokasi PV (misalnya, di zona atau Node mana ia berada). Label umum adalah `topology.kubernetes.io/zone` dan `topology.kubernetes.io/region`. Node juga biasanya memiliki label ini secara otomatis (diisi oleh Kubelet atau cloud controller manager).
2.  **`volumeBindingMode` di StorageClass:** Ini adalah field **krusial** pada objek `StorageClass`. Ia mengontrol *kapan* binding PVC ke PV dan dynamic provisioning harus terjadi.
    *   **`Immediate` (Default):** Binding PVC ke PV (atau dynamic provisioning PV) terjadi **segera** setelah PVC dibuat, **tanpa** mempertimbangkan di mana Pod akan dijadwalkan. Ini bisa menyebabkan masalah topologi seperti yang dijelaskan di atas, terutama dengan dynamic provisioning untuk storage zona-spesifik.
    *   **`WaitForFirstConsumer`:** Ini adalah mode yang mengaktifkan penjadwalan sadar topologi. Binding PVC ke PV dan dynamic provisioning **ditunda** sampai sebuah **Pod yang menggunakan PVC tersebut benar-benar dibuat dan dijadwalkan** ke sebuah Node oleh Scheduler.

## Cara Kerja `volumeBindingMode: WaitForFirstConsumer`

1.  **PVC Dibuat:** User membuat PVC yang menggunakan StorageClass dengan `volumeBindingMode: WaitForFirstConsumer`. PVC masuk ke status `Pending`. Tidak ada PV yang diikat atau dibuat saat ini.
2.  **Pod Dibuat:** User membuat Pod yang merujuk pada PVC `Pending` tersebut.
3.  **Scheduler Beraksi:** Kubernetes Scheduler melihat Pod baru yang membutuhkan PVC `Pending`. Alih-alih langsung menempatkan Pod, Scheduler sekarang akan:
    *   Mempertimbangkan **semua batasan penjadwalan Pod** (resource requests, node selectors, affinity, taints/tolerations).
    *   **DAN** mempertimbangkan **batasan topologi dari PV yang tersedia** (jika menggunakan PV statis) atau **topologi yang diizinkan oleh StorageClass** (jika dynamic provisioning).
    *   Scheduler akan memilih **Node yang paling sesuai** yang memenuhi *semua* batasan Pod *dan* berada di **topologi yang valid** untuk penyediaan/pengikatan volume.
4.  **PV Dipilih/Disediakan:** Setelah Node yang cocok dipilih oleh Scheduler:
    *   **Untuk PV Statis:** PersistentVolume Controller sekarang akan mencari PV yang tersedia yang memenuhi persyaratan PVC *dan* memiliki batasan topologi yang cocok dengan Node yang dipilih. Jika ditemukan, PVC diikat ke PV tersebut.
    *   **Untuk Dynamic Provisioning:** Informasi Node yang dipilih (termasuk label topologinya) diteruskan ke External Provisioner CSI. Provisioner kemudian memanggil driver CSI untuk membuat PV baru **dengan batasan topologi yang sesuai** (misalnya, membuat volume EBS di zona yang sama dengan Node yang dipilih). Setelah PV dibuat, PVC diikat ke PV baru tersebut.
5.  **Pod Dimulai:** Setelah PVC berhasil terikat ke PV (yang sekarang dijamin berada di topologi yang benar), Kubelet di Node yang dipilih dapat melanjutkan untuk me-mount volume dan memulai kontainer Pod.

## Manfaat `WaitForFirstConsumer`

*   **Penjadwalan Pod yang Benar:** Memastikan Pod hanya dijadwalkan ke Node yang dapat mengakses volume lokal atau zona-spesifik yang dibutuhkan.
*   **Penyediaan Volume yang Tepat:** Untuk dynamic provisioning, memastikan PV dibuat di zona/region yang benar sesuai dengan tempat Pod akan berjalan.
*   **Mendukung Local Persistent Volumes:** Ini adalah mode yang *diperlukan* agar Local PV dapat berfungsi dengan benar, karena Scheduler perlu tahu Node mana yang dituju sebelum PV dapat diikat.

## Kapan Menggunakan `WaitForFirstConsumer`?

Anda **harus** menggunakan `volumeBindingMode: WaitForFirstConsumer` di StorageClass Anda jika:

*   Anda menggunakan **Local Persistent Volumes**.
*   Anda menggunakan **penyimpanan cloud provider yang bersifat zona-spesifik** (seperti AWS EBS, GCE Persistent Disk, Azure Disk) dan ingin memastikan PV dibuat di zona yang sama dengan Node tempat Pod akan berjalan.
*   Anda memiliki persyaratan topologi penyimpanan lain yang perlu dipertimbangkan oleh Scheduler.

Jika Anda menggunakan penyimpanan jaringan yang dapat diakses dari semua Node (seperti NFS atau CephFS yang di-mount di semua Node), mode `Immediate` mungkin sudah cukup (walaupun `WaitForFirstConsumer` umumnya tidak berbahaya dan bisa memberikan fleksibilitas lebih).

## Contoh StorageClass dengan `WaitForFirstConsumer`

```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: ebs-gp3-wait
provisioner: ebs.csi.aws.com
parameters:
  type: gp3
  fsType: ext4
# --- Kunci Utama ---
volumeBindingMode: WaitForFirstConsumer
# --------------------
reclaimPolicy: Delete
allowVolumeExpansion: true
# (Opsional) Tentukan topologi yang diizinkan jika perlu lebih spesifik
# allowedTopologies:
# - matchLabelExpressions:
#   - key: topology.kubernetes.io/zone
#     values:
#       - us-east-1a
#       - us-east-1b
```

Dengan menggunakan `WaitForFirstConsumer`, Anda memungkinkan Kubernetes membuat keputusan penjadwalan dan penyediaan volume yang lebih cerdas dengan mempertimbangkan batasan lokasi fisik dari penyimpanan dan node.
