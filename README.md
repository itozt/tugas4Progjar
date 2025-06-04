# Tugas 4 - Pemrograman Jaringan - HTTP Server
# Daftar Isi
- Langkah - Langkah Pengerjaan
  - [Thread Pool](https://github.com/itozt/tugas4Progjar/tree/main#-thread-pool)
  - [Process Pool](https://github.com/itozt/tugas4Progjar/tree/main#%EF%B8%8F-process-pool)
- Hasil dan Pembahasan
  - [Thread Pool](https://github.com/itozt/tugas4Progjar/tree/main#-hasil-dan-pembahasan-thread-pool)
  - [Process Pool](https://github.com/itozt/tugas4Progjar/tree/main#-hasil-dan-pembahasan-process-pool)
- Penjelasan Program yang Dimodifikasi
  - [http.py]()
  - [client.py]()
  - [server_thread_pool_http.py]()
  - [server_process_pool_http.py]()
    
# 🌳 Langkah - Langkah Pengerjaan
1. Buka Mesin 1 sebagai Server dan Mesin 2 sebagai Client. <br>
   Gunakan command di browser :
   ``` py
   http://127.0.0.1:60001 # untuk mesin 1
   http://127.0.0.1:60001 # untuk mesin 2
   ```
2. Pada mesin 2 (client), instal perintah requests dengan command :
   ``` bash
   pip install requests
   ```
3. Pada mesin 1 dan 2, ubah file `http.py` dengan command :
   ``` bash
   vim http.py
   ```
   Lalu, ubah isinya menjadi seperti yang ada pada file di sini : [Link Github http.py](https://github.com/itozt/tugas4Progjar/blob/main/http(modif).py)
4. Pada mesin 1 (server), ubah file `server_thread_pool_http.py` dengan command :
   ``` bash
   vim server_thread_pool_http.py
   ```
   Lalu, ubah isinya menjadi seperti yang ada pada file di sini : [Link Github server_thread_pool_http.py](https://github.com/itozt/tugas4Progjar/blob/main/server_thread_pool_http(modif).py)
5. Pada mesin 1 (server), ubah file `server_process_pool_http.py` dengan command :
   ``` bash
   vim server_process_pool_http.py
   ```
   Lalu, ubah isinya menjadi seperti yang ada pada file di sini : [Link Github server_process_pool_http.py](https://github.com/itozt/tugas4Progjar/blob/main/server_process_pool_http(modif).py)
6. Pada mesin 2 (client), buat file `client.py` dengan command :
   ``` bash
   nano client.py
   ```
   Lalu, isinya menjadi seperti yang ada pada file di sini : [Link Github client.py](https://github.com/itozt/tugas4Progjar/blob/main/client(modif).py)
8. Pada mesin 2 (client), buat file `domain.crt` pada direktori yang sama dengan file `client.py`
   ``` bash
   nano domain.crt
   ```
    Lalu, isinya menjadi seperti yang ada pada file di sini : [Link Github domain.crt](https://github.com/itozt/tugas4Progjar/blob/main/domain.crt)
<br>
Karena kita menjalankan dengan 2 mode (thread pool dan process pool), maka ada 2 langkah yang berbeda.

## 🔥 **Thread Pool**
1. Pada mesin 1, nyalakan server dengan command :
   ``` bash
   python3 server_thread_pool_http.py
   ```
2. Pada mesin 2, cek isi file `client.py` dengan command :
   ``` bash
   nano client.py
   ```
   Pastikan Server IP dan Server Port sudah benar
   ``` py
   SERVER_IP = '172.16.16.101' # IP mesin 1
   SERVER_PORT = 8885          # Port khusus untuk Thread Pool
   ```
3. Pada mesin 2, jalakan program `client.py` dengan command :
   ``` bash
   python3 client.py
   ```
4. Cek output yang dihasilkan pada mesin 1 (server), pastikan benar-benar sudah terhubung dengan mesin 2 (client).
5. Pada mesin 2, berikan perintah dengan ketentuan sebagai berikut :
   - Ketik **'LIST'** untuk melihat daftar file.
   - Ketik **'UPLOAD [nama_file_di_server] [encode_base64_isi_file]'** untuk mengunggah file.
   - Ketik **'DELETE [nama_file_di_server]'** untuk menghapus file.
   - Ketik **'EXIT'** untuk keluar.
6. Cek output respon yang dihasilkan pada mesin 1 (server), dan cek output yang diterima pada mesin 2 (client).

## ❄️ **Process Pool**
1. Pada mesin 1, nyalakan server dengan command :
   ``` bash
   python3 server_process_pool_http.py
   ```
2. Pada mesin 2, cek isi file `client.py` dengan command :
   ``` bash
   nano client.py
   ```
   Pastikan Server IP dan Server Port sudah benar
   ``` py
   SERVER_IP = '172.16.16.101' # IP mesin 1
   SERVER_PORT = 8889          # Port khusus untuk Process Pool
   ```
3. Pada mesin 2, jalakan program `client.py` dengan command :
   ``` bash
   python3 client.py
   ```
4. Cek output yang dihasilkan pada mesin 1 (server), pastikan benar-benar sudah terhubung dengan mesin 2 (client).
5. Pada mesin 2, berikan perintah dengan ketentuan sebagai berikut :
   - Ketik **'LIST'** untuk melihat daftar file.
   - Ketik **'UPLOAD [nama_file_di_server] [encode_base64_isi_file]'** untuk mengunggah file.
   - Ketik **'DELETE [nama_file_di_server]'** untuk menghapus file.
   - Ketik **'EXIT'** untuk keluar.
6. Cek output respon yang dihasilkan pada mesin 1 (server), dan cek output yang diterima pada mesin 2 (client).

# 🌳 Hasil dan Pembahasan Thread Pool
### 1️⃣ LIST
   **Screenshoot :** <br>
   ![ThreadPool_LIST](https://github.com/user-attachments/assets/4d51ae31-3335-4c47-b68b-fdd91a6f9625) <br>
   **Penjelasan :** <br>
   <p align="justify">Percobaan yang telah dilakukan menunjukkan sistem client-server berfungsi dengan sangat baik dan sesuai harapan. Saat server di Mesin 1 dijalankan dan client di Mesin 2 memulai komunikasi dengan perintah LIST, client berhasil membuat koneksi TCP ke server di 172.16.16.101 pada port 8885. Client kemudian membangun sebuah permintaan HTTP POST yang valid, dengan body berisi perintah LIST, lalu mengirimkannya ke server. Di sisi server, log menunjukkan koneksi diterima dengan sukses dari client. Server lalu mengalokasikan sebuah thread dari thread pool untuk menangani permintaan tersebut. Permintaan LIST diterima dan diurai sepenuhnya oleh server.</p>
   <p align="justify">Setelah itu, server memproses perintah LIST, mengambil daftar file yang ada di direktorinya, dan membangun respons HTTP 200 OK yang berisi daftar file tersebut di bagian body-nya. Respons ini kemudian dikirim kembali ke client, dan server menutup koneksi. Di sisi client, respons HTTP dari server berhasil diterima. Client secara otomatis memisahkan header dari body respons, lalu mencetak body yang berisi daftar nama-nama file. Inilah mengapa deretan nama file seperti http.py, server_process_pool_http.py, dan lainnya muncul di terminal client. Seluruh proses komunikasi dari pengiriman perintah hingga penerimaan dan tampilan hasil berjalan dengan lancar, menegaskan bahwa implementasi fungsionalitas LIST telah berhasil divalidasi dengan baik pada server mode Thread Pool.</p>

### 2️⃣ UPLOAD
   **Screenshoot :** <br>
   ![ThreadPool_UPLOAD](https://github.com/user-attachments/assets/28edc742-f229-48c6-a42d-0e572cf90253) <br>
   **Penjelasan :** <br>
   <p align="justify">Pada percobaan ini, client berhasil melakukan operasi UPLOAD pada server Thread Pool. Saat client di Mesin 2 mengirim perintah `UPLOAD perkenalan.txt aGFsbyBuYW1hIHNheWEgSVRP`, client membangun permintaan HTTP POST yang valid. Permintaan ini menyertakan perkenalan.txt sebagai nama file dan aGFsbyBuYW1hIHNheWEgSVRP (konten Base64 dari "Halo nama saya ITO") sebagai isi file di body permintaan, dengan total panjang data 144 byte.</p>
   <p align="justify">Server di Mesin 1, yang beroperasi dalam mode Thread Pool, menerima koneksi dan permintaan UPLOAD tersebut. Sebuah thread dari pool memproses permintaan, mendekode konten Base64, dan menyimpan file `perkenalan.txt` di direktori server. Setelah berhasil mengunggah file, server mengirimkan respons HTTP 200 OK kembali ke client dengan pesan "UPLOAD success" di body respons, berukuran 152 byte. Client kemudian menerima respons ini dan menampilkan pesan sukses tersebut di terminalnya.</p>

### 3️⃣ DELETE
   **Screenshoot :** <br>
   ![ThreadPool_DELETE](https://github.com/user-attachments/assets/35a31eed-9f50-4b93-b84d-84d590a7b771) <br>
   **Penjelasan :** <br>
   <p align="justify">Dalam percobaan ini, client berhasil melakukan operasi DELETE pada server Thread Pool. Saat client di Mesin 2 mengirim perintah `DELETE perkenalan.txt`, ia membuat permintaan HTTP POST yang valid. Permintaan ini menyertakan perkenalan.txt sebagai nama file yang akan dihapus di body permintaan, dengan total panjang data 119 byte.</p>
   <p align="justify">Server di Mesin 1, yang beroperasi dalam mode Thread Pool, menerima koneksi dan permintaan DELETE tersebut. Sebuah thread dari pool memproses permintaan, menemukan file perkenalan.txt, dan menghapusnya dari direktori server. Setelah berhasil menghapus file, server mengirimkan respons HTTP 200 OK kembali ke client dengan pesan "`DELETE SUCCESS`" di body respons, berukuran 152 byte. Client kemudian menerima respons ini dan menampilkan pesan sukses tersebut di terminalnya.</p>

# 🌳 Hasil dan Pembahasan Process Pool
### 1️⃣ LIST
**Screenshoot :** <br>
![ProcessPool_LIST](https://github.com/user-attachments/assets/49e22978-50ce-42bf-a64a-35b5898423fa)<br>
**Penjelasan :** <br>
   <p align="justify">Dalam percobaan ini, client berhasil menguji fungsionalitas LIST pada server yang berjalan dalam mode Process Pool. Saat client di Mesin 2 mengirim perintah LIST, ia membuat permintaan HTTP POST yang valid ke server di 172.16.16.101 pada port 8889. Server menerima permintaan ini, dan sebuah proses dari process pool ditugaskan untuk memprosesnya. Server berhasil membaca seluruh permintaan (101 byte), memproses perintah LIST, dan mengirimkan respons HTTP 200 OK yang berisi daftar file sebagai body (panjang 447 byte) kembali ke client. Client kemudian menerima, mem-parsing, dan menampilkan daftar file tersebut di terminalnya, menegaskan bahwa operasi LIST berfungsi dengan benar pada server mode Process Pool.</p>

### 2️⃣ UPLOAD
   **Screenshoot :** <br>
   ![ProcessPool_UPLOAD](https://github.com/user-attachments/assets/d90f78c2-ac75-4e34-ac88-3be093353925)<br>
   **Penjelasan :** <br>
   <p align="justify">Dalam percobaan ini, client berhasil mengunggah file ke server yang beroperasi dalam mode Process Pool. Saat client di Mesin 2 mengirim perintah UPLOAD nama.txt Q2hyaXN0b2ZvcnVzIEluZHJh, client membuat permintaan HTTP POST yang valid. Permintaan ini berisi nama file nama.txt dan konten Base64 Q2hyaXN0b2ZvcnVzIEluZHJh di bagian body, dengan total panjang data 138 byte. Server di Mesin 1, yang mendengarkan pada port 8889 menggunakan process pool, menerima dan memproses permintaan UPLOAD tersebut. Sebuah proses dari pool menangani permintaan, mendekode konten Base64, dan berhasil menyimpan file nama.txt di direktori server. Sebagai konfirmasi, server mengirimkan respons HTTP 200 OK dengan pesan "UPLOAD success" kembali ke client, yang kemudian ditampilkan di terminal client.</p>

### 3️⃣ DELETE
   **Screenshoot :** <br>
   ![ProcessPool_DELETE](https://github.com/user-attachments/assets/35d63dba-520d-495c-935a-2468825af2a1)<br>
   **Penjelasan :** <br>
   <p align="justify">Pada percobaan ini, client berhasil melakukan operasi DELETE pada server yang berjalan dalam mode Process Pool. Ketika client di Mesin 2 mengirim perintah DELETE nama.txt, client membuat permintaan HTTP POST yang valid. Permintaan ini menyertakan nama.txt sebagai nama file yang akan dihapus di bagian body, dengan total panjang data 113 byte. Server di Mesin 1, yang mendengarkan pada port 8889 menggunakan process pool, menerima dan memproses permintaan DELETE tersebut. Sebuah proses dari pool menangani permintaan, berhasil menghapus file nama.txt dari direktori server. Sebagai konfirmasi, server mengirimkan respons HTTP 200 OK dengan pesan "DELETE SUCCESS" kembali ke client, yang kemudian ditampilkan di terminal client.</p>
