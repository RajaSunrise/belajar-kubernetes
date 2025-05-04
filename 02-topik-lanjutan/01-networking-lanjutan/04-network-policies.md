# Network Policies: Firewall Level Pod/Namespace

Secara default, model jaringan Kubernetes bersifat **terbuka**: semua Pod dapat berkomunikasi dengan semua Pod lain di dalam cluster, terlepas dari Namespace tempat mereka berada. Meskipun sederhana, ini bisa menjadi risiko keamanan. Jika sebuah Pod berhasil diretas, penyerang dapat dengan mudah mencoba mengakses Pod atau layanan lain di seluruh cluster (gerakan lateral).

Untuk mengatasi ini dan menerapkan prinsip *least privilege* pada jaringan, Kubernetes menyediakan objek **NetworkPolicy**.

## Apa itu NetworkPolicy?

NetworkPolicy memungkinkan Anda mendefinisikan aturan firewall **di dalam cluster Kubernetes** untuk mengontrol lalu lintas jaringan pada **Layer 3 (IP Address)** dan **Layer 4 (TCP/UDP Ports)**. Anda dapat menentukan Pod mana yang diizinkan untuk berkomunikasi dengan Pod lain.

**Penting:** Agar NetworkPolicy berfungsi, Anda **harus** menggunakan **plugin jaringan (CNI)** yang **mendukung** implementasi NetworkPolicy (misalnya, Calico, Cilium, Weave Net, atau CNI cloud provider tertentu). Flannel saja tidak mendukung NetworkPolicy. Jika CNI Anda tidak mendukungnya, membuat objek NetworkPolicy tidak akan berpengaruh.

## Konsep Utama NetworkPolicy

1.  **Target Pods (`podSelector`):** Setiap NetworkPolicy berlaku untuk sekelompok Pod tertentu dalam satu Namespace, yang dipilih menggunakan `podSelector` (berdasarkan label Pod). Jika `podSelector` kosong (`{}`), kebijakan berlaku untuk *semua* Pod di Namespace tersebut.
2.  **Jenis Kebijakan (`policyTypes`):** Anda dapat menentukan apakah kebijakan mengontrol lalu lintas masuk (`Ingress`), lalu lintas keluar (`Egress`), atau keduanya. Jika `policyTypes` tidak ditentukan:
    *   Jika ada aturan `ingress`, maka hanya lalu lintas `Ingress` yang terpengaruh (egress diizinkan semua).
    *   Jika ada aturan `egress`, maka hanya lalu lintas `Egress` yang terpengaruh (ingress diizinkan semua).
    *   Jika ada aturan `ingress` dan `egress`, keduanya terpengaruh.
    *   Jika tidak ada aturan `ingress` atau `egress`, maka **tidak berpengaruh**.
3.  **Aturan Izin (`ingress` / `egress`):** Bagian `ingress` dan `egress` berisi daftar aturan yang menentukan lalu lintas apa yang **diizinkan**. Lalu lintas yang tidak cocok dengan setidaknya satu aturan akan **diblokir**.
4.  **Sumber (`from` untuk Ingress) / Tujuan (`to` untuk Egress):** Aturan menentukan sumber (untuk ingress) atau tujuan (untuk egress) lalu lintas yang diizinkan. Ini dapat berupa:
    *   `podSelector`: Memilih Pod lain (berdasarkan label) di *namespace yang sama* dengan NetworkPolicy.
    *   `namespaceSelector`: Memilih Pod di *namespace lain* (berdasarkan label namespace). Jika dikombinasikan dengan `podSelector`, itu berarti "Pods dengan label X di Namespaces dengan label Y".
    *   `ipBlock`: Menentukan rentang alamat IP CIDR (misalnya, untuk mengizinkan akses dari luar cluster atau memblokir akses ke IP eksternal tertentu).
5.  **Ports (`ports`):** Anda dapat secara opsional membatasi aturan hanya untuk port TCP atau UDP tertentu. Jika tidak ditentukan, aturan berlaku untuk semua port.

## Sifat NetworkPolicy: Default Deny (Implisit)

*   **Isolasi Default:** Pods **tidak terisolasi** secara default. Mereka dapat mengirim dan menerima traffic dari mana saja.
*   **Efek Kebijakan Pertama:** Segera setelah **setidaknya satu** NetworkPolicy (baik Ingress maupun Egress) memilih sebuah Pod:
    *   Jika kebijakan itu memiliki aturan `Ingress`, semua lalu lintas masuk ke Pod tersebut **diblokir**, *kecuali* yang secara eksplisit diizinkan oleh aturan `ingress` dalam *setiap* NetworkPolicy yang menargetkan Pod tersebut.
    *   Jika kebijakan itu memiliki aturan `Egress`, semua lalu lintas keluar dari Pod tersebut **diblokir**, *kecuali* yang secara eksplisit diizinkan oleh aturan `egress` dalam *setiap* NetworkPolicy yang menargetkan Pod tersebut.

Dengan kata lain, NetworkPolicy bekerja berdasarkan prinsip **allow-list**. Jika Anda menerapkan kebijakan, Anda harus secara eksplisit mengizinkan semua lalu lintas yang Anda inginkan.

## Contoh NetworkPolicy YAML

