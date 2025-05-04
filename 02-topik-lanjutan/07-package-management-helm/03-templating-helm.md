# Templating Helm: Membuat Manifest Dinamis

Kekuatan utama Helm terletak pada **engine templating**-nya. Alih-alih menulis file manifest Kubernetes YAML statis, Anda membuat **template** yang berisi placeholder dan logika. Helm kemudian **merender** template ini, menggabungkan **nilai (values)** yang disediakan pengguna (atau nilai default), untuk menghasilkan file manifest YAML akhir yang valid yang diterapkan ke cluster.

Helm menggunakan bahasa template **Go `text/template`** sebagai dasarnya, ditambah dengan banyak fungsi tambahan dari library **[Sprig](http://masterminds.github.io/sprig/)** dan beberapa fungsi khusus Helm.

## Dasar-dasar Templating

1.  **File Template:** Semua file di dalam direktori `templates/` (kecuali yang diawali `_` atau `NOTES.txt`) dianggap sebagai template manifest.
2.  **Aksi Template (Actions):** Logika template disisipkan dalam `{{ }}`.
    ```yaml
    apiVersion: v1
    kind: ConfigMap
    metadata:
      # Contoh: Menyisipkan nilai dari values.yaml
      name: {{ .Release.Name }}-configmap
    data:
      # Contoh lain
      myvalue: "Hello World"
      drink: {{ .Values.favoriteDrink | default "tea" | quote }}
      #        ^                     ^           ^       ^
      #        |                     |           |       | Pipe ke fungsi 'quote'
      #        |                     |           | Pipe ke fungsi 'default'
      #        |                     | Mengakses nilai dari values.yaml
      #        | Titik (.) adalah objek scope saat ini
    ```
3.  **Objek Bawaan (`.`):** Di dalam template, Anda memiliki akses ke beberapa objek bawaan tingkat atas melalui titik (`.`):
    *   **`.Values`**: Objek yang paling sering digunakan. Berisi semua nilai dari file `values.yaml`, yang ditimpa oleh file yang disediakan pengguna (`-f values-prod.yaml`), dan ditimpa lagi oleh flag `--set`. Anda mengakses nilai menggunakan notasi titik (misalnya, `.Values.image.repository`, `.Values.service.port`).
    *   **`.Release`**: Berisi informasi tentang Release saat ini.
        *   `.Release.Name`: Nama Release (misalnya, `my-awesome-app-123`).
        *   `.Release.Namespace`: Namespace tempat Chart diinstal.
        *   `.Release.Service`: Layanan yang menjalankan Helm (selalu `Helm`).
        *   `.Release.Revision`: Nomor revisi Release ini.
        *   `.Release.IsUpgrade`: `true` jika ini operasi upgrade/rollback.
        *   `.Release.IsInstall`: `true` jika ini operasi instalasi baru.
    *   **`.Chart`**: Berisi konten dari file `Chart.yaml` (misalnya, `.Chart.Name`, `.Chart.Version`, `.Chart.AppVersion`).
    *   **`.Files`**: Memungkinkan akses ke file *non-template* di dalam Chart (misalnya, membaca file konfigurasi statis).
        *   `.Files.Get "namafile.txt"`: Mendapatkan konten file sebagai string.
        *   `.Files.GetBytes "binary.dat"`: Mendapatkan konten file sebagai byte array.
    *   **`.Capabilities`**: Berisi informasi tentang kemampuan cluster Kubernetes yang dituju.
        *   `.Capabilities.KubeVersion.Version`: Versi Kubernetes (misalnya, `v1.28.1`).
        *   `.Capabilities.KubeVersion.Major`, `.Capabilities.KubeVersion.Minor`.
        *   `.Capabilities.APIVersions.Has "batch/v1"`: Memeriksa apakah versi API tertentu tersedia.

## Mengakses Nilai (`.Values`)

Anda menavigasi struktur `values.yaml` menggunakan notasi titik.

```yaml
# values.yaml
image:
  repository: my-repo/my-image
  tag: latest
service:
  port: 8080
  type: LoadBalancer

# templates/deployment.yaml
spec:
  containers:
    - name: {{ .Chart.Name }}
      image: "{{ .Values.image.repository }}:{{ .Values.image.tag | default .Chart.AppVersion }}"
      #        ^ Quotes penting jika nilai bisa mengandung karakter khusus
      #                                         ^ Menggunakan default jika .Values.image.tag kosong
```

## Fungsi dan Pipeline

Helm menyediakan banyak fungsi bawaan (dari Go template, Sprig, dan Helm sendiri) yang dapat digunakan untuk memanipulasi data. Fungsi dipanggil dengan `namaFungsi arg1 arg2 ...`.

**Pipelines (`|`)**: Cara yang sangat umum untuk mengalirkan output dari satu fungsi (atau nilai) sebagai argumen terakhir ke fungsi berikutnya.

```yaml
data:
  config.yaml: |
    # Menggunakan fungsi 'indent' untuk mengindentasi blok YAML
    {{ .Values.myConfig | nindent 4 }}
  # Menggunakan 'quote' untuk memastikan nilai string dikutip
  database_url: {{ .Values.db.url | quote }}
  # Menggunakan 'upper' lalu 'quote'
  app_name: {{ .Values.appName | upper | quote }}
  # Menggunakan 'default' jika nilai tidak ada
  log_level: {{ .Values.logLevel | default "info" }}
  # Menggunakan 'required' untuk menghentikan render jika nilai wajib hilang
  api_key: {{ required "A valid .Values.apiKey is required!" .Values.apiKey | quote }}
```

**Beberapa Fungsi Penting Lainnya:**

*   **String:** `upper`, `lower`, `trim`, `trunc`, `quote`, `squote`, `indent`, `nindent`, `contains`, `hasPrefix`, `hasSuffix`, `replace`, `splitList`, `join`.
*   **Integer:** `add`, `sub`, `mul`, `div`, `mod`, `max`, `min`.
*   **Lists/Dicts:** `list`, `dict`, `get`, `set`, `unset`, `hasKey`, `pluck`, `merge`, `deepCopy`.
*   **Encoding:** `b64enc`, `b64dec`.
*   **Refleksi & Tipe:** `typeOf`, `kindIs`.
*   **Filesystem:** `glob`, `Get`, `GetBytes` (melalui `.Files`).
*   **Kubernetes & Helm:** `lookup` (mencari objek K8s yang ada - gunakan hati-hati!), `include` (memanggil template bernama lain), `template` (merender string sebagai template), `required`.

## Kontrol Alur (Control Flow)

Anda dapat menggunakan `if`/`else`, `range`, dan `with` untuk membuat template yang lebih dinamis.

**`if`/`else`:**

```yaml
{{- if .Values.ingress.enabled -}} # {{- hapus whitespace sebelum }}
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: {{ .Release.Name }}-ingress
spec:
  # ... definisi ingress ...
{{- else -}}
# Mungkin buat Service NodePort jika ingress tidak aktif
apiVersion: v1
kind: Service
# ... definisi service NodePort ...
{{- end -}} # Wajib ada 'end'
```

**`range` (Iterasi):**
Berguna untuk mengulang list atau map di `values.yaml`.

```yaml
# values.yaml
extraConfigData:
  key1: value1
  key2: value2

# templates/configmap.yaml
data:
{{- range $key, $value := .Values.extraConfigData }}
  {{ $key }}: {{ $value | quote }}
{{- end }}
```

**`with` (Mengubah Scope `.`):**
Berguna untuk menyederhanakan akses ke struktur nested.

```yaml
{{- with .Values.image }} # Di dalam blok 'with', '.' sekarang merujuk ke .Values.image
containers:
- name: main
  image: "{{ .repository }}:{{ .tag }}" # Lebih pendek daripada .Values.image.repository
  pullPolicy: {{ .pullPolicy | default "IfNotPresent" }}
{{- end }}
```

## Template Helpers (`_helpers.tpl`)

Untuk logika template yang kompleks atau berulang, praktik terbaik adalah mendefinisikannya sebagai *named template* di file `templates/_helpers.tpl` dan memanggilnya menggunakan `include`.

```yaml
# templates/_helpers.tpl

{{/*
Definisikan nama aplikasi standar.
Kita bisa memanggil ini di template lain menggunakan:
{{ include "mychart.fullname" . }}
*/}}
{{- define "mychart.fullname" -}}
{{- if .Values.fullnameOverride -}}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" -}}
{{- else -}}
{{- $name := default .Chart.Name .Values.nameOverride -}}
{{- if contains $name .Release.Name -}}
{{- .Release.Name | trunc 63 | trimSuffix "-" -}}
{{- else -}}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" -}}
{{- end -}}
{{- end -}}
{{- end -}}

{{/*
Definisikan labels standar untuk digunakan di semua resource.
Panggil dengan: {{ include "mychart.labels" . | nindent 4 }}
*/}}
{{- define "mychart.labels" -}}
helm.sh/chart: {{ include "mychart.chart" . }}
{{ include "mychart.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end -}}

{{/*
Definisikan selector labels.
Panggil dengan: {{ include "mychart.selectorLabels" . }}
*/}}
{{- define "mychart.selectorLabels" -}}
app.kubernetes.io/name: {{ include "mychart.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

# ... (definisi helper lainnya) ...
```

```yaml
# templates/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ include "mychart.fullname" . }} # Memanggil helper fullname
  labels:
    {{- include "mychart.labels" . | nindent 4 }} # Memanggil helper labels
spec:
  selector:
    matchLabels:
      {{- include "mychart.selectorLabels" . | nindent 6 }} # Memanggil helper selectorLabels
  template:
    metadata:
      labels:
        {{- include "mychart.selectorLabels" . | nindent 8 }}
    spec:
      # ...
```

**Catatan tentang Whitespace:**
*   `{{- ... }}`: Menghapus whitespace *sebelum* tag.
*   `{{ ... -}}`: Menghapus whitespace *setelah* tag.
*   Gunakan ini untuk mengontrol format YAML yang dihasilkan agar rapi.

Templating Helm adalah fitur yang sangat kuat yang memungkinkan pembuatan Chart yang fleksibel, dapat dikonfigurasi, dan dapat digunakan kembali. Mempelajari fungsi dan kontrol alur yang tersedia akan sangat meningkatkan kemampuan Anda dalam mengelola aplikasi Kubernetes dengan Helm. Gunakan `helm template <chart-path> -f <values-file>` untuk melihat hasil render YAML sebelum menginstalnya.
