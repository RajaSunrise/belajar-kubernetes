# Security Contexts: Mengontrol Privilege Pod dan Kontainer

Secara default, kontainer di Kubernetes berjalan dengan beberapa tingkat isolasi, tetapi mereka mungkin masih mewarisi beberapa privilege dari Node host atau berjalan sebagai user `root` di dalam kontainer. Ini bisa menjadi risiko keamanan. Jika seorang penyerang berhasil mendapatkan eksekusi kode di dalam kontainer, mereka mungkin dapat menggunakan privilege tersebut untuk melarikan diri dari kontainer atau mempengaruhi Node host atau kontainer lain.

**Security Context** adalah field dalam spesifikasi Pod (`spec.securityContext`) dan spesifikasi Kontainer (`spec.containers[].securityContext`) yang memungkinkan Anda mendefinisikan **pengaturan privilege dan kontrol akses** secara lebih granular untuk Pod atau kontainer individual.

Dengan Security Context, Anda dapat mengontrol aspek-aspek seperti:

*   User ID (UID) dan Group ID (GID) yang digunakan untuk menjalankan proses di dalam kontainer.
*   Apakah kontainer diizinkan untuk meningkatkan privilege (privilege escalation).
*   Linux Capabilities yang dimiliki oleh proses kontainer.
*   Apakah root filesystem bersifat read-only.
*   Pengaturan keamanan Linux spesifik seperti SELinux, AppArmor, dan Seccomp.

## Level Penerapan Security Context

Security Context dapat diterapkan pada dua level:

1.  **Level Pod (`spec.securityContext`):**
    *   Pengaturan di sini berlaku untuk **semua kontainer** di dalam Pod tersebut.
    *   Pengaturan yang umum di level Pod meliputi:
        *   `runAsUser`: Menjalankan *semua* proses di *semua* kontainer sebagai UID ini.
        *   `runAsGroup`: Menjalankan *semua* proses di *semua* kontainer dengan GID utama ini.
        *   `runAsNonRoot`: Jika `true`, Kubelet akan memvalidasi bahwa image tidak berjalan sebagai root (UID 0) dan menolak memulai Pod jika berjalan sebagai root.
        *   `fsGroup`: GID khusus yang akan menjadi pemilik *volume* Pod (jika volume mendukung perubahan kepemilikan) dan akan ditambahkan ke GID tambahan dari semua proses di Pod. Berguna untuk akses volume bersama.
        *   `supplementalGroups`: Daftar GID tambahan yang akan ditambahkan ke semua proses.
        *   `seLinuxOptions`, `seccompProfile`, `appArmorProfile`: Mengkonfigurasi profil keamanan Linux pada level Pod.
        *   `sysctls`: Memungkinkan pengaturan parameter kernel namespaced yang aman.

2.  **Level Kontainer (`spec.containers[].securityContext`):**
    *   Pengaturan di sini berlaku **hanya untuk kontainer spesifik** tersebut.
    *   Pengaturan ini **meng-override** pengaturan yang sama jika juga didefinisikan pada level Pod.
    *   Pengaturan yang umum di level Kontainer meliputi:
        *   `runAsUser`, `runAsGroup`, `runAsNonRoot`: Sama seperti level Pod, tetapi hanya untuk kontainer ini.
        *   `allowPrivilegeEscalation`: Boolean (default `true`). Jika disetel `false`, mencegah proses mendapatkan privilege lebih dari parent-nya (misalnya via `setuid` atau `setgid` binaries). Sangat direkomendasikan untuk disetel `false`.
        *   `capabilities`: Mengontrol Linux Capabilities. Praktik terbaik adalah:
            *   `drop: ["ALL"]`: Menghapus *semua* capabilities default.
            *   `add: ["NET_BIND_SERVICE", ... ]`: Menambahkan kembali *hanya* capabilities spesifik yang benar-benar diperlukan oleh aplikasi (misalnya, `NET_BIND_SERVICE` untuk binding ke port < 1024 sebagai non-root).
        *   `privileged`: Boolean (default `false`). Jika `true`, memberikan kontainer akses hampir penuh ke semua perangkat di host dan menonaktifkan banyak mekanisme keamanan. **Sangat berbahaya, hindari sebisa mungkin!**
        *   `readOnlyRootFilesystem`: Boolean (default `false`). Jika `true`, membuat filesystem root kontainer menjadi read-only. Meningkatkan keamanan dengan mencegah modifikasi binary atau konfigurasi sistem di dalam kontainer. Aplikasi perlu menulis ke volume (misalnya, `/tmp` sebagai `emptyDir`) untuk data sementara.
        *   `seLinuxOptions`, `seccompProfile`, `appArmorProfile`: Mengkonfigurasi profil keamanan Linux spesifik untuk kontainer ini.

