import sys
import os.path
import uuid
from glob import glob
from datetime import datetime
import os # Tambahkan import os untuk os.listdir dan os.remove

class HttpServer:
    def __init__(self):
        self.sessions={}
        self.types={}
        self.types['.pdf']='application/pdf'
        self.types['.jpg']='image/jpeg'
        self.types['.txt']='text/plain'
        self.types['.html']='text/html'
        # Tambahkan tipe file lain jika diperlukan
        self.types['.png']='image/png'
        self.types['.gif']='image/gif'
        self.types['.json']='application/json'

    def response(self,kode=404,message='Not Found',messagebody=bytes(),headers={}):
        tanggal = datetime.now().strftime('%c')
        resp=[]
        resp.append("HTTP/1.0 {} {}\r\n" . format(kode,message))
        resp.append("Date: {}\r\n" . format(tanggal))
        resp.append("Connection: close\r\n")
        resp.append("Server: myserver/1.0\r\n")
        resp.append("Content-Length: {}\r\n" . format(len(messagebody)))
        for kk in headers:
            resp.append("{}: {}\r\n" . format(kk,headers[kk])) # Perbaiki spasi setelah colon
        resp.append("\r\n")

        response_headers=''
        for i in resp:
            response_headers="{}{}" . format(response_headers,i)
        
        if (type(messagebody) is not bytes):
            messagebody = messagebody.encode()

        response = response_headers.encode() + messagebody
        return response

    def proses(self,data):
        requests = data.split("\r\n")
        baris = requests[0]
        all_headers = [n for n in requests[1:] if n!='']
        
        # Pisahkan body dari header untuk POST request
        # Temukan baris kosong pertama untuk memisahkan header dan body
        header_end_index = -1
        for i, line in enumerate(requests):
            if line.strip() == '':
                header_end_index = i
                break
        
        body = b''
        if header_end_index != -1 and header_end_index + 1 < len(requests):
            # Gabungkan kembali baris-baris body dan decode sebagai latin-1
            # Karena data dari socket.recv adalah bytes, kita harus membaca body juga sebagai bytes
            # Asumsikan data masuk sebagai bytes, jadi kita harus memproses `data` secara langsung
            # dan mencari '\r\n\r\n' untuk memisahkan header dan body
            try:
                raw_headers_end = data.find(b'\r\n\r\n')
                if raw_headers_end != -1:
                    body = data[raw_headers_end + 4:]
            except AttributeError: # Jika 'data' bukan bytes, mungkin ini dari test case di __main__
                 pass # Biarkan body kosong atau tangani sesuai kebutuhan

        j = baris.split(" ")
        try:
            method=j[0].upper().strip()
            object_address = j[1].strip()

            if (method=='GET'):
                return self.http_get(object_address, all_headers)
            elif (method=='POST'):
                return self.http_post(object_address, all_headers, body) # Kirim body ke http_post
            elif (method=='DELETE'): # Tambahkan penanganan method DELETE
                return self.http_delete(object_address, all_headers)
            else:
                return self.response(400,'Bad Request','',{})
        except IndexError:
            return self.response(400,'Bad Request','',{})
            
    def http_get(self,object_address,headers):
        thedir='./'
        
        # --- Fungsionalitas LIST ---
        if (object_address == '/list_files'):
            try:
                files_in_dir = os.listdir(thedir) # List semua item di direktori server
                html_list = "<h1>Daftar File di Server</h1><ul>"
                for item in files_in_dir:
                    # Anda bisa menambahkan logika untuk membedakan file dan direktori
                    if os.path.isfile(os.path.join(thedir, item)):
                        html_list += f"<li><a href='/{item}'>{item}</a> (File)</li>"
                    elif os.path.isdir(os.path.join(thedir, item)):
                        html_list += f"<li>{item}/ (Direktori)</li>" # Atau tambahkan link untuk navigasi direktori
                html_list += "</ul>"
                return self.response(200, 'OK', html_list, {'Content-type': 'text/html'})
            except Exception as e:
                return self.response(500, 'Internal Server Error', f'Error listing files: {e}', {'Content-type': 'text/plain'})


        # --- Fungsionalitas GET File Statis (Existing Logic) ---
        if (object_address == '/'):
            # Anda mungkin ingin mengubah ini menjadi redirect ke /list_files atau index.html
            # Untuk sekarang, biarkan seperti ini atau arahkan ke page.html
            try:
                with open('page.html', 'rb') as fp:
                    isi = fp.read()
                return self.response(200,'OK', isi, {'Content-type': 'text/html'})
            except FileNotFoundError:
                 return self.response(200,'OK','Ini Adalah web Server percobaan',dict())

        if (object_address == '/video'):
            return self.response(302,'Found','',dict(location='https://youtu.be/katoxpnTf04'))
        if (object_address == '/santai'):
            return self.response(200,'OK','santai saja',dict())

        # Untuk request file statis lainnya
        object_address_path = object_address[1:] # Hapus '/' di awal
        full_path = os.path.join(thedir, object_address_path)

        if not os.path.exists(full_path) or not os.path.isfile(full_path): # Pastikan itu file
            return self.response(404,'Not Found','',{})
        
        try:
            fp = open(full_path,'rb') 
            isi = fp.read()
            fp.close()
            
            fext = os.path.splitext(full_path)[1]
            content_type = self.types.get(fext, 'application/octet-stream') # Default jika tipe tidak ditemukan
            
            headers={}
            headers['Content-type']=content_type
            
            return self.response(200,'OK',isi,headers)
        except Exception as e:
            return self.response(500, 'Internal Server Error', f'Error reading file: {e}', {'Content-type': 'text/plain'})

    def http_post(self,object_address,headers,body):
        # --- Fungsionalitas UPLOAD ---
        if (object_address == '/upload'):
            try:
                # Ini adalah bagian yang paling tricky karena parsing multipart/form-data cukup kompleks.
                # Untuk penyederhanaan awal, kita akan mengasumsikan body berisi data file langsung
                # atau Anda akan perlu mencari library parsing multipart.
                # Namun, jika client mengirimkan data file saja (misal, dengan Content-Type: application/octet-stream)
                # tanpa form-data, ini akan lebih mudah.
                
                # Mendapatkan Content-Disposition untuk nama file (jika ada)
                # Atau Anda bisa mendapatkan nama file dari query parameter: /upload?filename=my_file.txt
                # Atau dari header kustom X-Filename
                filename_from_headers = "uploaded_file_" + str(uuid.uuid4()) # Default random filename

                for h in headers:
                    if h.lower().startswith('content-disposition'):
                        # Contoh: Content-Disposition: form-data; name="file"; filename="nama_asli.txt"
                        parts = h.split(';')
                        for part in parts:
                            if 'filename=' in part:
                                filename_from_headers = part.split('filename=')[1].strip('\"')
                                break
                    # Anda juga bisa mengecek header kustom seperti X-Filename
                    # if h.lower().startswith('x-filename'):
                    #     filename_from_headers = h.split(':')[1].strip()

                upload_path = os.path.join('./', filename_from_headers) # Simpan di direktori server

                # Asumsi body berisi data file mentah.
                # Jika client mengirim multipart/form-data, Anda perlu parser yang lebih kompleks.
                # Untuk demo sederhana, kita asumsikan client mengirim body sebagai file mentah.
                with open(upload_path, 'wb') as f: # wb = write binary
                    f.write(body)
                
                return self.response(200,'OK',f'File {filename_from_headers} uploaded successfully!', {'Content-type': 'text/plain'})
            except Exception as e:
                return self.response(500,'Internal Server Error',f'Error uploading file: {e}', {'Content-type': 'text/plain'})
        
        # Logika POST lainnya (jika ada)
        headers ={}
        isi = "kosong"
        return self.response(200,'OK',isi,headers)
        
    # --- Fungsionalitas DELETE ---
    def http_delete(self, object_address, headers):
        # object_address akan berbentuk '/nama_file_yang_akan_dihapus.txt'
        file_to_delete = object_address[1:] # Hapus '/' di awal path
        full_path = os.path.join('./', file_to_delete)

        if not os.path.exists(full_path):
            return self.response(404, 'Not Found', f'File {file_to_delete} not found.', {'Content-type': 'text/plain'})
        
        if not os.path.isfile(full_path): # Pastikan itu adalah file, bukan direktori atau link simbolik
            return self.response(400, 'Bad Request', f'{file_to_delete} is not a regular file.', {'Content-type': 'text/plain'})

        try:
            os.remove(full_path)
            return self.response(200, 'OK', f'File {file_to_delete} deleted successfully.', {'Content-type': 'text/plain'})
        except OSError as e:
            # Misalnya, izin ditolak
            return self.response(403, 'Forbidden', f'Error deleting file {file_to_delete}: {e}', {'Content-type': 'text/plain'})
        except Exception as e:
            return self.response(500, 'Internal Server Error', f'An unexpected error occurred: {e}', {'Content-type': 'text/plain'})
            
