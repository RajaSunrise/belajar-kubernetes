# Tips & Trik `kubectl` untuk Power User

`kubectl` adalah alat utama Anda untuk berinteraksi dengan Kubernetes. Meskipun perintah dasar seperti `get`, `describe`, `apply`, dan `delete` sangat penting, ada banyak fitur dan trik lain yang dapat secara signifikan meningkatkan produktivitas dan efisiensi Anda saat bekerja dengan Kubernetes. Menjadi "power user" `kubectl` berarti mengetahui cara memanfaatkan fitur-fitur ini.

## 1. Kustomisasi Output (`-o` atau `--output`)

Secara default, `kubectl get` menampilkan output tabel yang ringkas. Flag `-o` memungkinkan Anda mengontrol format output secara presisi:

*   **`-o wide`**: Menampilkan informasi tambahan dalam output tabel (misalnya, IP Pod, Node tempat Pod berjalan). Sangat berguna!
    ```bash
    kubectl get pods -o wide
    kubectl get nodes -o wide
    ```
*   **`-o yaml`**: Menampilkan definisi objek lengkap dalam format YAML. Berguna untuk melihat semua field atau menyimpan definisi objek.
    ```bash
    kubectl get deployment my-app -o yaml
    kubectl get pod my-pod-xyz -o yaml > my-pod-backup.yaml
    ```
*   **`-o json`**: Menampilkan definisi objek lengkap dalam format JSON.
    ```bash
    kubectl get service my-service -o json
    ```
