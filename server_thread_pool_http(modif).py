from socket import *
import socket
import time
import sys
import logging
import multiprocessing
from concurrent.futures import ThreadPoolExecutor
from http import HttpServer

httpserver = HttpServer()

# Pastikan logging diaktifkan untuk WARNING atau INFO
logging.basicConfig(level=logging.WARNING, format='%(asctime)s - %(levelname)s - %(message)s')

def ProcessTheClient(connection,address):
    logging.warning(f"Handler for client {address} started.")
    rcv_bytes = b"" # Gunakan bytes untuk menerima data
    try:
        # Baca data secara bertahap
        while True:
            data = connection.recv(2048) # Baca 2KB sekaligus
            if data:
                rcv_bytes += data
                # Cek apakah header HTTP sudah selesai
                if b"\r\n\r\n" in rcv_bytes:
                    # Di sini kita sudah punya header dan mungkin sebagian body
                    # Lanjutkan ke proses HTTP server
                    logging.warning(f"Received full headers from {address}. Data length: {len(rcv_bytes)}")
                    break # Keluar dari loop recv setelah header lengkap
            else:
                logging.warning(f"Client {address} disconnected during receive (no more data).")
                break # Client menutup koneksi

        if not rcv_bytes: # Jika tidak ada data diterima sama sekali
            logging.warning(f"No data received from client {address}.")
            connection.close()
            return

        # Proses request menggunakan HttpServer
        hasil_response_bytes = httpserver.proses(rcv_bytes)

        logging.warning(f"Sending response to client {address}. Response length: {len(hasil_response_bytes)}")
        connection.sendall(hasil_response_bytes)

    except OSError as e:
        logging.error(f"Socket error with client {address}: {e}")
    except Exception as e:
        logging.error(f"Error processing client {address}: {e}", exc_info=True) # exc_info=True akan menampilkan traceback
    finally:
        logging.warning(f"Closing connection for client {address}.")
        connection.close()
    return

def Server():
    the_clients = []
    my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    my_socket.bind(('0.0.0.0', 8885)) # Port 8885 untuk thread pool
    my_socket.listen(1)
    logging.warning("Server listening on 0.0.0.0:8885")

    with ThreadPoolExecutor(20) as executor:
        while True:
            try:
                connection, client_address = my_socket.accept()
                logging.warning(f"Accepted connection from {client_address}")
                p = executor.submit(ProcessTheClient, connection, client_address)
                the_clients.append(p)
                # menampilkan jumlah process yang sedang aktif (sekarang future/thread)
                jumlah = ['x' for i in the_clients if i.running() or i.done() and i.exception() is None]
                logging.info(f"Active clients/futures: {len(jumlah)}")
            except KeyboardInterrupt:
                logging.warning("Server interrupted by user. Shutting down.")
                break # Keluar dari loop jika Ctrl+C ditekan
            except Exception as e:
                logging.error(f"Error accepting connection: {e}", exc_info=True)


def main():
    Server()

if __name__=="__main__":
    main()
