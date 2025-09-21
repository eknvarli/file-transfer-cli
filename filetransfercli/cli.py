import argparse
import socket
import os
from tqdm import tqdm

BUFFER_SIZE = 4096
UPLOAD_FOLDER = 'uploads'

def get_all_files(path):
    files = []
    if os.path.isfile(path):
        files.append(path)
    else:
        for root, dirs, filenames in os.walk(path):
            for f in filenames:
                files.append(os.path.join(root, f))
    return files

def run_server(port):
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('0.0.0.0', port))
    server.listen(5)
    print(f'[SERVER] Listening on 0.0.0.0:{port}...')

    while True:
        conn, addr = server.accept()
        print(f'[CONNECTED] {addr} connected')
        try:
            command = conn.recv(BUFFER_SIZE).decode()
            if command.startswith('UPLOAD'):
                filename = command.split()[1]
                filesize = int(conn.recv(BUFFER_SIZE).decode())
                conn.send(b'READY')
                filepath = os.path.join(UPLOAD_FOLDER, filename)
                received = 0
                with open(filepath, 'wb') as f:
                    while received < filesize:
                        data = conn.recv(BUFFER_SIZE)
                        if not data:
                            break
                        f.write(data)
                        received += len(data)
                print(f'[UPLOAD] {filename} uploaded')
                conn.send(b'UPLOAD_DONE')
            elif command.startswith('DOWNLOAD'):
                filename = command.split()[1]
                filepath = os.path.join(UPLOAD_FOLDER, filename)
                if not os.path.exists(filepath):
                    conn.send(b'FILE_NOT_FOUND')
                else:
                    filesize = os.path.getsize(filepath)
                    conn.send(str(filesize).encode())
                    conn.recv(BUFFER_SIZE)  # ACK
                    with open(filepath, 'rb') as f:
                        while True:
                            data = f.read(BUFFER_SIZE)
                            if not data:
                                break
                            conn.send(data)
                    print(f'[DOWNLOAD] {filename} sent')
        except Exception as e:
            print(f'[ERROR] {e}')
        finally:
            conn.close()

def upload_file(server_ip, port, file_path):
    files_to_send = get_all_files(file_path)
    for file in files_to_send:
        filename = os.path.basename(file)
        filesize = os.path.getsize(file)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((server_ip, port))
        s.send(f'UPLOAD {filename}'.encode())
        s.send(str(filesize).encode())
        s.recv(BUFFER_SIZE)
        with open(file, 'rb') as f, tqdm(total=filesize, unit='B', unit_scale=True, desc=f'Uploading: {filename}') as pbar:
            while True:
                data = f.read(BUFFER_SIZE)
                if not data:
                    break
                s.send(data)
                pbar.update(len(data))
        s.recv(BUFFER_SIZE)
        print(f'[UPLOAD] {filename} uploaded')
        s.close()

def download_file(server_ip, port, filename, save_path):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((server_ip, port))
    s.send(f'DOWNLOAD {filename}'.encode())
    data = s.recv(BUFFER_SIZE)
    if data == b'FILE_NOT_FOUND':
        print('[ERROR] File not found')
        s.close()
        return
    filesize = int(data.decode())
    s.send(b'ACK')
    with open(save_path, 'wb') as f, tqdm(total=filesize, unit='B', unit_scale=True, desc=f'Downloading: {filename}') as pbar:
        received = 0
        while received < filesize:
            chunk = s.recv(BUFFER_SIZE)
            if not chunk:
                break
            f.write(chunk)
            received += len(chunk)
            pbar.update(len(chunk))
    print(f'[DOWNLOAD] {filename} downloaded -> {save_path}')
    s.close()

def main():
    parser = argparse.ArgumentParser(description='CLI File Transfer Tool')
    subparsers = parser.add_subparsers(dest='command')

    server_parser = subparsers.add_parser('server', help='Start server')
    server_parser.add_argument('--port', type=int, default=5001, help='Server port (default: 5001)')

    upload_parser = subparsers.add_parser('upload', help='Upload file or folder')
    upload_parser.add_argument('--server', required=True, help='Server IP')
    upload_parser.add_argument('--port', type=int, default=5001, help='Server port')
    upload_parser.add_argument('path', help='Path to file or folder')

    download_parser = subparsers.add_parser('download', help='Download file from server')
    download_parser.add_argument('--server', required=True, help='Server IP')
    download_parser.add_argument('--port', type=int, default=5001, help='Server port')
    download_parser.add_argument('filename', help='Filename on server')
    download_parser.add_argument('save', help='Local path to save file')

    args = parser.parse_args()

    if args.command == 'server':
        run_server(args.port)
    elif args.command == 'upload':
        upload_file(args.server, args.port, args.path)
    elif args.command == 'download':
        download_file(args.server, args.port, args.filename, args.save)
    else:
        parser.print_help()

if __name__ == '__main__':
    main()
