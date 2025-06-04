# Tugas 4 - Pemrograman Jaringan - HTTP Server

# Langkah - Langkah Pengerjaan
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