#>>> import os.path
#>>> ext = os.path.splitext('/ak/52.png')

if __name__=="__main__":
    httpserver = HttpServer()
    print("--- Test GET / ---")
    d = httpserver.proses(b'GET / HTTP/1.0\r\nHost: localhost\r\n\r\n')
    print(d.decode('latin-1')[:200]) # Decode sebagian untuk melihat header

    print("\n--- Test GET /list_files ---")
    d = httpserver.proses(b'GET /list_files HTTP/1.0\r\nHost: localhost\r\n\r\n')
    print(d.decode('latin-1')[:500]) # Decode sebagian untuk melihat header

    print("\n--- Test GET testing.txt (Pastikan ada file testing.txt di folder ini) ---")
    d = httpserver.proses(b'GET testing.txt HTTP/1.0\r\nHost: localhost\r\n\r\n')
    print(d.decode('latin-1')[:200]) # Decode sebagian untuk melihat header

    print("\n--- Test DELETE (Buat file dummy_delete.txt dulu secara manual) ---")
    # Buat file dummy_delete.txt secara manual di folder yang sama untuk pengujian ini
    with open('dummy_delete.txt', 'w') as f:
        f.write('Ini akan dihapus.')
    d = httpserver.proses(b'DELETE /dummy_delete.txt HTTP/1.0\r\nHost: localhost\r\n\r\n')
    print(d.decode('latin-1'))

    print("\n--- Test UPLOAD (Simulasi POST dengan body sederhana, belum support multipart) ---")
    # Ini hanya simulasi dasar, bukan parsing multipart/form-data lengkap
    # Nama file di sini diambil dari header 'Content-Disposition' atau default
    upload_body = b'This is the content of the uploaded file.'
    upload_request = b'POST /upload HTTP/1.0\r\n' \
                     b'Host: localhost\r\n' \
                     b'Content-Length: ' + str(len(upload_body)).encode() + b'\r\n' \
                     b'Content-Type: application/octet-stream\r\n' \
                     b'Content-Disposition: attachment; filename="uploaded_test.txt"\r\n' \
                     b'\r\n' + upload_body
    d = httpserver.proses(upload_request)
    print(d.decode('latin-1'))
    # Cek apakah uploaded_test.txt terbuat di folder
