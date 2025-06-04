import sys
import os.path
import uuid
from glob import glob
from datetime import datetime
import os # Tambahkan import os untuk os.listdir dan os.remove
import base64 # Tambahkan import base64 untuk decoding

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
        # Tambahkan tipe file lain jika diperlukan

    def response(self, kode=404, message='Not Found', messagebody=bytes(), headers={}):
        tanggal = datetime.now().strftime('%c')
        resp = []
        resp.append(f"HTTP/1.0 {kode} {message}\r\n")
        resp.append(f"Date: {tanggal}\r\n")
        resp.append("Connection: close\r\n")
        resp.append("Server: myserver/1.0\r\n")
        resp.append(f"Content-Length: {len(messagebody)}\r\n")
        for kk in headers:
            resp.append(f"{kk}: {headers[kk]}\r\n")
        resp.append("\r\n")

        response_headers = ''.join(resp)
        
        if (type(messagebody) is not bytes):
            messagebody = messagebody.encode()

        response_bytes = response_headers.encode() + messagebody
        return response_bytes

    def parse_headers(self, request_lines):
        headers = {}
        for line in request_lines:
            if ':' in line:
                key, value = line.split(':', 1)
                headers[key.strip().lower()] = value.strip()
        return headers

    def proses(self, raw_data_bytes): # Menerima raw bytes dari socket
        # Cari pemisah header dan body
        header_end_index = raw_data_bytes.find(b'\r\n\r\n')
        if header_end_index == -1:
            return self.response(400, 'Bad Request', 'No valid HTTP header end.')

        headers_raw = raw_data_bytes[:header_end_index].decode('latin-1').split("\r\n")
        request_line = headers_raw[0]
        all_headers = self.parse_headers(headers_raw[1:])
        
        body_bytes = raw_data_bytes[header_end_index + 4:] # +4 untuk '\r\n\r\n'

        j = request_line.split(" ")
        try:
            method = j[0].upper().strip()
            object_address = j[1].strip()

            if (method == 'GET'):
                return self.http_get(object_address, all_headers)
            elif (method == 'POST'):
                # Cek jika ini adalah request untuk command kustom
                if object_address == '/command':
                    try:
                        # Body mungkin masih berupa bytes, decode dulu ke string
                        body_string = body_bytes.decode('utf-8') 
                        return self.handle_custom_command(body_string)
                    except UnicodeDecodeError:
                        return self.response(400, 'Bad Request', 'Invalid body encoding for custom command.')
                else:
                    # Ini adalah POST standar, mungkin untuk form submission atau sejenisnya
                    # Saat ini tidak ada implementasi POST standar selain untuk /command
                    # Anda bisa menambahkan logika POST standar di sini jika diperlukan
                    return self.response(400, 'Bad Request', 'POST requests only supported for /command endpoint.')
            else:
                return self.response(400, 'Bad Request', '', {})
        except IndexError:
            return self.response(400, 'Bad Request', '', {})

    def http_get(self, object_address, headers):
        thedir='./'
        
        if (object_address == '/'):
            try:
                with open(os.path.join(thedir, 'page.html'), 'rb') as fp:
                    isi = fp.read()
                return self.response(200,'OK', isi, {'Content-type': 'text/html'})
            except FileNotFoundError:
                 return self.response(200,'OK','Ini Adalah web Server percobaan',dict())

        # Untuk request file statis lainnya
        object_address_path = object_address[1:] # Hapus '/' di awal
        full_path = os.path.join(thedir, object_address_path)

        if not os.path.exists(full_path) or not os.path.isfile(full_path): # Pastikan itu file
            return self.response(404,'Not Found','',{})
        
        try:
            with open(full_path,'rb') as fp: # rb = read binary
                isi = fp.read()
            
            fext = os.path.splitext(full_path)[1]
            content_type = self.types.get(fext, 'application/octet-stream') # Default jika tipe tidak ditemukan
            
            headers={}
            headers['Content-type']=content_type
            
            return self.response(200,'OK',isi,headers)
        except Exception as e:
            return self.response(500, 'Internal Server Error', f'Error reading file: {e}'.encode(), {'Content-type': 'text/plain'})

    # Metode http_post kosong karena semua custom command dihandle oleh handle_custom_command
    # Jika ada POST request standar lainnya, bisa diimplementasikan di sini
    # def http_post(self, object_address, headers, body_bytes):
    #    return self.response(400, 'Bad Request', 'Standard POST not implemented yet.')

    # --- Metode Baru: handle_custom_command ---
    def handle_custom_command(self, command_string):
        command_string = command_string.strip()
        thedir = './' # Direktori kerja server

        if command_string.upper() == 'LIST':
            try:
                files_in_dir = os.listdir(thedir)
                # Filter hanya file, atau Anda bisa tampilkan semua
                file_list = [f for f in files_in_dir if os.path.isfile(os.path.join(thedir, f))]
                
                if not file_list:
                    return self.response(200, 'OK', 'Direktori kosong atau tidak ada file.', {'Content-type': 'text/plain'})

                # Format respons sesuai permintaan: "file1\nfile2\n..."
                response_body = '\n'.join(file_list)
                return self.response(200, 'OK', response_body, {'Content-type': 'text/plain'})
            except Exception as e:
                return self.response(500, 'Internal Server Error', f'Error listing files: {e}'.encode(), {'Content-type': 'text/plain'})

        elif command_string.upper().startswith('UPLOAD '):
            parts = command_string.split(' ', 2) # Pisahkan 'UPLOAD', 'nama file', 'isi base64'
            if len(parts) < 3:
                return self.response(400, 'Bad Request', 'UPLOAD command format: UPLOAD [filename] [base64_content]'.encode(), {'Content-type': 'text/plain'})
            
            filename = parts[1].strip()
            base64_content = parts[2].strip()

            # Pastikan nama file aman (tidak ada path traversal)
            if '/' in filename or '\\' in filename or '..' in filename:
                return self.response(400, 'Bad Request', 'Invalid filename.'.encode(), {'Content-type': 'text/plain'})
            
            full_path = os.path.join(thedir, filename)

            try:
                decoded_content = base64.b64decode(base64_content)
                with open(full_path, 'wb') as f:
                    f.write(decoded_content)
                return self.response(200, 'OK', 'UPLOAD success'.encode(), {'Content-type': 'text/plain'})
            except base64.binascii.Error:
                return self.response(400, 'Bad Request', 'Invalid Base64 content.'.encode(), {'Content-type': 'text/plain'})
            except Exception as e:
                return self.response(500, 'Internal Server Error', f'UPLOAD FAILED: {e}'.encode(), {'Content-type': 'text/plain'})

        elif command_string.upper().startswith('DELETE '):
            parts = command_string.split(' ', 1) # Pisahkan 'DELETE', 'nama file'
            if len(parts) < 2:
                return self.response(400, 'Bad Request', 'DELETE command format: DELETE [filename]'.encode(), {'Content-type': 'text/plain'})
            
            filename = parts[1].strip()

            # Pastikan nama file aman
            if '/' in filename or '\\' in filename or '..' in filename:
                return self.response(400, 'Bad Request', 'Invalid filename.'.encode(), {'Content-type': 'text/plain'})

            full_path = os.path.join(thedir, filename)

            if not os.path.exists(full_path):
                return self.response(200, 'OK', 'DELETE FAILED, FILE NOT FOUND'.encode(), {'Content-type': 'text/plain'})
            
            if not os.path.isfile(full_path): # Pastikan itu adalah file, bukan direktori atau link simbolik
                return self.response(400, 'Bad Request', f'{filename} is not a regular file and cannot be deleted.'.encode(), {'Content-type': 'text/plain'})

            try:
                os.remove(full_path)
                return self.response(200, 'OK', 'DELETE SUCCESS'.encode(), {'Content-type': 'text/plain'})
            except OSError as e:
                return self.response(500, 'Internal Server Error', f'DELETE FAILED: Permission denied or other OS error: {e}'.encode(), {'Content-type': 'text/plain'})
            except Exception as e:
                return self.response(500, 'Internal Server Error', f'DELETE FAILED: An unexpected error occurred: {e}'.encode(), {'Content-type': 'text/plain'})
        
        else:
            return self.response(400, 'Bad Request', 'Unknown custom command.'.encode(), {'Content-type': 'text/plain'})

