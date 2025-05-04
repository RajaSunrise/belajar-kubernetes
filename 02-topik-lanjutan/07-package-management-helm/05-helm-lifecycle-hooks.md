# Helm Lifecycle Hooks: Menjalankan Aksi Selama Siklus Hidup Release

Terkadang, saat menginstal, meng-upgrade, atau menghapus sebuah Helm Release, Anda perlu melakukan tindakan tambahan di luar sekadar menerapkan manifest Kubernetes biasa. Contohnya:

*   Menjalankan Job Kubernetes untuk melakukan migrasi database *sebelum* Deployment aplikasi utama di-upgrade.
*   Menjalankan Pod untuk melakukan pemeriksaan kesehatan (health check) *setelah* semua sumber daya upgrade selesai dibuat.
*   Membersihkan sumber daya eksternal (misalnya, data di S3) *sebelum* menghapus (uninstall) Release.
*   Membuat Secret secara dinamis *saat* instalasi.

Untuk kasus penggunaan ini, Helm menyediakan mekanisme **Lifecycle Hooks**.

## Apa itu Hook?

Hook adalah **objek Kubernetes biasa** (seperti Job, Pod, ConfigMap, Secret) yang didefinisikan di dalam direktori `templates/` sebuah Chart, tetapi dengan **anotasi khusus** (`helm.sh/hook`) yang memberitahu Helm kapan harus menjalankan (menerapkan) objek tersebut selama siklus hidup sebuah Release.

**Penting:** Sumber daya Hook **tidak dikelola** sebagai bagian dari Release itu sendiri. Artinya:
*   Setelah Hook berhasil dijalankan, Helm tidak melacak atau mengelolanya lagi (kecuali jika ada anotasi `helm.sh/hook-delete-policy`).
*   Jika Anda menjalankan `helm upgrade`, Hook dari revisi *sebelumnya* tidak akan dihapus secara otomatis.
*   Menghapus Release (`helm uninstall`) *tidak* secara otomatis menghapus sumber daya Hook yang dibuat oleh Hook instalasi/upgrade sebelumnya (lagi-lagi, kecuali dikonfigurasi dengan delete policy).

## Hook yang Tersedia

Helm mendefinisikan beberapa titik (hooks) dalam siklus hidup di mana Anda dapat menjalankan aksi:

**Saat Instalasi (`helm install`):**

*   **`pre-install`**: Dijalankan *setelah* template dirender, tetapi *sebelum* sumber daya Chart utama dibuat di Kubernetes. Berguna untuk tugas persiapan.
*   **`post-install`**: Dijalankan *setelah* semua sumber daya Chart utama berhasil dibuat di Kubernetes. Berguna untuk tugas verifikasi atau inisialisasi pasca-instalasi.

**Saat Upgrade (`helm upgrade`):**

*   **`pre-upgrade`**: Dijalankan *setelah* template dirender, tetapi *sebelum* sumber daya Chart di-upgrade. Berguna untuk tugas persiapan sebelum upgrade (misalnya, backup database).
*   **`post-upgrade`**: Dijalankan *setelah* semua sumber daya Chart berhasil di-upgrade. Berguna untuk tugas verifikasi atau migrasi data pasca-upgrade.

**Saat Rollback (`helm rollback`):**

*   **`pre-rollback`**: Dijalankan *setelah* template untuk revisi target dirender, tetapi *sebelum* sumber daya benar-benar dikembalikan (rolled back).
*   **`post-rollback`**: Dijalankan *setelah* semua sumber daya berhasil dikembalikan ke revisi target.

**Saat Penghapusan (`helm uninstall`):**

*   **`pre-delete`**: Dijalankan *sebelum* sumber daya apa pun dari Release dihapus dari Kubernetes. Berguna untuk melakukan pembersihan atau de-registrasi sebelum penghapusan.
*   **`post-delete`**: Dijalankan *setelah* semua sumber daya dari Release berhasil dihapus. Berguna untuk konfirmasi akhir atau pembersihan sumber daya eksternal.

**Hook Pengujian (`helm test`):**

*   **`test` (atau `test-success`, `test-failure` - deprecated):** Dijalankan hanya ketika pengguna secara eksplisit menjalankan `helm test <release-name>`. Biasanya berupa Pod atau Job yang melakukan pengujian fungsional atau integrasi pada aplikasi yang sudah terinstal.

## Mendefinisikan Hook

Anda mendefinisikan Hook dengan menambahkan anotasi `helm.sh/hook` ke metadata objek Kubernetes di dalam file template Anda.

