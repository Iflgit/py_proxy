import socket
import ssl
import threading
import sys
import logging
import subprocess
import os


logging.basicConfig(filename="proxy.log", level=logging.DEBUG, format="%(asctime)s - %(message)s")


def proxy_thread(client, data):
    req = b''

    logging.info("waiting data...")
    client.settimeout(0.1)
    while data:
        req += data
        try:
            data = client.recv(1024)
        except socket.error:
            break

    logging.info(req)

    server_socket = ssl.wrap_socket(socket.socket())
    server_socket.connect(('192.168.83.51', 443))

    logging.info("sending request to server")
    server_socket.send(req)

    logging.info("receiving server answer")
    resp = b''
    server_socket.settimeout(1)
    data = server_socket.recv(1024)
    while data:
        resp += data
        try:
            data = server_socket.recv(1024)
        except socket.error:
            break

    logging.info(resp)

    logging.info("sending answer to client")
    client.send(resp)


def main_thread():
    logging.info("main thread start")

    sock = ssl.wrap_socket(socket.socket(), 'key.pem', 'cert.pem', True)
    sock.bind(('localhost', 9999))
    sock.listen(10)

    while True:
        logging.info("waiting incoming connections...")
        conn, addr = sock.accept()

        data = conn.recv(4)
        if data == b'STOP':
            break

        logging.info("request received")
        t = threading.Thread(target=proxy_thread, args=(conn, data))
        t.run()
    logging.info("stop")


def start():
    logging.info("runing")
    subprocess.Popen("python proxy.py daemon", creationflags=0x08000000, close_fds=True)


def stop():
    logging.info("stoping")

    me = ssl.wrap_socket(socket.socket())
    me.connect(('localhost', 9999))
    me.send(b'STOP')
    me.close()


def run():
    if sys.argv[1] == "start":
        start()
    elif sys.argv[1] == "stop":
        stop()
    elif sys.argv[1] == "daemon":
        main_thread()
    else:
        print("unknown command ", sys.argv[1])

main_thread()
if len(sys.argv) > 1:
    run()
else:
    print("start - run, stop - break")

