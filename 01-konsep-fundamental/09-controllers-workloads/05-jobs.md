# DaemonSets: Menjalankan Pod di Setiap Node

**DaemonSet** adalah jenis controller Kubernetes yang memastikan bahwa **semua (atau sebagian) Node** dalam cluster menjalankan **satu salinan** dari Pod tertentu. Berbeda dengan Deployment atau ReplicaSet yang bertujuan menjalankan sejumlah replika *di seluruh cluster*, DaemonSet fokus pada penempatan Pod *per Node*.

## Tujuan Utama DaemonSet

DaemonSet sangat berguna untuk men-deploy **agen tingkat sistem** atau **daemon** yang perlu berjalan di setiap mesin dalam cluster untuk menyediakan fungsionalitas infrastruktur atau pemantauan.

**Kasus Penggunaan Umum:**

*   **Agen Logging:** Menjalankan kolektor log seperti Fluentd, Fluent Bit, atau Logstash di setiap Node untuk mengumpulkan log dari semua kontainer yang berjalan di Node tersebut (biasanya dengan me-mount direktori log host seperti `/var/log`).
*   **Agen Monitoring Node:** Menjalankan agen seperti Prometheus Node Exporter, Datadog Agent, atau agen APM lainnya di setiap Node untuk mengumpulkan metrik kinerja Node (CPU, memori, disk, jaringan) dan metrik sistem lainnya.
*   **Daemon Penyimpanan Cluster:** Menjalankan komponen untuk sistem penyimpanan terdistribusi seperti GlusterFS atau Ceph di setiap Node yang berpartisipasi dalam cluster penyimpanan.
*   **Plugin Jaringan (CNI):** Beberapa plugin CNI (Container Network Interface) seperti Calico atau Cilium di-deploy sebagai DaemonSet untuk mengelola jaringan di setiap Node.
*   **Node Problem Detector:** Menjalankan agen yang memantau kesehatan Node dan melaporkan masalah ke API Server.
*   **Agen Keamanan:** Menjalankan pemindai keamanan atau agen intrusi di setiap Node.

## Bagaimana DaemonSet Bekerja?

1.  **Definisi DaemonSet:** Anda membuat objek DaemonSet, yang mencakup:
    *   `spec.selector`: Label selector untuk mengidentifikasi Pods yang dikelola oleh DaemonSet ini.
    *   `spec.template`: Template Pod (seperti di Deployment) yang mendefinisikan Pod yang akan dijalankan di setiap Node. Label Pod di template *harus* cocok dengan selector.
    *   (Opsional) `spec.template.spec.nodeSelector`: Membatasi DaemonSet agar hanya berjalan di Node yang cocok dengan label tertentu.
    *   (Opsional) `spec.template.spec.affinity`: Menggunakan Node Affinity untuk aturan penempatan yang lebih kompleks.
    *   (Opsional) `spec.template.spec.tolerations`: Sangat penting jika Anda ingin Pod DaemonSet berjalan di semua jenis Node, termasuk node Control Plane yang mungkin memiliki Taints (`NoSchedule`). DaemonSet sering perlu mentolerir taints ini.
2.  **DaemonSet Controller:** Controller ini mengawasi objek DaemonSet dan Node di cluster.
3.  **Penjadwalan Pod:** Untuk setiap Node yang **memenuhi syarat** (cocok dengan `nodeSelector`/`affinity` dan Pod dapat mentolerir `Taints` Node):
    *   DaemonSet Controller akan **membuat satu Pod** berdasarkan `spec.template` di Node tersebut.
    *   **Penting:** Penjadwalan Pod DaemonSet *tidak* ditangani oleh `kube-scheduler` default. DaemonSet Controller langsung mengatur `.spec.nodeName` pada Pod yang dibuatnya. (Namun, ada fitur alpha/beta untuk menggunakan scheduler default).
4.  **Penyesuaian Otomatis:**
    *   **Node Baru Ditambahkan:** Jika Node baru ditambahkan ke cluster dan memenuhi syarat, DaemonSet Controller akan secara otomatis membuat Pod baru di Node tersebut.
    *   **Node Dihapus:** Jika Node dihapus dari cluster, Pod DaemonSet di Node tersebut akan di-garbage collected.
    *   **Label Node Berubah:** Jika label Node diubah sehingga tidak lagi memenuhi syarat (atau sebaliknya), DaemonSet Controller akan menghapus (atau menambahkan) Pod yang sesuai.
