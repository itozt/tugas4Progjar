import sys
import os.path
import uuid
from glob import glob
from datetime import datetime
import os
import base64
import re # Import modul regex (meskipun belum dipakai, jaga jika nanti perlu)

class HttpServer:
    def __init__(self):
        self.sessions={}
        self.types={}
        self.types['.pdf']='application/pdf'
        self.types['.jpg']='image/jpeg'
        self.types['.txt']='text/plain'
        self.types['.html']='text/html'
        self.types['.png']='image/png'
        self.types['.gif']='image/gif'
        self.types['.json']='application/json'
        # Tambahkan tipe file lain jika diperlukan, contoh:
        self.types['.css']='text/css'
        self.types['.js']='application/javascript'


    def response(self, kode=404, message='Not Found', messagebody=bytes(), headers={}):
        """
        Membangun respons HTTP lengkap dalam bentuk bytes.
        """
        tanggal = datetime.now().strftime('%c')
        resp = []
        resp.append(f"HTTP/1.0 {kode} {message}\r\n")
        resp.append(f"Date: {tanggal}\r\n")
        resp.append("Connection: close\r\n") # Selalu tutup koneksi setelah respons
        resp.append("Server: myserver/1.0\r\n")
        resp.append(f"Content-Length: {len(messagebody)}\r\n") # Penting untuk client
        for kk in headers:
            resp.append(f"{kk}: {headers[kk]}\r\n")
        resp.append("\r\n") # Baris kosong pemisah header dan body

        response_headers = ''.join(resp)
        
        # Pastikan messagebody selalu dalam bentuk bytes sebelum digabungkan
        if not isinstance(messagebody, bytes):
            messagebody = str(messagebody).encode('utf-8') # Default encode string ke utf-8

        response_bytes = response_headers.encode('latin-1') + messagebody # Encode header ke latin-1
        return response_bytes

    def parse_headers(self, request_lines):
        """Menganalisis baris-baris header HTTP menjadi dictionary."""
        headers = {}
        for line in request_lines:
            if ':' in line:
                key, value = line.split(':', 1)
                headers[key.strip().lower()] = value.strip()
        return headers

    def proses(self, raw_data_bytes):
        """
        Memproses seluruh request HTTP dari client (dalam bentuk bytes).
        """
        # Cari pemisah header dan body (\r\n\r\n)
        header_end_index = raw_data_bytes.find(b'\r\n\r\n')
        if header_end_index == -1:
            # Jika tidak ada pemisah header/body yang valid
            return self.response(400, 'Bad Request', 'No valid HTTP header end.'.encode('utf-8'))

        # Pisahkan header (string) dan body (bytes)
        # Decode header menggunakan 'latin-1' karena header HTTP seringkali menggunakan encoding ini
        headers_part_str = raw_data_bytes[:header_end_index].decode('latin-1')
        body_bytes = raw_data_bytes[header_end_index + 4:] # +4 untuk '\r\n\r\n'

        request_lines = headers_part_str.split("\r\n")
        request_line = request_lines[0] # Baris pertama: METHOD /path HTTP/1.x
        all_headers = self.parse_headers(request_lines[1:]) # Headers lainnya

        j = request_line.split(" ")
        try:
            method = j[0].upper().strip()
            object_address = j[1].strip() # Path URL

            if (method == 'GET'):
                # Handle GET requests (untuk file statis seperti page.html)
                return self.http_get(object_address, all_headers)
            elif (method == 'POST'):
                # Jika request adalah POST ke endpoint /command
                if object_address == '/command':
                    try:
                        # Body dari POST /command berisi perintah kustom (LIST/UPLOAD/DELETE)
                        # Decode body ke UTF-8 untuk diproses
                        body_string = body_bytes.decode('utf-8') 
                        return self.handle_custom_command(body_string)
                    except UnicodeDecodeError:
                        return self.response(400, 'Bad Request', 'Invalid body encoding for custom command.'.encode('utf-8'))
                else:
                    # POST request lain yang tidak ke /command dianggap Bad Request untuk tugas ini
                    return self.response(400, 'Bad Request', 'POST requests only supported for /command endpoint.'.encode('utf-8'))
            else:
                # Metode HTTP lain yang tidak didukung
                return self.response(400, 'Bad Request', ''.encode('utf-8'), {})
        except IndexError:
            # Jika baris request tidak valid (misal, tidak ada METHOD atau PATH)
            return self.response(400, 'Bad Request', ''.encode('utf-8'), {})
            
    def http_get(self, object_address, headers):
        """
        Menangani GET requests untuk menyajikan file statis.
        """
        thedir='./' # Direktori kerja server
        
        # Jika request adalah root path ('/'), sajikan page.html
        if (object_address == '/'):
            try:
                with open(os.path.join(thedir, 'page.html'), 'rb') as fp:
                    isi = fp.read()
                return self.response(200,'OK', isi, {'Content-type': 'text/html'})
            except FileNotFoundError:
                 return self.response(200,'OK','Ini Adalah web Server percobaan'.encode('utf-8'),dict())

        # Untuk request file statis lainnya (misal: /pokijan.jpg)
        object_address_path = object_address[1:] # Hapus '/' di awal path
        full_path = os.path.join(thedir, object_address_path)

        # Cek apakah file ada dan itu adalah file, bukan direktori
        if not os.path.exists(full_path) or not os.path.isfile(full_path):
            return self.response(404,'Not Found',''.encode('utf-8'),{})
        
        try:
            with open(full_path,'rb') as fp: # Buka file dalam mode binary read
                isi = fp.read()
            
            # Tentukan Content-Type berdasarkan ekstensi file
            fext = os.path.splitext(full_path)[1]
            content_type = self.types.get(fext.lower(), 'application/octet-stream') # Default jika tipe tidak ditemukan
            
            headers={}
            headers['Content-type']=content_type
            
            return self.response(200,'OK',isi,headers)
        except Exception as e:
            return self.response(500, 'Internal Server Error', f'Error reading file: {e}'.encode('utf-8'), {'Content-type': 'text/plain'})

    # --- Metode Baru: handle_custom_command ---
    def handle_custom_command(self, command_string):
        """
        Memproses perintah kustom (LIST, UPLOAD, DELETE) yang ada di body POST request.
        """
        command_string = command_string.strip()
        thedir = './' # Direktori kerja server

        # Menangani perintah LIST
        if command_string.upper() == 'LIST':
            try:
                files_in_dir = os.listdir(thedir) # Dapatkan semua item di direktori
                # Filter hanya file (bukan subdirektori)
                file_list = [f for f in files_in_dir if os.path.isfile(os.path.join(thedir, f))]
                
                if not file_list:
                    return self.response(200, 'OK', 'Direktori kosong atau tidak ada file.'.encode('utf-8'), {'Content-type': 'text/plain'})

                # Format respons: daftar file dipisahkan oleh newline
                response_body = '\n'.join(file_list)
                return self.response(200, 'OK', response_body.encode('utf-8'), {'Content-type': 'text/plain'})
            except Exception as e:
                return self.response(500, 'Internal Server Error', f'Error listing files: {e}'.encode('utf-8'), {'Content-type': 'text/plain'})

        # Menangani perintah UPLOAD
        elif command_string.upper().startswith('UPLOAD '):
            # Pisahkan menjadi UPLOAD, nama_file, dan base64_content
            parts = command_string.split(' ', 2) 
            if len(parts) < 3:
                return self.response(400, 'Bad Request', 'UPLOAD command format: UPLOAD [filename] [base64_content]'.encode('utf-8'), {'Content-type': 'text/plain'})
            
            filename = parts[1].strip()
            base64_content = parts[2].strip()

            # Validasi dasar nama file untuk keamanan (mencegah path traversal)
            if '/' in filename or '\\' in filename or '..' in filename:
                return self.response(400, 'Bad Request', 'Invalid filename.'.encode('utf-8'), {'Content-type': 'text/plain'})
            
            full_path = os.path.join(thedir, filename)

            try:
                # Dekode konten Base64
                decoded_content = base64.b64decode(base64_content)
                with open(full_path, 'wb') as f: # Tulis file dalam mode binary write
                    f.write(decoded_content)
                return self.response(200, 'OK', 'UPLOAD success'.encode('utf-8'), {'Content-type': 'text/plain'})
            except base64.binascii.Error:
                return self.response(400, 'Bad Request', 'Invalid Base64 content.'.encode('utf-8'), {'Content-type': 'text/plain'})
            except Exception as e:
                return self.response(500, 'Internal Server Error', f'UPLOAD FAILED: {e}'.encode('utf-8'), {'Content-type': 'text/plain'})

        # Menangani perintah DELETE
        elif command_string.upper().startswith('DELETE '):
            # Pisahkan menjadi DELETE dan nama_file
            parts = command_string.split(' ', 1) 
            if len(parts) < 2:
                return self.response(400, 'Bad Request', 'DELETE command format: DELETE [filename]'.encode('utf-8'), {'Content-type': 'text/plain'})
            
            filename = parts[1].strip()

            # Validasi dasar nama file untuk keamanan
            if '/' in filename or '\\' in filename or '..' in filename:
                return self.response(400, 'Bad Request', 'Invalid filename.'.encode('utf-8'), {'Content-type': 'text/plain'})

            full_path = os.path.join(thedir, filename)

            # Cek apakah file ada
            if not os.path.exists(full_path):
                return self.response(200, 'OK', 'DELETE FAILED, FILE NOT FOUND'.encode('utf-8'), {'Content-type': 'text/plain'})
            
            # Pastikan itu adalah file, bukan direktori, untuk menghindari penghapusan direktori secara tidak sengaja
            if not os.path.isfile(full_path): 
                return self.response(400, 'Bad Request', f'{filename} is not a regular file and cannot be deleted.'.encode('utf-8'), {'Content-type': 'text/plain'})

            try:
                os.remove(full_path) # Hapus file
                return self.response(200, 'OK', 'DELETE SUCCESS'.encode('utf-8'), {'Content-type': 'text/plain'})
            except OSError as e:
                # Menangani error seperti izin ditolak
                return self.response(500, 'Internal Server Error', f'DELETE FAILED: Permission denied or other OS error: {e}'.encode('utf-8'), {'Content-type': 'text/plain'})
            except Exception as e:
                # Menangani error lain yang tidak terduga
                return self.response(500, 'Internal Server Error', f'DELETE FAILED: An unexpected error occurred: {e}'.encode('utf-8'), {'Content-type': 'text/plain'})
        
        else:
            # Jika perintah kustom tidak dikenali
            return self.response(400, 'Bad Request', 'Unknown custom command.'.encode('utf-8'), {'Content-type': 'text/plain'})