# --- Test cases di __main__ (Opsional, untuk pengujian cepat tanpa server penuh) ---
if __name__=="__main__":
    httpserver = HttpServer()

    # Simulasi data mentah dari socket (perhatikan b'' untuk bytes)
    print("--- Test GET / (standard HTML) ---")
    d = httpserver.proses(b'GET / HTTP/1.0\r\nHost: localhost\r\n\r\n')
    print(d.decode('latin-1')[:200]) 

    print("\n--- Test Custom Command: LIST ---")
    list_request = b'POST /command HTTP/1.1\r\nHost: localhost\r\nContent-Length: 4\r\nContent-Type: text/plain\r\n\r\nLIST'
    d = httpserver.proses(list_request)
    print(d.decode('latin-1'))

    print("\n--- Test Custom Command: UPLOAD ---")
    test_content = b'Ini adalah isi file yang diunggah melalui command UPLOAD.'
    encoded_content = base64.b64encode(test_content).decode('ascii') # Encode ke base64, lalu decode ke ascii string
    upload_command_body = f"UPLOAD test_file_upload.txt {encoded_content}"
    upload_request_headers = f"POST /command HTTP/1.1\r\nHost: localhost\r\nContent-Length: {len(upload_command_body)}\r\nContent-Type: text/plain\r\n\r\n"
    upload_request = upload_request_headers.encode() + upload_command_body.encode()
    d = httpserver.proses(upload_request)
    print(d.decode('latin-1'))
    # Cek apakah test_file_upload.txt terbuat di folder
    print("\n--- Cek file setelah UPLOAD ---")
    list_after_upload = b'POST /command HTTP/1.1\r\nHost: localhost\r\nContent-Length: 4\r\nContent-Type: text/plain\r\n\r\nLIST'
    d = httpserver.proses(list_after_upload)
    print(d.decode('latin-1'))


    print("\n--- Test Custom Command: DELETE ---")
    delete_command_body = "DELETE test_file_upload.txt"
    delete_request_headers = f"POST /command HTTP/1.1\r\nHost: localhost\r\nContent-Length: {len(delete_command_body)}\r\nContent-Type: text/plain\r\n\r\n"
    delete_request = delete_request_headers.encode() + delete_command_body.encode()
    d = httpserver.proses(delete_request)
    print(d.decode('latin-1'))
    # Cek apakah file sudah terhapus
    print("\n--- Cek file setelah DELETE ---")
    list_after_delete = b'POST /command HTTP/1.1\r\nHost: localhost\r\nContent-Length: 4\r\nContent-Type: text/plain\r\n\r\nLIST'
    d = httpserver.proses(list_after_delete)
    print(d.decode('latin-1'))

    print("\n--- Test Custom Command: DELETE (File Not Found) ---")
    delete_command_body_nf = "DELETE non_existent_file.txt"
    delete_request_headers_nf = f"POST /command HTTP/1.1\r\nHost: localhost\r\nContent-Length: {len(delete_command_body_nf)}\r\nContent-Type: text/plain\r\n\r\n"
    delete_request_nf = delete_request_headers_nf.encode() + delete_command_body_nf.encode()
    d = httpserver.proses(delete_request_nf)
    print(d.decode('latin-1'))
