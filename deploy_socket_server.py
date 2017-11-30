import socket
import subprocess


HOST = '0.0.0.0'
PORT = 54321


def run_command(command):
    print(command)
    p = subprocess.Popen(command,
                         shell=True, stdin=subprocess.PIPE,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)
    p.wait()
    return True


while True:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen(1)
        conn, addr = s.accept()
        with conn:
            print('Connected by', addr)
            while True:
                data = conn.recv(1024)
                if not data:
                    break
                run_command('{}'.format(data.decode()))