**Contoh 1: Default Deny All (Isolasi Penuh)**
Kebijakan ini menargetkan semua Pod di namespace dan tidak memiliki aturan `ingress` atau `egress`, secara efektif memblokir semua lalu lintas masuk dan keluar.

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny-all
  namespace: my-secure-app # Berlaku di namespace ini
spec:
  podSelector: {} # Kosong: berlaku untuk semua Pods di namespace ini
  policyTypes:
  - Ingress
  - Egress
  # Tidak ada aturan 'ingress' atau 'egress', jadi semua diblokir
```

**Contoh 2: Izinkan Ingress dari Namespace Lain dan Pod Tertentu**
Kebijakan ini diterapkan pada Pods dengan label `app=backend`.

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: backend-allow-frontend-and-monitoring
  namespace: backend-ns
spec:
  podSelector: # Targetkan Pods ini
    matchLabels:
      app: backend
  policyTypes:
  - Ingress # Hanya kontrol lalu lintas masuk
  ingress: # Aturan izin masuk
  - from: # Izinkan dari sumber berikut:
    - namespaceSelector: # Pods dari namespace mana saja yang...
        matchLabels:
          team: frontend-team # ...memiliki label 'team: frontend-team'
      podSelector: # Dan Pods di namespace itu yang...
        matchLabels:
          role: frontend # ...memiliki label 'role: frontend'
    - namespaceSelector: # ATAU Pods dari namespace mana saja yang...
        matchLabels:
          purpose: monitoring # ...memiliki label 'purpose: monitoring'
    ports: # Hanya izinkan traffic ke port berikut:
    - protocol: TCP
      port: 8080 # Port aplikasi backend
```
*Pod `app=backend` hanya bisa menerima koneksi TCP di port 8080 dari Pod `role=frontend` di namespace `team=frontend-team`, atau dari Pod mana saja di namespace `purpose=monitoring`.*

**Contoh 3: Izinkan Egress Hanya ke DNS dan API Server Internal**

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-dns-and-api-egress
  namespace: default
spec:
  podSelector: {} # Berlaku untuk semua pod di namespace 'default'
  policyTypes:
  - Egress # Hanya kontrol lalu lintas keluar
  egress:
  - to: # Izinkan tujuan berikut:
    - namespaceSelector: {} # Ke Pods di namespace mana saja... (Perlu disempurnakan!)
      podSelector: # ...yang memiliki label Kube-DNS
        matchLabels:
          k8s-app: kube-dns
    ports: # Hanya izinkan ke port DNS
    - protocol: UDP
      port: 53
    - protocol: TCP # DNS bisa juga TCP
      port: 53
  - to: # Izinkan ke API Server Kubernetes (gunakan ipBlock)
    - ipBlock:
        # Ganti ini dengan CIDR atau IP API Server Anda jika diketahui.
        # Menemukan IP API Server bisa rumit; cara yang lebih baik adalah
        # jika CNI mendukung aturan berbasis Service atau entitas K8s.
        # Untuk contoh ini, kita biarkan terbuka ke jaringan cluster (jika diketahui):
        cidr: 10.96.0.1/32 # Asumsi IP Service 'kubernetes.default'
        # PERINGATAN: Jangan gunakan 0.0.0.0/0 kecuali benar-benar diperlukan & dipahami
    ports:
    - protocol: TCP
      port: 443 # Port default API Server
  # Anda mungkin perlu menambahkan aturan egress lain untuk koneksi eksternal yang diperlukan aplikasi
```
*Kebijakan ini mengizinkan semua Pod di namespace `default` untuk mengirim traffic UDP/TCP ke port 53 (DNS) ke Pods dengan label `k8s-app=kube-dns` (biasanya CoreDNS), dan traffic TCP ke port 443 ke IP API Server Kubernetes. Semua traffic egress lainnya diblokir.*

## Strategi Penerapan NetworkPolicy

*   **Mulai dengan `default-deny`:** Terapkan kebijakan `default-deny-all` di namespace, lalu secara bertahap tambahkan kebijakan `allow` hanya untuk komunikasi yang benar-benar diperlukan. Ini adalah pendekatan paling aman (zero-trust).
*   **Gunakan Label Secara Efektif:** Kebijakan sangat bergantung pada label Pod dan Namespace. Rancang strategi pelabelan yang baik dan konsisten.
*   **Uji Coba:** Terapkan kebijakan di lingkungan non-produksi terlebih dahulu dan uji konektivitas aplikasi secara menyeluruh.
*   **Visualisasi:** Gunakan alat bantu (beberapa CNI menyediakannya, atau alat pihak ketiga) untuk memvisualisasikan aturan kebijakan dan aliran traffic yang diizinkan/diblokir.
*   **Pertimbangkan Kebijakan Egress:** Jangan hanya fokus pada ingress. Mengontrol traffic keluar (egress) juga penting untuk mencegah Pod yang terkompromi menghubungi server eksternal berbahaya atau melakukan eksfiltrasi data.

NetworkPolicy adalah alat keamanan jaringan yang sangat kuat di Kubernetes. Memanfaatkannya secara efektif dapat secara signifikan mengurangi permukaan serangan cluster Anda dan membantu menerapkan segmentasi jaringan mikro.
