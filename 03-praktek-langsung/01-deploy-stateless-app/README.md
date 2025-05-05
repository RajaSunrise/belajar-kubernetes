# Praktik Langsung: Deploy Aplikasi Stateless Sederhana

Contoh ini mendemonstrasikan cara men-deploy aplikasi web stateless sederhana (ditulis dengan Python Flask) ke cluster Kubernetes menggunakan objek `Deployment` dan `Service`.

Aplikasi ini hanya menampilkan pesan "Hello, Kubernetes!" dan nama host dari Pod tempat ia berjalan. Karena bersifat stateless, setiap replika Pod identik dan dapat diganti tanpa kehilangan data.

## Struktur Direktori

*   `app/main.py`: Kode sumber aplikasi Flask.
*   `Dockerfile`: Instruksi untuk membangun image container aplikasi.
*   `requirements.txt`: Daftar dependensi Python (Flask).
*   `deployment.yml`: Manifes Kubernetes untuk membuat `Deployment` yang mengelola Pods aplikasi.
*   `service.yml`: Manifes Kubernetes untuk membuat `Service` tipe `LoadBalancer` (atau `NodePort` jika LoadBalancer tidak tersedia) yang mengekspos aplikasi ke luar cluster.

## Prasyarat

*   Cluster Kubernetes yang sedang berjalan (misalnya, Minikube, Kind, Docker Desktop, atau cluster cloud).
*   `kubectl` terkonfigurasi untuk berinteraksi dengan cluster Anda.
*   Docker (atau container runtime lain) untuk membangun image (jika Anda ingin membangunnya sendiri).

## Langkah-langkah Menjalankan

1.  **(Opsional) Bangun Image Docker:**
    Jika Anda ingin membangun image sendiri (misalnya, setelah memodifikasi kode aplikasi), jalankan perintah berikut dari dalam direktori `01-deploy-stateless-app`:
    ```bash
    # Ganti 'nama-anda/hello-k8s:v1' dengan nama image yang Anda inginkan
    docker build -t nama-anda/hello-k8s:v1 .
    ```
    Jika menggunakan cluster lokal seperti Minikube atau Kind, Anda mungkin perlu memuat image ini ke dalam cluster:
    *   **Minikube:** `minikube image load nama-anda/hello-k8s:v1`
    *   **Kind:** `kind load docker-image nama-anda/hello-k8s:v1`
    *   **Penting:** Jika Anda membangun image sendiri, jangan lupa **perbarui field `spec.template.spec.containers[0].image`** di dalam file `deployment.yml` agar sesuai dengan nama image yang baru Anda bangun. Contoh ini secara default menggunakan image publik `paulbouwer/hello-kubernetes:1.10` agar bisa langsung dijalankan tanpa build.

2.  **Deploy Aplikasi ke Kubernetes:**
    Terapkan manifes Deployment dan Service:
    ```bash
    kubectl apply -f deployment.yml
    kubectl apply -f service.yml
    ```

3.  **Verifikasi Deployment:**
    *   Periksa status Deployment:
        ```bash
        kubectl get deployment hello-kubernetes
        ```
        Tunggu hingga kolom `READY` menunjukkan `3/3` (atau jumlah replika yang Anda tentukan).
    *   Periksa Pods yang dibuat:
        ```bash
        kubectl get pods -l app=hello-kubernetes
        ```
        Anda akan melihat beberapa Pod dengan nama seperti `hello-kubernetes-xxxxxxxxx-yyyyy`.

4.  **Verifikasi Service dan Akses Aplikasi:**
    *   Periksa Service:
        ```bash
        kubectl get service hello-kubernetes
        ```
    *   Cari tahu cara mengakses Service. Ini tergantung pada tipe Service (`LoadBalancer` atau `NodePort`) dan lingkungan cluster Anda:
        *   **Jika `EXTERNAL-IP` memiliki alamat IP (Tipe LoadBalancer):** Akses aplikasi melalui `http://<EXTERNAL-IP>`.
        *   **Jika `EXTERNAL-IP` masih `<pending>` (Tipe LoadBalancer di Minikube/Kind):** Gunakan perintah khusus:
            *   **Minikube:** `minikube service hello-kubernetes --url` (akan memberikan URL akses)
            *   **Kind (dengan Ingress Controller):** Anda mungkin perlu setup Ingress. Cara termudah tanpa Ingress adalah port-forward: `kubectl port-forward service/hello-kubernetes 8080:80` lalu akses `http://localhost:8080`.
        *   **Jika Tipe `NodePort`:** Dapatkan IP salah satu Node (`kubectl get nodes -o wide`) dan port Node (`kubectl get svc hello-kubernetes -o jsonpath='{.spec.ports[0].nodePort}'`). Akses melalui `http://<NODE_IP>:<NODE_PORT>`.

    Anda seharusnya melihat pesan "Hello, Kubernetes!" dan nama host Pod di browser atau output `curl`. Refresh beberapa kali, dan Anda mungkin akan melihat nama host berubah saat request Anda diarahkan ke Pod yang berbeda oleh Service.

5.  **Scaling (Opsional):**
    Naikkan jumlah replika Pod:
    ```bash
    kubectl scale deployment hello-kubernetes --replicas=5
    kubectl get pods -l app=hello-kubernetes # Verifikasi ada 5 Pods
    ```

6.  **Pembersihan:**
    Hapus Deployment dan Service:
    ```bash
    kubectl delete -f service.yml
    kubectl delete -f deployment.yml
    ```

## Konsep Kunci yang Didemonstrasikan

*   **Deployment:** Mengelola replika aplikasi stateless, menangani update dan rollback.
*   **Pod:** Unit terkecil yang dapat di-deploy, berisi container aplikasi.
*   **Service:** Menyediakan endpoint jaringan yang stabil untuk mengakses sekumpulan Pods.
*   **Labels & Selectors:** Digunakan oleh Deployment dan Service untuk mengidentifikasi dan mengelompokkan Pods.
*   **Stateless Application:** Aplikasi yang tidak menyimpan state lokal yang persisten, membuatnya mudah untuk di-scale dan diganti.
