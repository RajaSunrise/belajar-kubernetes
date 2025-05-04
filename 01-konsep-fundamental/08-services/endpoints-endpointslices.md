# Endpoints dan EndpointSlices: Pelacakan Backend Service

Kita tahu bahwa `Service` menyediakan IP virtual (ClusterIP) yang stabil dan melakukan load balance ke sekumpulan Pods backend. Tapi, bagaimana Service (atau lebih tepatnya, mekanisme di baliknya seperti `kube-proxy`) tahu **alamat IP dan port mana saja** dari Pods yang menjadi targetnya, terutama karena Pods bisa dibuat, dihapus, atau menjadi tidak siap kapan saja?

Jawabannya terletak pada objek **Endpoints** dan **EndpointSlices**.

## Objek Endpoints (Mekanisme Lama)

*   **Definisi:** Secara historis, untuk setiap objek `Service` yang memiliki `selector`, Kubernetes Control Plane (khususnya Endpoint Controller) secara otomatis membuat objek `Endpoints` dengan **nama yang sama** dan di **namespace yang sama** dengan Service tersebut.
*   **Isi:** Objek `Endpoints` berisi daftar (dalam `subsets`) dari:
    *   Alamat IP (`addresses`) dari Pods yang **cocok dengan `selector` Service** DAN saat ini berada dalam keadaan **`Ready`** (lulus `readinessProbe`).
    *   Informasi Port (`ports`) yang relevan (port dan protokol yang diekspos oleh Pods tersebut yang sesuai dengan `targetPort` Service).
    *   Informasi tentang Pods yang cocok dengan selector tetapi **belum `Ready`** (`notReadyAddresses`).
*   **Pembaruan:** Endpoint Controller terus menerus mengawasi Pods dan Services. Setiap kali ada perubahan (Pod dibuat/dihapus, Pod menjadi Ready/NotReady, label Pod berubah, selector Service berubah), Endpoint Controller akan memperbarui objek `Endpoints` yang relevan.
*   **Penggunaan:** `kube-proxy` (dan komponen lain seperti Ingress controllers atau CoreDNS untuk beberapa konfigurasi) mengawasi perubahan pada objek `Endpoints` untuk mengetahui daftar backend yang valid untuk setiap Service.

**Contoh Melihat Objek Endpoints:**
Jika Anda memiliki Service bernama `my-service`, Anda bisa melihat Endpoints terkait:
```bash
kubectl get endpoints my-service -o yaml
# Output (Contoh):
# apiVersion: v1
# kind: Endpoints
# metadata:
#   name: my-service
#   namespace: default
#   # ... label, anotasi, dll ...
# subsets:
# - addresses: # Pods yang Ready
#   - ip: 10.1.0.5
#     targetRef: # Referensi ke Pod
#       kind: Pod
#       name: my-pod-abcde
#       namespace: default
#       uid: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
#   - ip: 10.1.1.7
#     targetRef:
#       kind: Pod
#       name: my-pod-fghij
#       namespace: default
#       uid: yyyyyyyy-yyyy-yyyy-yyyy-yyyyyyyyyyyy
#   notReadyAddresses: [] # Pods yang Not Ready (kosong dlm contoh ini)
#   ports:
#   - name: http
#     port: 8080 # targetPort dari Service/Pod
#     protocol: TCP
```

## Masalah Skalabilitas dengan Endpoints

Meskipun Endpoints berfungsi dengan baik untuk jumlah backend yang moderat, ia memiliki **masalah skalabilitas** yang signifikan:

*   **Satu Objek Besar:** Seluruh daftar IP dan port untuk *semua* Pods backend sebuah Service disimpan dalam *satu* objek `Endpoints`.
*   **Update Mahal:** Jika *satu saja* Pod ditambahkan, dihapus, atau berubah status kesiapannya, *seluruh* objek `Endpoints` yang besar itu harus diperbarui dan dikirimkan ke semua komponen yang mengawasinya (seperti `kube-proxy` di setiap Node).
*   **Batas Ukuran:** Objek `Endpoints` memiliki batas ukuran (sekitar 1MB secara default di etcd), yang membatasi jumlah endpoint yang dapat ditampung oleh satu Service (biasanya beberapa ribu).

Untuk Service dengan ribuan atau puluhan ribu Pods backend (misalnya, di cluster skala sangat besar), pembaruan objek `Endpoints` yang konstan ini dapat membebani Control Plane (API Server, etcd) dan jaringan cluster, serta memperlambat propagasi perubahan.