```yaml
# templates/my-pre-install-job.yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: "{{ .Release.Name }}-db-migration"
  namespace: {{ .Release.Namespace }}
  labels:
    app.kubernetes.io/managed-by: {{ .Release.Service | quote }}
    app.kubernetes.io/instance: {{ .Release.Name | quote }}
    helm.sh/chart: "{{ .Chart.Name }}-{{ .Chart.Version }}"
  annotations:
    # --- Anotasi Hook ---
    "helm.sh/hook": pre-install,pre-upgrade # Jalankan sebelum install & upgrade
    "helm.sh/hook-weight": "-5" # Urutan eksekusi (lebih kecil dijalankan dulu)
    "helm.sh/hook-delete-policy": before-hook-creation,hook-succeeded # Kapan hook dihapus
spec:
  template:
    metadata:
      name: "{{ .Release.Name }}-db-migration"
      labels:
        app.kubernetes.io/managed-by: {{ .Release.Service | quote }}
        app.kubernetes.io/instance: {{ .Release.Name | quote }}
        helm.sh/chart: "{{ .Chart.Name }}-{{ .Chart.Version }}"
    spec:
      restartPolicy: Never
      containers:
      - name: migration-runner
        image: "my-migration-tool:latest"
        # ... args, env, volumeMounts untuk menjalankan migrasi ...
  backoffLimit: 1
```

**Anotasi Penting:**

*   **`helm.sh/hook` (Wajib):** Daftar hook (dipisahkan koma) kapan objek ini harus dijalankan (misalnya, `pre-install`, `post-upgrade`).
*   **`helm.sh/hook-weight` (Opsional):** Angka integer (bisa negatif) yang menentukan urutan eksekusi hook *di dalam fase hook yang sama*. Hook dengan bobot lebih rendah dijalankan terlebih dahulu. Defaultnya 0.
*   **`helm.sh/hook-delete-policy` (Opsional):** Daftar kebijakan (dipisahkan koma) yang menentukan kapan Helm harus menghapus sumber daya hook ini setelah dibuat. Pilihan:
    *   `before-hook-creation`: Hapus hook sebelumnya dengan nama yang sama *sebelum* hook baru dijalankan. Berguna untuk memastikan hook berjalan dari keadaan bersih setiap saat (misalnya, Job).
    *   `hook-succeeded`: Hapus hook *setelah* ia berhasil dijalankan.
    *   `hook-failed`: Hapus hook *jika* ia gagal dijalankan.

**Jika tidak ada `hook-delete-policy` yang ditentukan, Helm tidak akan pernah menghapus sumber daya hook tersebut.** Anda perlu membersihkannya secara manual jika perlu. Kebijakan `before-hook-creation` dan `hook-succeeded` sering digunakan bersama untuk Jobs.

## Pertimbangan Penting

*   **Hook Blocking:** Secara default, Helm akan **menunggu** hook selesai (terutama Jobs dan Pods) sebelum melanjutkan ke langkah berikutnya dalam siklus hidup. Jika hook gagal atau macet, operasi Helm (install/upgrade/delete) juga akan gagal atau macet. Pastikan hook Anda dirancang untuk selesai atau memiliki batas waktu.
*   **Idempotensi:** Usahakan membuat hook Anda idempoten (dapat dijalankan berkali-kali tanpa efek samping yang tidak diinginkan), terutama jika Anda tidak menggunakan `hook-delete-policy`.
*   **Manajemen State Hook:** Ingat bahwa Hook tidak dikelola oleh Helm seperti sumber daya rilis biasa. Anda bertanggung jawab atas pembersihan jika `hook-delete-policy` tidak digunakan atau tidak mencakup semua kasus.
*   **Akses ke Nilai & Objek Release:** Template hook memiliki akses ke semua objek bawaan Helm (`.Values`, `.Release`, `.Chart`, dll.) sama seperti template biasa, memungkinkan Anda mengkonfigurasi hook secara dinamis.
*   **Jangan Gunakan untuk Sumber Daya Utama:** Hindari menggunakan hook untuk men-deploy komponen inti aplikasi Anda (gunakan template biasa untuk itu). Hook ditujukan untuk tugas-tugas tambahan selama siklus hidup.
*   **Test Hooks:** Hook `test` sangat berguna untuk validasi pasca-deployment. `helm test` akan menjalankan semua Pod/Job dengan anotasi `helm.sh/hook: test` dan melaporkan keberhasilan atau kegagalan berdasarkan status penyelesaian Pod/Job tersebut.

Helm Lifecycle Hooks menyediakan mekanisme yang kuat untuk mengintegrasikan tugas-tugas kustom ke dalam alur kerja deployment aplikasi Anda, memungkinkan otomatisasi tugas persiapan, migrasi, verifikasi, dan pembersihan yang terkait dengan siklus hidup aplikasi Kubernetes Anda. Gunakan dengan bijak dan perhatikan manajemen state sumber daya hook itu sendiri.
