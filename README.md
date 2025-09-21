# FileTransferCLI

A simple CLI-based file transfer tool for server-client file upload and download over TCP. Users can easily start a server, upload files or folders, and download files directly from the command line.

## Features
- Upload single files or entire folders
- Download files from the server
- Progress bars during transfers
- No web server required, works with TCP sockets
- Single CLI application for both server and client

## Installation

### Install via pip (from GitHub)
```bash
pip install git+https://github.com/username/filetransfercli.git
```

### Or install locally from source
```bash
git clone https://github.com/username/filetransfercli.git
cd filetransfercli
pip install .
```

## Usage

### Start Server
```bash
filetransfercli server --port 5001
```
- `--port`: Optional, default is 5001

### Upload File or Folder
```bash
filetransfercli upload --server SERVER_IP --port 5001 PATH_TO_FILE_OR_FOLDER
```
- `--server`: IP address of the server
- `--port`: Optional, default is 5001
- `PATH_TO_FILE_OR_FOLDER`: Local path to the file or folder you want to upload

### Download File
```bash
filetransfercli download --server SERVER_IP --port 5001 FILENAME SAVE_PATH
```
- `--server`: IP address of the server
- `--port`: Optional, default is 5001
- `FILENAME`: Name of the file on the server
- `SAVE_PATH`: Local path to save the downloaded file

## Example

Start the server on port 5001:
```bash
filetransfercli server --port 5001
```

Upload a folder:
```bash
filetransfercli upload --server 192.168.1.10 my_folder/
```

Download a file:
```bash
filetransfercli download --server 192.168.1.10 server_file.txt downloaded_file.txt
```

## Requirements
- Python 3.8+
- tqdm (for progress bars)

## License
MIT License