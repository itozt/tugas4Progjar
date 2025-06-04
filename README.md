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
