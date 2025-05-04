# Siklus Hidup Pod (Pod Lifecycle)

Pods di Kubernetes bersifat **fana** (ephemeral), artinya mereka tidak dirancang untuk hidup selamanya. Mereka dibuat, diberi ID unik (UID), dijadwalkan ke Node, menjalankan kontainer mereka, dan akhirnya berhenti atau dihapus. Jika sebuah Pod dihapus, ia tidak akan kembali; jika Anda membutuhkan Pod baru (misalnya karena kegagalan), Anda (atau lebih umum, sebuah Controller seperti Deployment) harus membuat Pod *baru* dengan UID baru.

Memahami siklus hidup Pod penting untuk men-debug aplikasi dan memahami perilaku cluster. Siklus hidup Pod direpresentasikan terutama melalui **fase (Phase)** dan **kondisi (Conditions)**.

## Fase Pod (`status.phase`)

Fase Pod adalah ringkasan sederhana tentang di mana Pod berada dalam siklus hidupnya. Nilai yang mungkin untuk `status.phase` adalah:

1.  **`Pending`:**
    *   Pod telah diterima oleh cluster Kubernetes (objek Pod dibuat di API Server).
    *   Tetapi, satu atau lebih kontainer di dalamnya **belum** dibuat atau siap dijalankan.
    *   Ini bisa terjadi karena beberapa alasan:
        *   **Penjadwalan (Scheduling):** Scheduler belum menemukan Node yang cocok untuk Pod (misalnya, resource tidak cukup, Node tidak memenuhi affinity/selector, Pod tidak mentolerir Taint Node).
        *   **Tarik Image (Image Pull):** Kubelet sedang dalam proses mengunduh (pull) image kontainer yang diperlukan. Ini bisa memakan waktu tergantung ukuran image dan kecepatan jaringan.
        *   **Pembuatan Volume:** Volume penyimpanan (misalnya dari PVC) sedang disiapkan atau di-attach ke Node.
    *   Pod akan tetap dalam fase `Pending` sampai bisa dijadwalkan dan semua persiapan awal selesai. Periksa `kubectl describe pod <pod-name>` untuk melihat Events yang memberikan petunjuk mengapa Pod masih Pending.

2.  **`Running`:**
    *   Pod telah berhasil **diikat (bound)** ke sebuah Node.
    *   Semua kontainer di dalam Pod telah **dibuat** oleh container runtime.
    *   Setidaknya **satu** kontainer masih **berjalan (running)**, atau sedang dalam proses **memulai (starting)** atau **me-restart (restarting)**.
    *   **Penting:** Fase `Running` *tidak* berarti Pod atau aplikasi di dalamnya benar-benar berfungsi atau siap melayani traffic. Itu hanya berarti proses kontainer utama ada dan berjalan. Anda perlu memeriksa **Kondisi Pod** (terutama `Ready`) untuk status fungsionalitas.

3.  **`Succeeded`:**
    *   Semua kontainer di dalam Pod telah **berhenti (terminated)** dengan **sukses** (exit code 0).
    *   Kontainer-kontainer ini **tidak akan di-restart** oleh Kubelet (terlepas dari `restartPolicy`).
    *   Fase ini biasanya relevan untuk Pods yang dibuat oleh **Jobs** atau tugas batch lainnya yang dirancang untuk berjalan hingga selesai. Pods yang dikelola oleh Deployment atau StatefulSet biasanya tidak diharapkan mencapai fase ini.

4.  **`Failed`:**
    *   Semua kontainer di dalam Pod telah **berhenti (terminated)**.
    *   Setidaknya **satu** kontainer berhenti dengan **kegagalan** (exit code non-zero) atau dihentikan oleh sistem (misalnya, OOMKilled).
    *   Fase ini juga biasanya relevan untuk Pods **Jobs** yang gagal menyelesaikan tugasnya.

5.  **`Unknown`:**
    *   State Pod **tidak dapat diperoleh** oleh Control Plane.
    *   Ini biasanya terjadi karena **masalah komunikasi** dengan Kubelet di Node tempat Pod seharusnya berjalan (misalnya, Node mati atau tidak dapat dijangkau jaringannya).
    *   Controller Manager akan menunggu beberapa saat (timeout) sebelum mungkin menandai Pod sebagai `Failed` atau mengambil tindakan lain berdasarkan status Node.

## Kondisi Pod (`status.conditions`)

