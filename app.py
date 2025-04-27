from flask import Flask, request, jsonify, send_from_directory
import os, uuid, threading, time
from werkzeug.utils import secure_filename
from werkzeug.exceptions import RequestEntityTooLarge

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "uploads")
HOST, PORT = "anmicius.cfd", 443
FILE_RETENTION_MINUTES, MAX_CONTENT_LENGTH = 3, 1 * 1024**3
CLEANUP_INTERVAL_SECONDS = 60

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = MAX_CONTENT_LENGTH
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
uploaded_files = {}


def delete_file_after_timeout(file_path, file_id):
    time.sleep(FILE_RETENTION_MINUTES * 60)
    if os.path.exists(file_path):
        os.remove(file_path)
    uploaded_files.pop(file_id, None)
    print(f"Deleted expired file: {file_path}")


@app.route("/upload", methods=["POST"])
def upload_file():
    file = request.files.get("file")
    if not file or file.filename == "":
        return jsonify({"error": "No file selected"}), 400
    file_id = str(uuid.uuid4())
    filename = secure_filename(file.filename)
    new_filename = f"{file_id}_{filename}"
    file_path = os.path.join(UPLOAD_FOLDER, new_filename)
    file.save(file_path)
    uploaded_files[file_id] = {
        "path": file_path,
        "original_name": filename,
        "expiry_time": time.time() + FILE_RETENTION_MINUTES * 60,
    }
    threading.Thread(
        target=delete_file_after_timeout, args=(file_path, file_id), daemon=True
    ).start()
    link = f"http://{HOST}:{PORT}/download/{file_id}/{filename}"
    return jsonify(
        {
            "message": "File uploaded successfully",
            "download_link": link,
            "expires_in": f"{FILE_RETENTION_MINUTES} minutes",
        }
    )


@app.route("/download/<file_id>/<filename>")
def download_file(file_id, filename):
    info = uploaded_files.get(file_id)
    if not info:
        return jsonify({"error": "File not found or expired"}), 404
    return send_from_directory(
        os.path.dirname(info["path"]),
        os.path.basename(info["path"]),
        as_attachment=True,
        download_name=info["original_name"],
    )


@app.route("/health")
def health_check():
    return jsonify({"status": "ok"})


@app.errorhandler(RequestEntityTooLarge)
def handle_file_too_large(e):
    return jsonify({"error": "File too large. Maximum upload size is 1GB."}), 413


def cleanup_expired_files():
    while True:
        now = time.time()
        expired = [
            fid for fid, info in uploaded_files.items() if now > info["expiry_time"]
        ]
        for fid in expired:
            if os.path.exists(uploaded_files[fid]["path"]):
                os.remove(uploaded_files[fid]["path"])
            uploaded_files.pop(fid, None)
            print(f"Cleanup: Deleted expired file ID {fid}")
        time.sleep(CLEANUP_INTERVAL_SECONDS)


if __name__ == "__main__":
    threading.Thread(target=cleanup_expired_files, daemon=True).start()
    print(f"Server running at http://{HOST}:{PORT}")
    print(
        f"Upload files using: curl -F 'file=@/path/to/your/file' http://{HOST}:{PORT}/upload"
    )
    app.run(host="0.0.0.0", port=PORT)
