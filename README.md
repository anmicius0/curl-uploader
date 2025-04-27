# Curl Upload Service

A simple Flask-based file upload service that allows users to upload files using curl and receive temporary download links.

## Features

- Upload files using curl
- Automatic file deletion after **3 minutes**
- Secure filename handling
- Background cleanup process
- Health check endpoint

## Installation

1. Clone this repository:

   ```
   git clone <repository-url>
   cd curl-upload
   ```

2. Create a virtual environment and install dependencies:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

## Usage

### Start the server

```
python app.py
```

The server will run on `anmicius.cfd:443` by default.

### Upload a file

Use curl to upload a file:

```
curl -F 'file=@/path/to/your/file' http://anmicius.cfd/upload
```

Example response:

```json
{
  "download_link": "http://anmicius.cfd:443/download/3f2d8a7e-5c1b-4b3e-8f9a-1d2e3f4a5b6c/example.txt",
  "expires_in": "3 minutes",
  "message": "File uploaded successfully"
}
```

### Download a file

Use the provided download link from the upload response:

```
curl -O -J "http://anmicius.cfd:443/download/3f2d8a7e-5c1b-4b3e-8f9a-1d2e3f4a5b6c/example.txt"
```

Or open the link in a browser.

### Health check

To check if the service is alive:

```
curl http://anmicius.cfd/health
```

Expected response:

```json
{ "status": "ok" }
```

## Configuration

You can modify the following settings in `app.py`:

- `HOST`: The hostname or IP address of the server (default: `anmicius.cfd`)
- `PORT`: The port number to listen on (default: `443`)
- `FILE_RETENTION_MINUTES`: How long to keep uploaded files (default: `3` minutes)
- `UPLOAD_FOLDER`: Where to store uploaded files (default: `./uploads` directory)

## Notes

- Files are automatically deleted after 3 minutes
- The service uses a background thread to clean up expired files
- All uploads are stored in the `uploads` directory
- Maximum upload size is 1GB
- Use HTTP for file transfer (no SSL by default)
