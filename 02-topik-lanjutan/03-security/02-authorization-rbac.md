# Authorization: Role-Based Access Control (RBAC)

Setelah seorang pengguna atau proses diautentikasi (Authentication), langkah berikutnya adalah **Authorization** (Otorisasi): menentukan apakah subjek yang diautentikasi tersebut *diizinkan* untuk melakukan tindakan yang diminta pada sumber daya tertentu.

Kubernetes menggunakan **Role-Based Access Control (RBAC)** sebagai mekanisme otorisasi utamanya. RBAC memungkinkan administrator untuk mendefinisikan *peran* (roles) dengan *izin* (permissions) spesifik dan kemudian menetapkan peran tersebut kepada *subjek* (users, groups, atau service accounts).

## Mengapa RBAC?

*   **Granularitas:** Memungkinkan kontrol akses yang sangat detail. Anda bisa menentukan izin seperti "hanya boleh membaca (get, list, watch) Pods di namespace `dev`" atau "boleh membuat (create) Deployments di seluruh cluster".
*   **Prinsip Least Privilege:** Memudahkan penerapan prinsip keamanan fundamental ini, di mana subjek hanya diberikan izin minimum yang diperlukan untuk melakukan tugasnya.
*   **Pengelolaan Terpusat:** Izin didefinisikan sebagai objek Kubernetes (Roles, ClusterRoles) dan penugasan izin juga objek (RoleBindings, ClusterRoleBindings), membuatnya mudah dikelola secara deklaratif (misalnya, melalui GitOps).
*   **Standar:** RBAC adalah mekanisme otorisasi standar dan paling banyak digunakan di Kubernetes.

## Objek Inti RBAC

Ada empat jenis objek utama dalam RBAC API Group (`rbac.authorization.k8s.io`):

1.  **`Role`:**
    *   **Scope:** Namespaced (hanya berlaku dalam satu namespace).
    *   **Tujuan:** Mendefinisikan sekumpulan izin (verbs) pada sekumpulan sumber daya (resources) API Kubernetes *di dalam namespace tertentu*.
    *   **Contoh:** Memberikan izin untuk `get`, `list`, `watch` pada `pods` dan `services` di namespace `frontend`.

2.  **`ClusterRole`:**
    *   **Scope:** Cluster-wide (berlaku di seluruh cluster).
    *   **Tujuan:** Sama seperti `Role`, tetapi untuk:
        *   Sumber daya cluster-scoped (seperti `nodes`, `persistentvolumes`, `namespaces`).
        *   Sumber daya namespaced *di semua namespace* (misalnya, memberikan izin `get` pods di *semua* namespace).
        *   Endpoint non-resource (seperti `/healthz`, `/metrics`).
    *   **Contoh:** Memberikan izin `get`, `list` pada `nodes`, atau memberikan izin `get`, `list`, `watch` pada `pods` di *semua* namespace.

3.  **`RoleBinding`:**
    *   **Scope:** Namespaced.
    *   **Tujuan:** Mengikat (bind) sebuah `Role` atau `ClusterRole` ke satu atau lebih *subjek* (Users, Groups, ServiceAccounts) *di dalam namespace tertentu*.
    *   **Penting:** Jika Anda mengikat `ClusterRole` menggunakan `RoleBinding`, izin `ClusterRole` tersebut hanya akan berlaku untuk sumber daya *di dalam namespace RoleBinding tersebut*.
    *   **Contoh:** Mengikat `Role` "pod-reader" ke `User` "developer-alice" di namespace `dev`. Atau mengikat `ClusterRole` "view" (role bawaan) ke `Group` "auditors" di namespace `finance`.

4.  **`ClusterRoleBinding`:**
    *   **Scope:** Cluster-wide.
    *   **Tujuan:** Mengikat (bind) sebuah `ClusterRole` ke satu atau lebih *subjek* (Users, Groups, ServiceAccounts) *di seluruh cluster*.
    *   **Penting:** Ini memberikan izin yang didefinisikan dalam `ClusterRole` di *semua namespace* dan untuk *sumber daya cluster-scoped*. Gunakan dengan hati-hati, terutama untuk `ClusterRole` dengan izin luas seperti `cluster-admin`.
    *   **Contoh:** Mengikat `ClusterRole` "cluster-admin" (role bawaan) ke `User` "cluster-administrator".

## Struktur Objek RBAC

**Role / ClusterRole:**

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role # atau ClusterRole
metadata:
  namespace: my-namespace # Hanya untuk Role
  name: pod-reader
rules:
- apiGroups: [""] # "" adalah core API group
  resources: ["pods", "pods/log"]
  verbs: ["get", "list", "watch"]
- apiGroups: ["apps"]
  resources: ["deployments"]
  verbs: ["get", "list"]
