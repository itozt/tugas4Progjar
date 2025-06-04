import sys
import socket
import logging
import os
import base64
import re

# --- Konfigurasi Server Tujuan ---
SERVER_IP = '172.16.16.101'
# SESUAIKAN PORT SESUAI SERVER YANG ANDA JALANKAN DI MESIN 1
# 8885 untuk server_thread_pool_http.py
# 8889 untuk server_process_pool_http.py
SERVER_PORT = 8885 # PASTIKAN PORT INI SESUAI DENGAN SERVER YANG SEDANG AKTIF DI MESIN 1

server_address = (SERVER_IP, SERVER_PORT)

# --- Konfigurasi Logging ---
# Mengubah level ke ERROR akan menyembunyikan pesan WARNING dari library logging
# Anda tetap akan melihat pesan ERROR dan CRITICAL jika ada masalah serius
logging.basicConfig(level=logging.ERROR, format='%(levelname)s:%(message)s')

# --- Fungsi Dasar Socket ---
def make_socket(destination_address, port):
    """Membuat dan mengembalikan objek socket TCP yang terhubung ke server."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_addr = (destination_address, port)
        # logging.warning(f"Connecting to {server_addr}") # Pesan ini sekarang tersembunyi
        sock.connect(server_addr)
        return sock
    except Exception as ee:
        logging.error(f"Error making socket: {str(ee)}") # Pesan error ini tetap akan muncul
        return None

# --- Fungsi Pengiriman Perintah HTTP ---
def send_command(command_data_bytes):
    """
    Mengirimkan data perintah HTTP (dalam bentuk bytes) ke server
    dan mengembalikan respons dari server.
    """
    alamat_server = server_address[0]
    port_server = server_address[1]
    
    sock = make_socket(alamat_server, port_server)

    if sock is None:
        # logging.error("Failed to create socket. Check server address/port or firewall.") # Pesan ini sekarang dikelola di make_socket
        return False

    try:
        # logging.warning(f"Sending message (length: {len(command_data_bytes)} bytes)") # Pesan ini sekarang tersembunyi
        sock.sendall(command_data_bytes)
        
        data_received = b""
        # Set timeout agar recv tidak macet selamanya
        sock.settimeout(10.0) # Timeout 10 detik

        # Fase 1: Baca header sampai ketemu '\r\n\r\n'
        header_end = -1
        while header_end == -1:
            chunk = sock.recv(4096)
            if not chunk: # Server menutup koneksi terlalu dini
                logging.error("Server closed connection prematurely during header receive.")
                return False
            data_received += chunk
            header_end = data_received.find(b'\r\n\r\n')

        # Setelah header diterima, ekstrak Content-Length
        headers_part = data_received[:header_end].decode('latin-1')
        content_length_match = re.search(r'Content-Length:\s*(\d+)', headers_part, re.IGNORECASE)
        
        body_start_index = header_end + 4 # Posisi awal body setelah \r\n\r\n
        
        # Fase 2: Baca body berdasarkan Content-Length jika ada
        if content_length_match:
            expected_body_length = int(content_length_match.group(1))
            current_body_length = len(data_received) - body_start_index
            
            # Lanjutkan membaca hingga seluruh body yang diharapkan diterima
            while current_body_length < expected_body_length:
                bytes_to_read = expected_body_length - current_body_length
                chunk = sock.recv(min(4096, bytes_to_read))
                if not chunk: # Server menutup koneksi sebelum mengirim body penuh
                    logging.error("Server closed connection before full body received.")
                    break 
                data_received += chunk
                current_body_length += len(chunk)
            
            # logging.warning(f"Received expected body length ({expected_body_length} bytes).") # Pesan ini sekarang tersembunyi
        else:
            # Fallback jika tidak ada Content-Length (misal, untuk respons tanpa body)
            # logging.warning("No Content-Length header. Reading until server closes connection.") # Pesan ini sekarang tersembunyi
            while True:
                chunk = sock.recv(4096)
                if not chunk: # Server menutup koneksi
                    break
                data_received += chunk

        # logging.warning(f"Finished receiving data. Total bytes: {len(data_received)}") # Pesan ini sekarang tersembunyi

        if not data_received:
            logging.error("No data received from server.")
            return False

        hasil = data_received.decode('latin-1') 
        # logging.warning("Data received from server.") # Pesan ini sekarang tersembunyi
        return hasil
    except socket.timeout:
        logging.error("Socket receive timed out. Server might not be responding or sending full data.")
        return False
    except Exception as ee:
        logging.error(f"Critical error in send_command: {str(ee)}", exc_info=True)
        return False
    finally:
        if sock:
            sock.close()
            # logging.warning("Socket closed.") # Pesan ini sekarang tersembunyi

# --- Fungsi Pembantu untuk Membangun Request POST /command ---
def build_custom_command_request(command_body_str):
    """
    Membangun seluruh HTTP POST request yang valid untuk perintah kustom.
    """
    request_line = f"POST /command HTTP/1.1"
    headers = (
        f"Host: {server_address[0]}:{server_address[1]}\r\n"
        f"Content-Length: {len(command_body_str.encode('utf-8'))}\r\n"
        f"Content-Type: text/plain"
    )
    full_request_str = f"{request_line}\r\n{headers}\r\n\r\n{command_body_str}"
    return full_request_str.encode('utf-8')

# --- Main Program Client Interaktif ---
if __name__ == '__main__':
    # Untuk debugging lebih detail, Anda bisa ubah level di sini (misal: logging.WARNING)
    # logging.getLogger().setLevel(logging.DEBUG) 

    print(f"\n--- Client Interaktif untuk HTTP Server di {SERVER_IP}:{SERVER_PORT} ---")
    print("Ketik 'LIST' untuk melihat daftar file.")
    print("Ketik 'UPLOAD [nama_file_di_server] [encode_base64_isi_file]' untuk mengunggah file.")
    print("Ketik 'DELETE [nama_file_di_server]' untuk menghapus file.")
    print("Ketik 'EXIT' untuk keluar.")

    while True:
        try:
            user_input = input("Masukkan perintah: ").strip()
            if not user_input:
                continue

            if user_input.upper() == 'EXIT':
                print("Client berhenti.")
                break

            command_type = user_input.split(' ')[0].upper()
            
            response_from_server = None 

            # --- Logika untuk Perintah LIST ---
            if command_type == 'LIST':
                command_body = "LIST"
                request_bytes = build_custom_command_request(command_body)
                response_from_server = send_command(request_bytes)
                
                print("\n--- Client Output (LIST) ---")
                if response_from_server is not False and response_from_server is not None:
                    # Pisahkan header HTTP dari body respons
                    response_parts = response_from_server.split('\r\n\r\n', 1)
                    if len(response_parts) > 1:
                        response_body_only = response_parts[1]
                    else:
                        response_body_only = response_from_server 
                        print("[DEBUG: No \\r\\n\\r\\n found in response. Treating entire response as body.]")
                    
                    print("\n--- Daftar File di Server ---")
                    if response_body_only.strip(): # Cek jika body tidak kosong setelah strip whitespace
                        print(response_body_only)
                    else:
                        print("[Kosong atau hanya whitespace. Mungkin tidak ada file atau respons error dari server.]")
                else:
                    print("Gagal mengambil daftar file. send_command mengembalikan False atau None.")
                print("--- END Client Output (LIST) ---\n")

            # --- Logika untuk Perintah UPLOAD ---
            elif command_type == 'UPLOAD':
                parts = user_input.split(' ', 2)
                if len(parts) < 3:
                    print("Format UPLOAD salah. Gunakan: UPLOAD [nama_file_di_server] [encode_base64_isi_file]")
                    continue
                
                server_filename = parts[1].strip()
                encoded_content = parts[2].strip()

                command_body = f"UPLOAD {server_filename} {encoded_content}"
                request_bytes = build_custom_command_request(command_body)
                response_from_server = send_command(request_bytes)
                
                print("\n--- Client Output (UPLOAD) ---")
                if response_from_server is not False and response_from_server is not None:
                    response_body_only = response_from_server.split('\r\n\r\n', 1)[1] if '\r\n\r\n' in response_from_server else response_from_server
                    print("Respons UPLOAD Server:", response_body_only)
                else:
                    print("Gagal melakukan UPLOAD.")
                print("--- END Client Output (UPLOAD) ---\n")
                
            # --- Logika untuk Perintah DELETE ---
            elif command_type == 'DELETE':
                parts = user_input.split(' ', 1)
                if len(parts) < 2:
                    print("Format DELETE salah. Gunakan: DELETE [nama_file_di_server]")
                    continue
                file_to_delete = parts[1].strip()

                command_body = f"DELETE {file_to_delete}"
                request_bytes = build_custom_command_request(command_body)
                response_from_server = send_command(request_bytes)

                print("\n--- Client Output (DELETE) ---")
                if response_from_server is not False and response_from_server is not None:
                    response_body_only = response_from_server.split('\r\n\r\n', 1)[1] if '\r\n\r\n' in response_from_server else response_from_server
                    print("Respons DELETE Server:", response_body_only)
                else:
                    print("Gagal melakukan DELETE.")
                print("--- END Client Output (DELETE) ---\n")

            else:
                print("Perintah tidak dikenal. Gunakan LIST, UPLOAD [nama_file_di_server] [encode_base64_isi_file], atau DELETE [nama_file_di_server].")

        except EOFError:
            print("\nClient berhenti.")
            break
        except Exception as e:
            print(f"Terjadi kesalahan umum pada client: {e}")