## Solusi: EndpointSlices (Mekanisme Baru & Direkomendasikan)

Untuk mengatasi masalah skalabilitas Endpoints, Kubernetes memperkenalkan objek **EndpointSlice** (menjadi default di versi K8s yang lebih baru, sekitar 1.21+).

*   **Definisi:** Alih-alih satu objek Endpoints besar per Service, EndpointSlice Controller **membagi** endpoint untuk sebuah Service menjadi beberapa objek `EndpointSlice` yang **lebih kecil dan lebih mudah dikelola**.
*   **Cara Kerja:**
    *   EndpointSlice Controller tetap mengawasi Pods dan Services.
    *   Ketika endpoint perlu diperbarui, hanya objek `EndpointSlice` yang relevan (yang berisi endpoint yang berubah) yang perlu diperbarui.
    *   Secara default, setiap `EndpointSlice` menampung hingga 100 endpoint, tetapi ini dapat dikonfigurasi.
    *   EndpointSlices dikelola oleh Kubernetes dan secara otomatis dibuat untuk Service (jika fitur diaktifkan).
*   **Keuntungan:**
    *   **Lebih Scalable:** Pembaruan jauh lebih efisien karena hanya sebagian kecil data yang perlu ditransfer saat ada perubahan. Mengurangi beban pada Control Plane dan jaringan.
    *   **Lebih Fleksibel:** Memungkinkan penambahan informasi tambahan per endpoint, seperti topologi (zona, region).
    *   **Mendukung Dual-Stack:** Dirancang dengan dukungan yang lebih baik untuk IPv4 dan IPv6.
*   **Hubungan:** Sebuah Service dapat memiliki *beberapa* EndpointSlices yang terkait dengannya (melalui label `kubernetes.io/service-name`). Komponen seperti `kube-proxy` sekarang mengawasi EndpointSlices alih-alih (atau selain) Endpoints.

**Contoh Melihat Objek EndpointSlice:**
```bash
# Lihat EndpointSlices untuk Service 'my-service'
kubectl get endpointslices -l kubernetes.io/service-name=my-service -o yaml
# Output (Contoh - mungkin ada beberapa slice):
# apiVersion: discovery.k8s.io/v1
# kind: EndpointSlice
# metadata:
#   name: my-service-abc12 # Nama slice unik
#   namespace: default
#   labels:
#     kubernetes.io/service-name: my-service # Menghubungkan ke Service
#     endpointslice.kubernetes.io/managed-by: endpointslice-controller.k8s.io
# addressType: IPv4 # Tipe alamat (bisa IPv6)
# endpoints:
# - addresses:
#   - "10.1.0.5" # Hanya daftar IP
#   conditions:
#     ready: true # Status kesiapan endpoint ini
#     serving: true
#     terminating: false
#   targetRef: # Referensi ke Pod
#     kind: Pod
#     name: my-pod-abcde
#     namespace: default
#     uid: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
#   zone: us-west-2a # Informasi topologi (contoh)
# - addresses:
#   - "10.1.1.7"
#   conditions:
#     ready: true
#     serving: true
#     terminating: false
#   targetRef:
#     kind: Pod
#     name: my-pod-fghij
#     namespace: default
#     uid: yyyyyyyy-yyyy-yyyy-yyyy-yyyyyyyyyyyy
#   zone: us-west-2b
# ports:
# - name: http
#   port: 8080
#   protocol: TCP
# ---
# (Mungkin ada EndpointSlice lain jika endpoint > 100)
```

## Mana yang Digunakan?

*   Di versi Kubernetes modern (1.21+), **EndpointSlices adalah mekanisme default dan direkomendasikan** karena skalabilitasnya.
*   `kube-proxy` dan komponen lain yang lebih baru akan mengkonsumsi EndpointSlices.
*   Objek `Endpoints` mungkin masih dibuat untuk kompatibilitas mundur dengan alat atau controller lama yang belum mendukung EndpointSlices.
*   Anda tidak perlu mengelola Endpoints atau EndpointSlices secara manual; mereka dibuat dan diperbarui secara otomatis oleh Kubernetes berdasarkan Service dan Pods Anda.

Memahami bahwa Service mengandalkan Endpoints/EndpointSlices untuk menemukan backend Pods yang `Ready` membantu menjelaskan mengapa `readinessProbe` sangat penting dan bagaimana Service dapat beradaptasi dengan perubahan dinamis dalam Pods di belakangnya.