```

*   `rules`: Daftar aturan izin.
    *   `apiGroups`: Grup API dari sumber daya (misalnya, `""` untuk core, `apps`, `batch`, `networking.k8s.io`).
    *   `resources`: Jenis sumber daya yang terpengaruh (misalnya, `pods`, `deployments`, `services`, `nodes`). Bisa juga sub-resource seperti `pods/log`.
    *   `verbs`: Tindakan yang diizinkan (misalnya, `get`, `list`, `watch`, `create`, `update`, `patch`, `delete`, `deletecollection`, `exec`).

**RoleBinding / ClusterRoleBinding:**

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding # atau ClusterRoleBinding
metadata:
  name: read-pods-binding
  namespace: my-namespace # Hanya untuk RoleBinding
subjects:
- kind: User
  name: alice@example.com # Nama case-sensitive, tergantung authenticator
  apiGroup: rbac.authorization.k8s.io
- kind: Group
  name: frontend-devs
  apiGroup: rbac.authorization.k8s.io
- kind: ServiceAccount
  name: my-app-sa # Nama ServiceAccount
  namespace: my-namespace # Namespace ServiceAccount (penting!)
roleRef:
  kind: Role # atau ClusterRole (harus cocok dengan scope binding)
  name: pod-reader # Nama Role atau ClusterRole yang diikat
  apiGroup: rbac.authorization.k8s.io
```

*   `subjects`: Daftar pengguna, grup, atau service account yang mendapatkan izin.
*   `roleRef`: Referensi ke `Role` atau `ClusterRole` yang memberikan izin. `kind` harus `Role` untuk `RoleBinding` (kecuali mengikat ClusterRole ke namespace) dan `ClusterRole` untuk `ClusterRoleBinding`.

## Role Bawaan (Default Roles)

Kubernetes menyediakan beberapa `ClusterRole` bawaan yang umum digunakan:

*   `cluster-admin`: Akses superuser, dapat melakukan apa saja. Gunakan dengan sangat hati-hati.
*   `admin`: Akses admin di dalam namespace (diberikan melalui `RoleBinding`). Memungkinkan sebagian besar tindakan pada sumber daya namespaced, tetapi tidak dapat memodifikasi namespace itu sendiri atau sumber daya cluster-scoped.
*   `edit`: Mirip `admin`, tetapi tidak dapat melihat atau memodifikasi `Roles` atau `RoleBindings`.
*   `view`: Akses hanya-baca (read-only) di dalam namespace. Tidak dapat melihat `Secrets` atau `Roles`/`RoleBindings`.

## Perintah `kubectl` yang Berguna

*   **Melihat Roles/ClusterRoles:**
    ```bash
    kubectl get roles -n <namespace>
    kubectl get clusterroles
    kubectl describe role <role-name> -n <namespace>
    kubectl describe clusterrole <clusterrole-name>
    ```
*   **Melihat Bindings:**
    ```bash
    kubectl get rolebindings -n <namespace>
    kubectl get clusterrolebindings
    kubectl describe rolebinding <binding-name> -n <namespace>
    kubectl describe clusterrolebinding <binding-name>
    ```
*   **Memeriksa Izin (Sangat Berguna!):**
    ```bash
    # Apakah SAYA bisa melakukan <verb> pada <resource> di <namespace>?
    kubectl auth can-i <verb> <resource> --namespace <namespace>

    # Contoh: Apakah saya bisa membuat deployment di namespace 'dev'?
    kubectl auth can-i create deployments --namespace dev

    # Apakah user 'bob' bisa melihat secrets di namespace 'prod'?
    kubectl auth can-i list secrets --namespace prod --as bob

    # Apakah service account 'my-sa' di namespace 'app' bisa get pods?
    kubectl auth can-i get pods --namespace app --as system:serviceaccount:app:my-sa
    ```

## Praktik Terbaik RBAC

*   **Gunakan Prinsip Least Privilege:** Berikan hanya izin yang benar-benar diperlukan.
*   **Favoritkan `Role` dan `RoleBinding`:** Gunakan izin namespaced sebisa mungkin untuk membatasi cakupan. Hanya gunakan `ClusterRoleBinding` jika benar-benar diperlukan izin cluster-wide.
*   **Manfaatkan Role Bawaan:** Gunakan `view`, `edit`, `admin` jika sesuai daripada membuat role kustom dari awal.
*   **Gunakan Service Accounts untuk Aplikasi:** Jangan gunakan akun pengguna biasa untuk proses otomatis atau aplikasi di dalam cluster. Buat `ServiceAccount` spesifik untuk setiap aplikasi dan berikan izin minimal melalui `RoleBinding` atau `ClusterRoleBinding`.
*   **Audit Secara Berkala:** Tinjau `RoleBindings` dan `ClusterRoleBindings` secara teratur untuk memastikan izin masih sesuai dan tidak ada hak akses berlebih.
*   **Kelola RBAC Secara Deklaratif:** Simpan definisi Role/Binding Anda di Git dan terapkan menggunakan alat seperti `kubectl apply` atau GitOps tools.

RBAC adalah pilar keamanan fundamental di Kubernetes. Memahaminya dan menerapkannya dengan benar sangat penting untuk melindungi cluster dan aplikasi Anda dari akses yang tidak sah.