*   **`-o jsonpath='<template>'`**: Memungkinkan Anda mengekstrak nilai spesifik dari output JSON menggunakan ekspresi [JSONPath](https://kubernetes.io/docs/reference/kubectl/jsonpath/). Sangat kuat untuk scripting dan otomatisasi.
    ```bash
    # Dapatkan IP semua Pods di namespace default
    kubectl get pods -o jsonpath='{.items[*].status.podIP}'

    # Dapatkan nama kontainer pertama dari sebuah Pod
    kubectl get pod my-pod-xyz -o jsonpath='{.spec.containers[0].name}'

    # Dapatkan semua image kontainer dari semua Pods
    kubectl get pods -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{range .spec.containers[*]}{.image}{" "}{end}{"\n"}{end}'

    # Dapatkan nilai spesifik dari Secret (data sudah base64 decoded)
    kubectl get secret my-secret -o jsonpath='{.data.password}' | base64 --decode
    ```
*   **`-o custom-columns=<HEADER>:<jsonpath>,<HEADER>:<jsonpath>,...`**: Membuat output tabel kustom dengan kolom dan data yang Anda tentukan menggunakan JSONPath.
    ```bash
    # Tampilkan Nama Pod, Status, dan Node
    kubectl get pods -o custom-columns=NAME:.metadata.name,STATUS:.status.phase,NODE:.spec.nodeName

    # Tampilkan Nama Deployment dan Image Kontainer pertama
    kubectl get deployments -o custom-columns=DEPLOYMENT:.metadata.name,IMAGE:.spec.template.spec.containers[0].image
    ```
*   **`-o name`**: Hanya menampilkan `type/name` dari resource (misalnya, `pod/mypod-123`). Berguna untuk di-pipe ke perintah lain.
    ```bash
    kubectl get pods -l app=my-app -o name | xargs kubectl delete
    ```

## 2. Menggunakan `--selector` (`-l`) Secara Efektif

Flag `-l` memungkinkan Anda memfilter objek berdasarkan label.

*   **Kecocokan Eksak:** `-l key1=value1,key2=value2` (Logika AND).
*   **Ketidakcocokan:** `-l key1!=value1`.
*   **Berbasis Set:**
    *   `-l 'key in (value1, value2)'`
    *   `-l 'key notin (value1, value2)'`
    *   `-l key` (Label `key` harus ada, nilai apa saja).
    *   `-l '!key'` (Label `key` tidak boleh ada).

```bash
# Dapatkan semua pods di env production kecuali yang di tier frontend
kubectl get pods -l environment=production,tier!=frontend

# Dapatkan semua pods yang memiliki label 'app'
kubectl get pods -l app
```

## 3. `kubectl explain`

Alat dokumentasi bawaan yang sangat berguna untuk memahami struktur dan field objek API Kubernetes.

```bash
# Jelaskan objek Deployment
kubectl explain deployment

# Jelaskan field 'spec' dari Deployment
kubectl explain deployment.spec

# Jelaskan field 'strategy' di dalam 'spec' Deployment
kubectl explain deployment.spec.strategy

# Jelaskan secara rekursif (semua field di bawahnya)
kubectl explain deployment --recursive
```

## 4. Alias Shell

Membuat alias di lingkungan shell Anda (`.bashrc`, `.zshrc`) dapat sangat mempercepat pengetikan perintah `kubectl`.

```bash
# Contoh alias umum
alias k='kubectl'
alias kg='kubectl get'
alias kd='kubectl describe'
alias ka='kubectl apply -f'
alias kdel='kubectl delete'
alias klogs='kubectl logs'
alias kexec='kubectl exec -it'
alias kctx='kubectl config use-context'
alias kns='kubectl config set-context --current --namespace'

# Penggunaan:
# k get pods -n my-ns
# kd service my-svc
# ka my-manifest.yaml
# klogs -f my-pod-xyz
# kexec my-pod-xyz -- /bin/sh
# kns production
```

## 5. `kubectl exec`

Menjalankan perintah di dalam kontainer yang sedang berjalan.

```bash
# Dapatkan shell interaktif di kontainer
kubectl exec -it <pod-name> -- /bin/sh # atau /bin/bash

# Jalankan perintah non-interaktif
kubectl exec <pod-name> -- ls /app

# Jalankan di kontainer spesifik jika Pod punya >1 kontainer
kubectl exec -it <pod-name> -c <container-name> -- /bin/bash
```

## 6. `kubectl logs`

Melihat log `stdout`/`stderr` kontainer.

```bash
# Lihat log Pod
kubectl logs <pod-name>

# Lihat log kontainer spesifik
kubectl logs <pod-name> -c <container-name>

# Streaming log secara real-time
kubectl logs -f <pod-name>

# Lihat log dari instans kontainer sebelumnya (jika crash & restart)
kubectl logs --previous <pod-name>

# Tampilkan N baris terakhir
kubectl logs --tail=50 <pod-name>

# Tampilkan log sejak waktu tertentu (RFC3339 atau durasi)
kubectl logs --since=1h <pod-name>
kubectl logs --since-time='2023-10-27T10:00:00Z' <pod-name>
```

## 7. `kubectl port-forward`

Meneruskan koneksi dari port lokal Anda ke port pada Pod atau Service di dalam cluster. Sangat berguna untuk debugging atau akses sementara.

```bash
# Teruskan port lokal 8080 ke port 80 pada Pod 'my-pod'
kubectl port-forward pod/my-pod 8080:80

# Teruskan port lokal 9090 ke port 9090 pada Service 'my-service'
# (akan memilih satu Pod di belakang service)
kubectl port-forward service/my-service 9090:9090

# Teruskan ke port pada Deployment (akan memilih satu Pod)
kubectl port-forward deployment/my-deployment 5000:5000

# Dengarkan di semua interface lokal (hati-hati!)
# kubectl port-forward service/my-service --address 0.0.0.0 8080:80
```

## 8. `kubectl diff`

Membandingkan konfigurasi yang akan Anda terapkan (`kubectl apply -f file.yaml`) dengan konfigurasi yang saat ini ada di cluster, *tanpa* benar-benar menerapkannya. Sangat berguna untuk melihat perubahan apa yang akan terjadi.

```bash
# Lihat perbedaan antara file lokal dan state di cluster
kubectl diff -f my-updated-deployment.yaml
```

## 9. `kubectl debug` (Fitur Lebih Baru)

Menyediakan cara untuk men-debug beban kerja yang sedang berjalan dengan membuat Pod sementara (ephemeral container) atau menyalin Pod dengan konfigurasi yang diubah.

*   **Ephemeral Containers (Beta):** Menambahkan kontainer debug sementara ke Pod yang *sedang berjalan* tanpa me-restartnya. Berguna untuk menginstal alat debug (seperti `tcpdump`, `strace`) yang tidak ada di image asli.
    ```bash
    # Tambahkan kontainer 'debugger' dengan image 'busybox' ke pod 'my-pod'
    # dan langsung dapatkan shell di dalamnya.
    kubectl debug -it my-pod --image=busybox --target=main-container --share-processes # Contoh
    ```
*   **Menyalin Pod:** Membuat salinan Pod dengan modifikasi (misalnya, mengganti image, mengganti command) untuk debugging.
    ```bash
    # Buat salinan 'my-pod' bernama 'my-pod-debug', ganti imagenya, dan dapatkan shell
    kubectl debug my-pod -it --copy-to=my-pod-debug --set-image=main=ubuntu -- /bin/bash
    ```

## 10. Plugin `kubectl` dengan `krew`

`krew` adalah manajer plugin untuk `kubectl`. Ini memungkinkan Anda menemukan, menginstal, dan mengelola plugin `kubectl` yang dibuat oleh komunitas untuk memperluas fungsionalitas `kubectl`.

1.  **Instal Krew:** Ikuti [petunjuk instalasi Krew](https://krew.sigs.k8s.io/docs/user-guide/setup/install/).
2.  **Gunakan Krew:**
    ```bash
    # Update indeks plugin
    kubectl krew update

    # Cari plugin (misal: untuk melihat namespace)
    kubectl krew search ns

    # Instal plugin (misal: 'ns')
    kubectl krew install ns

    # Gunakan plugin yang terinstal
    kubectl ns # Plugin untuk beralih namespace dengan cepat

    # Lihat plugin terinstal
    kubectl krew list

    # Upgrade plugin
    kubectl krew upgrade
    ```
    Beberapa plugin populer: `ns`, `ctx` (alih konteks), `view-utilization`, `tree`, `get-all`.

## 11. Menunggu Kondisi (`--wait`)

Beberapa perintah `kubectl` mendukung flag `--wait` untuk menunggu kondisi tertentu terpenuhi sebelum kembali.

```bash
# Tunggu sampai deployment selesai rollout
kubectl rollout status deployment/my-deployment --wait

# Tunggu sampai pod dihapus (dengan timeout)
kubectl delete pod my-pod --wait --timeout=60s

# Tunggu sampai CRD terbentuk
kubectl wait --for=condition=established crd/mycrds.example.com --timeout=60s
```

Menguasai berbagai opsi dan fitur `kubectl` ini akan membuat interaksi Anda dengan Kubernetes jauh lebih cepat, efisien, dan informatif. Luangkan waktu untuk bereksperimen dengan opsi output, selector, `explain`, alias, dan plugin `krew`.