# --- Test cases di __main__ (gunakan ini untuk menguji http.py secara mandiri) ---
if __name__=="__main__":
    httpserver = HttpServer()

    print("--- Test Custom Command: LIST ---")
    list_request = b'POST /command HTTP/1.1\r\nHost: localhost\r\nContent-Length: 4\r\nContent-Type: text/plain\r\n\r\nLIST'
    d = httpserver.proses(list_request)
    print(d.decode('latin-1'))

    print("\n--- Test Custom Command: UPLOAD ---")
    test_content = b'Ini adalah isi file yang diunggah melalui command UPLOAD.'
    encoded_content = base64.b64encode(test_content).decode('ascii')
    upload_command_body = f"UPLOAD test_file_upload.txt {encoded_content}"
    upload_request_headers = f"POST /command HTTP/1.1\r\nHost: localhost\r\nContent-Length: {len(upload_command_body)}\r\nContent-Type: text/plain\r\n\r\n"
    upload_request = upload_request_headers.encode('utf-8') + upload_command_body.encode('utf-8')
    d = httpserver.proses(upload_request)
    print(d.decode('latin-1'))

    print("\n--- Test Custom Command: DELETE ---")
    delete_command_body = "DELETE test_file_upload.txt"
    delete_request_headers = f"POST /command HTTP/1.1\r\nHost: localhost\r\nContent-Length: {len(delete_command_body)}\r\nContent-Type: text/plain\r\n\r\n"
    delete_request = delete_request_headers.encode('utf-8') + delete_command_body.encode('utf-8')
    d = httpserver.proses(delete_request)
    print(d.decode('latin-1'))