Selain fase ringkasan, Kubernetes melacak kondisi (Conditions) yang lebih detail tentang Pod. Kondisi adalah array dalam `status.conditions`, di mana setiap elemen memiliki field `type`, `status` (`True`, `False`, `Unknown`), `lastProbeTime`, `lastTransitionTime`, dan mungkin `reason` serta `message`.

Kondisi utama meliputi:

*   **`PodScheduled`:** Status `True` jika Pod telah berhasil dijadwalkan ke sebuah Node oleh Scheduler. Status `False` jika belum.
*   **`Initialized`:** Status `True` jika semua [Init Containers](./init-containers.md) dalam Pod telah berhasil diselesaikan. Status `False` jika masih ada Init Container yang berjalan atau gagal.
*   **`ContainersReady`:** Status `True` jika *semua* kontainer aplikasi di dalam Pod (tidak termasuk Init Containers) telah lulus `readinessProbe` mereka (jika dikonfigurasi). Status `False` jika setidaknya satu kontainer belum siap.
*   **`Ready`:** Kondisi ini adalah agregasi dari `ContainersReady` (dan beberapa kondisi lain di masa depan). Status `True` jika Pod dianggap siap untuk melayani permintaan (semua kontainer siap). Pod yang `Ready` akan dimasukkan sebagai endpoint oleh Services yang menargetkannya. Status `False` jika tidak. **Ini adalah indikator penting untuk fungsionalitas aplikasi.**

Anda dapat melihat kondisi ini menggunakan `kubectl describe pod <pod-name>`.

## Status Kontainer (`status.containerStatuses`)

Kubernetes juga melacak status setiap kontainer individu di dalam Pod dalam `status.containerStatuses`. Ini mencakup informasi seperti:

*   `name`: Nama kontainer.
*   `state`: Status kontainer saat ini (`waiting`, `running`, `terminated`).
    *   `waiting`: Kontainer belum `running` atau `terminated`. Mungkin sedang menarik image (`ImagePullBackOff`, `ErrImagePull`), menunggu dependensi, atau mengalami error lain (`CrashLoopBackOff`). `reason` akan memberikan detail.
    *   `running`: Kontainer sedang berjalan normal. `startedAt` menunjukkan kapan dimulai.
    *   `terminated`: Kontainer telah berhenti. `exitCode`, `reason` (`Completed`, `Error`, `OOMKilled`), `startedAt`, `finishedAt` memberikan detail.
*   `lastState`: Status kontainer sebelumnya (berguna untuk melihat mengapa kontainer di-restart).
*   `ready`: `true` jika kontainer lulus `readinessProbe`-nya.
*   `restartCount`: Berapa kali kontainer ini telah di-restart oleh Kubelet.
*   `image`, `imageID`: Image yang digunakan.
*   `containerID`: ID runtime kontainer.

## Kebijakan Restart (`spec.restartPolicy`)

Field `spec.restartPolicy` pada Pod menentukan apa yang harus dilakukan Kubelet jika kontainer di dalam Pod berhenti. Nilai yang mungkin:

*   **`Always` (Default):** Kubelet akan selalu mencoba me-restart kontainer yang berhenti (baik berhenti sukses maupun gagal). Ini adalah default dan cocok untuk Pods yang dikelola oleh Deployment, StatefulSet, DaemonSet yang diharapkan berjalan terus menerus.
*   **`OnFailure`:** Kubelet hanya akan me-restart kontainer jika berhenti dengan exit code non-zero (gagal). Cocok untuk Pods yang dibuat oleh Jobs yang perlu mencoba lagi jika gagal.
*   **`Never`:** Kubelet tidak akan pernah me-restart kontainer yang berhenti. Cocok untuk Pods Jobs yang hanya perlu dijalankan sekali hingga selesai atau gagal.

**Penting:** `restartPolicy` berlaku untuk *semua* kontainer dalam Pod dan hanya mengacu pada restart *di Node yang sama*. Jika seluruh Node gagal, Pod tidak akan di-restart di Node lain oleh Kubelet; itu adalah tugas Controller (seperti Deployment) untuk membuat Pod *baru* di Node lain.

Memahami fase, kondisi, status kontainer, dan kebijakan restart sangat penting untuk mendiagnosis masalah Pod dan memastikan aplikasi Anda berjalan seperti yang diharapkan di Kubernetes. Selalu gunakan `kubectl describe pod` sebagai langkah pertama saat troubleshooting Pod.