## Contoh YAML

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: secure-pod-example
spec:
  # --- Pengaturan Level Pod ---
  securityContext:
    runAsUser: 1001        # Jalankan semua kontainer sebagai UID 1001
    runAsGroup: 3000       # Jalankan semua kontainer dengan GID utama 3000
    runAsNonRoot: true     # Pastikan tidak ada kontainer berjalan sebagai root
    fsGroup: 2000          # Volume akan dimiliki oleh GID 2000
    # seccompProfile:      # Contoh profil seccomp
    #  type: RuntimeDefault # Gunakan profil default dari container runtime

  containers:
  - name: main-app
    image: my-secure-app:1.0
    # Tidak ada securityContext di sini, jadi mewarisi dari Pod level
    volumeMounts:
      - name: app-data
        mountPath: /data
      - name: tmp-storage
        mountPath: /tmp

  - name: sidecar-needing-caps
    image: my-sidecar:1.0
    # --- Pengaturan Level Kontainer (override Pod level jika ada) ---
    securityContext:
      # runAsUser: 1002 # Bisa override UID jika perlu
      allowPrivilegeEscalation: false # Sangat direkomendasikan
      readOnlyRootFilesystem: true    # Praktik baik
      capabilities:
        drop: # Hapus semua capabilities
        - "ALL"
        add: # Tambahkan hanya yang diperlukan
        - "NET_BIND_SERVICE" # Contoh jika perlu bind port < 1024
        # - "SYS_TIME"      # Contoh lain
    volumeMounts: # Sidecar ini juga butuh /tmp untuk menulis
      - name: tmp-storage
        mountPath: /tmp

  volumes:
  - name: app-data
    persistentVolumeClaim:
      claimName: my-app-pvc
  - name: tmp-storage # Gunakan emptyDir untuk data sementara jika rootfs read-only
    emptyDir: {}
```

## Mengapa Menggunakan Security Contexts?

*   **Mengurangi Permukaan Serangan:** Membatasi privilege yang dimiliki proses jika kontainer terkompromi.
*   **Prinsip Hak Akses Minimum:** Memberikan hanya izin dan kemampuan yang benar-benar diperlukan oleh aplikasi.
*   **Mematuhi Standar Keamanan:** Membantu memenuhi persyaratan keamanan organisasi atau standar industri.
*   **Mencegah Eskalasi Privilege:** Menghentikan penyerang agar tidak dapat meningkatkan hak akses mereka di dalam atau di luar kontainer.

## Praktik Terbaik

1.  **Jalankan sebagai Non-Root:** Selalu usahakan untuk menjalankan kontainer Anda sebagai pengguna non-root (`runAsNonRoot: true`, tentukan `runAsUser` > 0). Desain Dockerfile Anda untuk mendukung ini.
2.  **Nonaktifkan Eskalasi Privilege:** Set `allowPrivilegeEscalation: false` kecuali ada alasan kuat untuk tidak melakukannya.
3.  **Minimalkan Capabilities:** Hapus semua capabilities (`drop: ["ALL"]`) dan tambahkan kembali hanya yang *mutlak diperlukan*.
4.  **Gunakan Read-Only Root Filesystem:** Set `readOnlyRootFilesystem: true` jika memungkinkan, dan gunakan volume (`emptyDir` atau PV/PVC) untuk path yang memerlukan penulisan.
5.  **Hindari `privileged: true`:** Hanya gunakan ini jika benar-benar tidak ada alternatif lain dan Anda memahami risikonya (biasanya hanya untuk agen sistem tingkat sangat rendah).
6.  **Manfaatkan Seccomp, AppArmor, SELinux:** Jika lingkungan Anda mendukungnya, gunakan profil keamanan ini untuk lebih membatasi panggilan sistem (syscalls) dan akses file yang diizinkan.

Security Context adalah alat penting dalam toolkit keamanan Kubernetes Anda. Mengkonfigurasikannya dengan benar adalah langkah vital dalam mengeraskan (hardening) beban kerja Anda. Kebijakan keamanan cluster (seperti Pod Security Admission) seringkali memberlakukan beberapa pengaturan Security Context ini secara otomatis.