5.  **Self-Healing:** Jika Pod DaemonSet di sebuah Node gagal atau dihapus secara tidak sengaja, DaemonSet Controller akan membuat Pod pengganti *di Node yang sama*.

## Update DaemonSet

DaemonSet mendukung dua strategi update (`spec.updateStrategy.type`):

1.  **`RollingUpdate` (Default):**
    *   Mirip dengan Rolling Update pada Deployment, tetapi terjadi **per Node**.
    *   Ketika `spec.template` DaemonSet diperbarui, Pods lama di Node akan dihapus dan Pods baru (dengan template baru) akan dibuat secara terkontrol.
    *   Konfigurasi Kunci:
        *   `spec.updateStrategy.rollingUpdate.maxUnavailable`: Jumlah atau persentase maksimum Node yang Pod DaemonSet-nya boleh tidak tersedia selama update. Default 1.
        *   `spec.updateStrategy.rollingUpdate.maxSurge` (Di versi K8s lebih baru): Jumlah atau persentase Pod tambahan di atas jumlah Node. Default 0. Memungkinkan Pod baru dibuat sebelum yang lama dihapus.
    *   Prosesnya bisa node-by-node atau lebih cepat tergantung `maxUnavailable`/`maxSurge`.

2.  **`OnDelete`:**
    *   Controller tidak secara otomatis memperbarui Pods ketika `spec.template` diubah.
    *   Untuk menerapkan pembaruan, Anda perlu **menghapus Pods DaemonSet lama secara manual**. DaemonSet Controller kemudian akan membuat Pods baru menggunakan template yang baru untuk menggantikannya.
    *   Berguna jika Anda memerlukan kontrol manual penuh atas proses update per node.

## Contoh YAML DaemonSet (Agen Logging Fluentd)

```yaml
# fluentd-daemonset.yaml
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: fluentd-elasticsearch
  namespace: kube-system # Umumnya ditempatkan di kube-system
  labels:
    k8s-app: fluentd-logging
spec:
  # Selector untuk Pods yang dikelola DaemonSet
  selector:
    matchLabels:
      name: fluentd-elasticsearch
  # Template Pod
  template:
    metadata:
      labels:
        name: fluentd-elasticsearch
    spec:
      # Toleransi agar bisa berjalan di control-plane/master nodes
      tolerations:
      - key: node-role.kubernetes.io/control-plane
        operator: Exists
        effect: NoSchedule
      - key: node-role.kubernetes.io/master # Untuk kompatibilitas versi lama
        operator: Exists
        effect: NoSchedule
      containers:
      - name: fluentd-elasticsearch
        image: quay.io/fluentd_elasticsearch/fluentd:v2.5.2 # Gunakan image spesifik
        resources:
          limits:
            memory: 300Mi
          requests:
            cpu: 100m
            memory: 200Mi
        # Mount volume dari host node untuk membaca log
        volumeMounts:
        - name: varlog # Mount /var/log dari host
          mountPath: /var/log
        - name: varlibdockercontainers # Mount log kontainer Docker
          mountPath: /var/lib/docker/containers
          readOnly: true
        # Tambahkan mount lain jika menggunakan runtime containerd/CRI-O
        # - name: containerd-log
        #   mountPath: /var/log/pods
        #   readOnly: true
      terminationGracePeriodSeconds: 30
      # Definisi Volume tipe hostPath
      volumes:
      - name: varlog
        hostPath:
          path: /var/log
      - name: varlibdockercontainers
        hostPath:
          path: /var/lib/docker/containers
      # - name: containerd-log
      #   hostPath:
      #     path: /var/log/pods
  # Strategi Update (Opsional, defaultnya RollingUpdate)
  updateStrategy:
    type: RollingUpdate
    rollingUpdate:
      maxUnavailable: 1 # Hanya 1 node yg diupdate pada satu waktu
```

**Penting:** Menggunakan `hostPath` seperti dalam contoh ini memberikan akses ke filesystem Node host, yang memiliki implikasi keamanan. Pastikan Pod DaemonSet Anda (seperti agen logging) benar-benar memerlukan akses ini dan konfigurasikan izin seminimal mungkin. Gunakan `securityContext` untuk membatasi privilege jika memungkinkan.

DaemonSet adalah alat penting untuk memastikan agen atau layanan tingkat infrastruktur berjalan secara konsisten di seluruh (atau sebagian) Node dalam cluster Kubernetes Anda.
